import re
from typing import List, Dict, Any
from backend.app.services.crawler.safe_crawler import CrawlResult

class TechDetector:
    def detect(self, crawl: CrawlResult) -> List[Dict[str, Any]]:
        detected = []
        html = crawl.raw_html.lower()
        headers = {k.lower(): v.lower() for k, v in crawl.headers.items()}
        server_header = headers.get("server", "")
        powered_by = headers.get("x-powered-by", "")
        
        # WordPress
        if "wp-content" in html or "wp-includes" in html or "wordpress" in html:
            detected.append({
                "name": "WordPress",
                "category": "CMS",
                "confidence": 0.98,
                "version": self._extract_wp_version(crawl.raw_html)
            })
            
        # WooCommerce
        if "woocommerce" in html or "wc-block" in html:
            detected.append({
                "name": "WooCommerce",
                "category": "Ecommerce",
                "confidence": 0.95,
                "version": None
            })
            
        # Shopify
        if "cdn.shopify.com" in html or "shopify.com" in html or "myshopify" in html:
            detected.append({
                "name": "Shopify",
                "category": "Ecommerce",
                "confidence": 0.99,
                "version": None
            })
            
        # Webflow
        if "assets.website-files.com" in html or "w-nav" in html or "w-slider" in html:
            detected.append({
                "name": "Webflow",
                "category": "Website Builder",
                "confidence": 0.95,
                "version": None
            })
            
        # Wix
        if "wix.com" in html or "wixsite" in html or "parastorage.com" in html:
            detected.append({
                "name": "Wix",
                "category": "Website Builder",
                "confidence": 0.98,
                "version": None
            })
            
        # Squarespace
        if "squarespace.com" in html or "static1.squarespace" in html:
            detected.append({
                "name": "Squarespace",
                "category": "Website Builder",
                "confidence": 0.98,
                "version": None
            })
            
        # React / Next.js
        if "__next" in html or "_next/static" in html:
            detected.append({
                "name": "Next.js",
                "category": "Framework",
                "confidence": 0.95,
                "version": None
            })
            detected.append({
                "name": "React",
                "category": "Frontend Library",
                "confidence": 0.95,
                "version": None
            })
        elif "react" in html or "data-reactroot" in html:
            detected.append({
                "name": "React",
                "category": "Frontend Library",
                "confidence": 0.90,
                "version": None
            })
            
        # Vue.js / Nuxt
        if "__nuxt" in html or "data-n-head" in html:
            detected.append({
                "name": "Nuxt.js",
                "category": "Framework",
                "confidence": 0.95,
                "version": None
            })
            
        # PHP / Laravel
        if "php" in server_header or "php" in powered_by or ".php" in html:
            detected.append({
                "name": "PHP",
                "category": "Backend",
                "confidence": 0.85,
                "version": None
            })
        if "laravel" in html or "laravel_session" in html or "xsrf-token" in html:
            detected.append({
                "name": "Laravel",
                "category": "Framework",
                "confidence": 0.90,
                "version": None
            })
            
        # Analytics
        if "googletagmanager.com" in html or "google-analytics.com" in html:
            detected.append({
                "name": "Google Analytics",
                "category": "Analytics",
                "confidence": 0.99,
                "version": None
            })
        if "connect.facebook.net" in html or "fbevents.js" in html:
            detected.append({
                "name": "Facebook Pixel",
                "category": "Marketing",
                "confidence": 0.95,
                "version": None
            })
            
        return detected

    def _extract_wp_version(self, raw_html: str) -> str:
        m = re.search(r'content="WordPress\s+([\d.]+)"', raw_html, re.I)
        return m.group(1) if m else None

tech_detector = TechDetector()
