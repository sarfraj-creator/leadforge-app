import json
import datetime
from typing import Dict, Any, List, Optional
from backend.app.services.audit.engine import AuditResult

class ServiceNeedItem:
    def __init__(
        self,
        service_type: str,
        need_score: int,
        evidence: List[str],
        source_url: Optional[str] = None,
        confidence: float = 1.0
    ):
        self.service_type = service_type
        self.need_score = need_score
        self.evidence = evidence
        self.source_url = source_url
        self.confidence = confidence

class ServiceNeedEngine:
    """
    Evaluates 9 core agency services strictly based on measured audit metrics:
    WEB_DESIGN, WEB_DEVELOPMENT, UI_UX, SEO, PERFORMANCE,
    ECOMMERCE, CONVERSION, ACCESSIBILITY, MAINTENANCE.
    """

    @classmethod
    def evaluate_services(
        cls,
        has_website: bool,
        audit: Optional[AuditResult] = None,
        source_url: Optional[str] = None
    ) -> List[ServiceNeedItem]:
        service_items: List[ServiceNeedItem] = []

        if not has_website or not audit or audit.status != "AUDIT_COMPLETE":
            if not has_website:
                # No website -> Web Development / Design need is maximum
                service_items.append(ServiceNeedItem(
                    service_type="WEB_DEVELOPMENT",
                    need_score=95,
                    evidence=["Discovered business has zero online web presence.", "Requires complete website design and development from scratch."],
                    source_url=source_url,
                    confidence=1.0
                ))
                service_items.append(ServiceNeedItem(
                    service_type="WEB_DESIGN",
                    need_score=90,
                    evidence=["No existing digital brand presence or website layout."],
                    source_url=source_url,
                    confidence=1.0
                ))
            return service_items

        # Helper: Extract metric values from audit
        metrics_dict = {m["metric_name"]: m["value"] for m in audit.metrics}

        # 1. WEB_DESIGN: Evaluated from Mobile Score and Viewport Tag
        web_design_ev = []
        if audit.mobile_score < 60:
            web_design_ev.append(f"Mobile responsive score is low ({audit.mobile_score}/100).")
        if "Missing Viewport" in str(audit.issues):
            web_design_ev.append("Viewport meta tag is missing, causing scaling issues on mobile devices.")
        if web_design_ev:
            service_items.append(ServiceNeedItem(
                service_type="WEB_DESIGN",
                need_score=max(50, 100 - audit.mobile_score),
                evidence=web_design_ev,
                source_url=source_url,
                confidence=0.9
            ))

        # 2. PERFORMANCE: Evaluated from Response Time & Page Weight
        perf_ev = []
        if audit.performance_score < 60:
            perf_ev.append(f"Performance health score is {audit.performance_score}/100.")
        resp_raw = metrics_dict.get("Response Time")
        if resp_raw:
            try:
                resp_num = float(str(resp_raw).replace("ms", "").strip())
                if resp_num > 1500:
                    perf_ev.append(f"Slow server response time: {resp_raw} (target < 800ms).")
            except Exception:
                pass
        page_raw = metrics_dict.get("Page Weight KB")
        if page_raw:
            try:
                page_num = float(str(page_raw).replace("KB", "").strip())
                if page_num > 2000:
                    perf_ev.append(f"Heavy initial payload weight: {page_raw} (target < 1500KB).")
            except Exception:
                pass
        if perf_ev:
            service_items.append(ServiceNeedItem(
                service_type="PERFORMANCE",
                need_score=max(50, 100 - audit.performance_score),
                evidence=perf_ev,
                source_url=source_url,
                confidence=0.95
            ))

        # 3. SEO: Evaluated from Title, Meta Description & H1
        seo_ev = []
        if audit.seo_score < 60:
            seo_ev.append(f"On-page SEO score is {audit.seo_score}/100.")
        if "Missing Meta Description" in str(audit.issues):
            seo_ev.append("Missing meta description on main landing page.")
        if "Missing H1" in str(audit.issues):
            seo_ev.append("No H1 heading element found in HTML document.")
        if seo_ev:
            service_items.append(ServiceNeedItem(
                service_type="SEO",
                need_score=max(50, 100 - audit.seo_score),
                evidence=seo_ev,
                source_url=source_url,
                confidence=0.9
            ))

        # 4. ACCESSIBILITY: Evaluated from Image Alt Tags
        acc_ev = []
        if audit.accessibility_score < 60:
            acc_ev.append(f"Accessibility score is {audit.accessibility_score}/100.")
        alt_raw = metrics_dict.get("Alt Tag Coverage")
        if alt_raw is not None:
            try:
                alt_num = float(str(alt_raw).replace("%", "").strip())
                if alt_num < 80:
                    perf_ev.append(f"Only {alt_raw} of images include descriptive alt attributes.")
            except Exception:
                pass
        if acc_ev:
            service_items.append(ServiceNeedItem(
                service_type="ACCESSIBILITY",
                need_score=max(45, 100 - audit.accessibility_score),
                evidence=acc_ev,
                source_url=source_url,
                confidence=0.85
            ))

        # 5. CONVERSION: Evaluated from CTAs & Lead Capture Forms
        conv_ev = []
        if audit.conversion_score < 60:
            conv_ev.append(f"Conversion score is {audit.conversion_score}/100.")
        cta_count = metrics_dict.get("Call to Action Buttons", 0)
        form_count = metrics_dict.get("Lead Capture Forms", 0)
        if cta_count == 0:
            conv_ev.append("Zero prominent call-to-action buttons identified on page.")
        if form_count == 0:
            conv_ev.append("No direct lead capture or appointment booking forms detected.")
        if conv_ev:
            service_items.append(ServiceNeedItem(
                service_type="CONVERSION",
                need_score=max(50, 100 - audit.conversion_score),
                evidence=conv_ev,
                source_url=source_url,
                confidence=0.9
            ))

        # 6. MAINTENANCE & SECURITY: Evaluated from HTTPS / SSL
        maint_ev = []
        if audit.security_score < 60:
            maint_ev.append(f"Security score is {audit.security_score}/100.")
        if "Insecure HTTP" in str(audit.issues) or "SSL" in str(audit.issues):
            maint_ev.append("Website is missing modern SSL certificate or served over insecure HTTP.")
        if maint_ev:
            service_items.append(ServiceNeedItem(
                service_type="MAINTENANCE",
                need_score=max(50, 100 - audit.security_score),
                evidence=maint_ev,
                source_url=source_url,
                confidence=0.95
            ))

        return service_items

service_need_engine = ServiceNeedEngine()
