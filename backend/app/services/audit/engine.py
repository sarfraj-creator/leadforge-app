import re
from typing import Dict, List, Any, Optional
from backend.app.services.crawler.safe_crawler import CrawlResult
from backend.app.services.audit.tech_detector import tech_detector

class AuditResult:
    def __init__(self):
        self.status: str = "AUDIT_INCOMPLETE" # "AUDIT_COMPLETE" | "AUDIT_INCOMPLETE" | "AUDIT_FAILED"
        self.overall_score: int = 0
        self.performance_score: int = 0
        self.mobile_score: int = 0
        self.seo_score: int = 0
        self.accessibility_score: int = 0
        self.security_score: int = 0
        self.ux_score: int = 0
        self.conversion_score: int = 0
        
        self.metrics: List[Dict[str, Any]] = []
        self.issues: List[Dict[str, Any]] = []
        self.technologies: List[Dict[str, Any]] = []
        self.summary: str = ""

class WebsiteIntelligenceEngine:
    def audit(self, crawl: CrawlResult) -> AuditResult:
        result = AuditResult()
        
        # 1. Check reachability & crawl success
        if not crawl.is_reachable or not crawl.raw_html:
            result.status = "AUDIT_INCOMPLETE"
            result.overall_score = 0
            result.performance_score = 0
            result.mobile_score = 0
            result.seo_score = 0
            result.accessibility_score = 0
            result.security_score = 0
            result.ux_score = 0
            result.conversion_score = 0
            
            error_reason = crawl.error or f"HTTP status {crawl.http_status or 'no response'}"
            result.issues.append({
                "category": "technical",
                "title": "Website Unreachable / Audit Incomplete",
                "severity": "critical",
                "evidence": f"Failed to retrieve complete page markup from '{crawl.url}'. Diagnostic error: {error_reason}",
                "recommendation": "Verify domain DNS records, server status, and SSL configuration."
            })
            result.metrics.append({
                "category": "technical",
                "metric_name": "Crawl Status",
                "value": "INCOMPLETE",
                "score": 0
            })
            result.summary = f"Audit could not be completed because the website was unreachable ({error_reason}). No speculative scores were assigned."
            return result

        # Mark Audit as successfully completed
        result.status = "AUDIT_COMPLETE"

        # 1. Performance Audit (0-100)
        perf_score = 100
        load_time = crawl.load_time_ms
        page_size_kb = round(crawl.page_size_bytes / 1024, 1)
        
        result.metrics.append({
            "category": "performance",
            "metric_name": "Response Time",
            "value": f"{load_time}ms",
            "score": max(20, 100 - int(load_time / 30))
        })
        result.metrics.append({
            "category": "performance",
            "metric_name": "Page Weight",
            "value": f"{page_size_kb} KB",
            "score": 100 if page_size_kb < 1200 else (75 if page_size_kb < 3000 else 40)
        })
        
        if load_time > 3000:
            deduction = min(50, 20 + int((load_time - 3000) / 40))
            perf_score -= deduction
            result.issues.append({
                "category": "performance",
                "title": "Slow Response Latency",
                "severity": "high" if load_time > 4000 else "medium",
                "evidence": f"Measured initial response time: {load_time}ms (exceeds 3000ms standard).",
                "recommendation": "Implement server-side page caching, edge CDN delivery, and image optimization."
            })
        elif load_time > 1500:
            perf_score -= 15
            
        if page_size_kb > 3000:
            perf_score -= 20
            result.issues.append({
                "category": "performance",
                "title": "Large Page Weight",
                "severity": "medium",
                "evidence": f"Total document size is {page_size_kb} KB.",
                "recommendation": "Compress asset bundles and serve next-gen image formats (WebP/AVIF)."
            })
        result.performance_score = max(10, min(100, perf_score))

        # 2. Mobile Audit (0-100)
        mobile_score = 100
        has_viewport = bool(crawl.viewport_meta and "width=device-width" in crawl.viewport_meta.lower())
        result.metrics.append({
            "category": "mobile",
            "metric_name": "Viewport Tag",
            "value": crawl.viewport_meta if has_viewport else "Missing",
            "score": 100 if has_viewport else 0
        })
        
        if not has_viewport:
            mobile_score -= 50
            result.issues.append({
                "category": "mobile",
                "title": "Missing Mobile Viewport Configuration",
                "severity": "critical",
                "evidence": "No `<meta name='viewport' content='width=device-width...'>` tag detected in head.",
                "recommendation": "Add a standard viewport meta tag and implement responsive CSS breakpoints."
            })
            
        touch_targets = len(crawl.buttons) + len([l for l in crawl.links if len(l) > 2])
        result.metrics.append({
            "category": "mobile",
            "metric_name": "Interactive Elements",
            "value": f"{touch_targets} interactive elements",
            "score": 100 if touch_targets >= 5 else 60
        })
        if touch_targets < 3:
            mobile_score -= 20
            result.issues.append({
                "category": "mobile",
                "title": "Sparse Touch Targets",
                "severity": "medium",
                "evidence": f"Only {touch_targets} interactive links/buttons identified in document markup.",
                "recommendation": "Enrich mobile layout with accessible navigation controls."
            })
        result.mobile_score = max(10, min(100, mobile_score))

        # 3. SEO Audit (0-100)
        seo_score = 100
        title_len = len(crawl.title) if crawl.title else 0
        meta_desc_len = len(crawl.meta_description) if crawl.meta_description else 0
        h1_count = len(crawl.h1_tags)
        
        result.metrics.append({
            "category": "seo",
            "metric_name": "Title Tag",
            "value": f"{crawl.title} ({title_len} chars)" if crawl.title else "Missing",
            "score": 100 if (30 <= title_len <= 65) else (60 if title_len > 0 else 0)
        })
        result.metrics.append({
            "category": "seo",
            "metric_name": "Meta Description",
            "value": f"{meta_desc_len} chars" if crawl.meta_description else "Missing",
            "score": 100 if (70 <= meta_desc_len <= 160) else (50 if meta_desc_len > 0 else 20)
        })
        result.metrics.append({
            "category": "seo",
            "metric_name": "H1 Heading",
            "value": f"{h1_count} H1 tags detected" if h1_count > 0 else "None",
            "score": 100 if h1_count == 1 else (60 if h1_count > 1 else 30)
        })
        
        if not crawl.title:
            seo_score -= 35
            result.issues.append({
                "category": "seo",
                "title": "Missing Title Tag",
                "severity": "critical",
                "evidence": "HTML document has no `<title>` tag.",
                "recommendation": "Add a distinct, keyword-rich title between 30 and 65 characters."
            })
        elif title_len < 20 or title_len > 70:
            seo_score -= 10
            result.issues.append({
                "category": "seo",
                "title": "Suboptimal Title Tag Length",
                "severity": "low",
                "evidence": f"Title tag has {title_len} characters (ideal: 30-65 chars).",
                "recommendation": "Refine page title to prevent search engine truncation."
            })
            
        if not crawl.meta_description:
            seo_score -= 25
            result.issues.append({
                "category": "seo",
                "title": "Missing Meta Description",
                "severity": "high",
                "evidence": "No `<meta name='description'>` tag found.",
                "recommendation": "Write a compelling 120-160 character description highlighting key offerings."
            })
            
        if h1_count == 0:
            seo_score -= 20
            result.issues.append({
                "category": "seo",
                "title": "Missing Primary H1 Tag",
                "severity": "medium",
                "evidence": "No `<h1>` heading element found in body content.",
                "recommendation": "Incorporate a single descriptive H1 tag representing the core service or business value."
            })
        elif h1_count > 2:
            seo_score -= 10
        result.seo_score = max(10, min(100, seo_score))

        # 4. Accessibility Audit (0-100)
        a11y_score = 100
        total_images = len(crawl.images)
        missing_alt = sum(1 for img in crawl.images if not img.get("has_alt"))
        
        result.metrics.append({
            "category": "accessibility",
            "metric_name": "Image Alt Coverage",
            "value": f"{total_images - missing_alt}/{total_images} images with alt text",
            "score": 100 if missing_alt == 0 else max(30, 100 - (missing_alt * 10))
        })
        
        if missing_alt > 0:
            ded = min(30, missing_alt * 8)
            a11y_score -= ded
            result.issues.append({
                "category": "accessibility",
                "title": "Missing Image Alt Tags",
                "severity": "medium",
                "evidence": f"{missing_alt} image(s) out of {total_images} lack `alt` attributes.",
                "recommendation": "Provide concise, descriptive alt text for all content-bearing images."
            })
        result.accessibility_score = max(20, min(100, a11y_score))

        # 5. Security Audit (0-100)
        sec_score = 100
        is_https = bool(crawl.ssl_valid)
        has_hsts = any("strict-transport-security" in k.lower() for k in crawl.headers.keys())
        
        result.metrics.append({
            "category": "security",
            "metric_name": "TLS/HTTPS Encryption",
            "value": "Valid TLS/HTTPS" if is_https else ("SSL Error" if crawl.ssl_error else "Unencrypted HTTP"),
            "score": 100 if is_https else 0
        })
        result.metrics.append({
            "category": "security",
            "metric_name": "HSTS Protection",
            "value": "Enforced" if has_hsts else "Not Configured",
            "score": 100 if has_hsts else 40
        })
        
        if not is_https:
            sec_score -= 55
            result.issues.append({
                "category": "security",
                "title": "Insecure Connection (No Valid HTTPS)",
                "severity": "critical",
                "evidence": crawl.ssl_error or "Website does not enforce valid HTTPS encryption.",
                "recommendation": "Install a valid SSL certificate and enforce HTTPS redirection."
            })
        if not has_hsts and is_https:
            sec_score -= 15
        result.security_score = max(10, min(100, sec_score))

        # 6. UX & Conversion Audit (0-100)
        ux_score = 100
        conv_score = 100
        has_forms = len(crawl.forms) > 0
        has_ctas = len(crawl.cta_texts) > 0
        has_phone = len(crawl.phones) > 0
        has_email = len(crawl.emails) > 0
        
        result.metrics.append({
            "category": "conversion",
            "metric_name": "Call-to-Action Elements",
            "value": f"{len(crawl.cta_texts)} CTAs detected" if has_ctas else "No prominent CTAs",
            "score": 100 if has_ctas else 25
        })
        result.metrics.append({
            "category": "conversion",
            "metric_name": "Inquiry / Booking Forms",
            "value": f"{len(crawl.forms)} forms" if has_forms else "Missing",
            "score": 100 if has_forms else 30
        })
        result.metrics.append({
            "category": "conversion",
            "metric_name": "Direct Contact Channels",
            "value": f"{len(crawl.emails)} email(s), {len(crawl.phones)} phone(s)",
            "score": 100 if (has_phone or has_email) else 20
        })
        
        if not has_ctas:
            conv_score -= 35
            ux_score -= 20
            result.issues.append({
                "category": "conversion",
                "title": "Missing Direct Call-to-Action (CTA)",
                "severity": "high",
                "evidence": "No conversion-focused action buttons (e.g. 'Book Table', 'Request Quote', 'Contact Us') detected.",
                "recommendation": "Add prominent, contrasting call-to-action buttons in header and hero sections."
            })
            
        if not has_forms:
            conv_score -= 25
            result.issues.append({
                "category": "conversion",
                "title": "Missing Lead Capture / Reservation Form",
                "severity": "medium",
                "evidence": "No interactive input form found on homepage.",
                "recommendation": "Integrate an embedded booking or contact form to convert website visitors."
            })
            
        if not has_phone and not has_email:
            conv_score -= 20
            result.issues.append({
                "category": "conversion",
                "title": "Missing Direct Contact Channels",
                "severity": "medium",
                "evidence": "Neither telephone number nor contact email was visible in markup.",
                "recommendation": "Provide clear click-to-call phone and direct email links."
            })
            
        result.ux_score = max(20, min(100, ux_score))
        result.conversion_score = max(20, min(100, conv_score))

        # Detect Technologies
        result.technologies = tech_detector.detect(crawl)

        # Calculate Overall Deterministic Score
        weights = [
            (result.performance_score, 0.15),
            (result.mobile_score, 0.25),
            (result.seo_score, 0.20),
            (result.accessibility_score, 0.10),
            (result.security_score, 0.10),
            (result.ux_score, 0.10),
            (result.conversion_score, 0.10),
        ]
        result.overall_score = int(sum(score * weight for score, weight in weights))
        
        issue_count = len(result.issues)
        result.summary = f"Complete audit measured overall score {result.overall_score}/100 based on live page inspection. Identified {issue_count} observable service opportunities."
        
        return result

audit_engine = WebsiteIntelligenceEngine()
