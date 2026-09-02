import json
from typing import List, Dict, Any, Optional, Tuple
from backend.app.services.audit.engine import AuditResult
from backend.app.services.crawler.safe_crawler import CrawlResult

class OpportunityMatch:
    def __init__(
        self,
        opportunity_type: str,
        observed_evidence: str,
        inferred_benefit: str,
        confidence: float = 1.0,
        score_impact: int = 10,
        recommended_service: str = ""
    ):
        self.opportunity_type = opportunity_type
        self.observed_evidence = observed_evidence
        self.inferred_benefit = inferred_benefit
        self.confidence = confidence
        self.score_impact = score_impact
        self.recommended_service = recommended_service or opportunity_type

class OpportunityEngine:
    def evaluate(
        self,
        has_website: bool,
        audit: Optional[AuditResult] = None,
        has_contact_email: bool = False,
        has_phone: bool = False,
        is_fresh: bool = True
    ) -> Tuple[List[OpportunityMatch], str]:
        """
        Deterministically identifies digital agency opportunities from observable facts.
        """
        opportunities: List[OpportunityMatch] = []
        
        if not has_website:
            opportunities.append(OpportunityMatch(
                opportunity_type="New Website Development",
                observed_evidence="No active website or domain registered for this business.",
                inferred_benefit="Building a modern website will capture local search traffic and build online credibility.",
                score_impact=25,
                recommended_service="Custom Website Development"
            ))
            return opportunities, "Custom Website Development"
            
        if not audit:
            return opportunities, "Website Audit"
            
        # Check Mobile Optimization
        if audit.mobile_score < 60:
            evidence = next((i["evidence"] for i in audit.issues if i["category"] == "mobile"), "Mobile score is below 60/100")
            opportunities.append(OpportunityMatch(
                opportunity_type="Responsive Redesign",
                observed_evidence=evidence,
                inferred_benefit="A responsive mobile redesign ensures seamless experience on smartphones and improves search engine ranking.",
                score_impact=15,
                recommended_service="Mobile Responsive Redesign"
            ))
            
        # Check Performance Optimization
        if audit.performance_score < 55:
            evidence = next((i["evidence"] for i in audit.issues if i["category"] == "performance"), "Performance score is below 55/100")
            opportunities.append(OpportunityMatch(
                opportunity_type="Performance Optimization",
                observed_evidence=evidence,
                inferred_benefit="Optimizing load speeds reduces visitor bounce rates and boosts conversion rates.",
                score_impact=10,
                recommended_service="Speed & Core Web Vitals Optimization"
            ))
            
        # Check SEO Opportunity
        if audit.seo_score < 65:
            evidence = next((i["evidence"] for i in audit.issues if i["category"] == "seo"), "SEO score is below 65/100")
            opportunities.append(OpportunityMatch(
                opportunity_type="SEO Optimization",
                observed_evidence=evidence,
                inferred_benefit="Fixing meta tags, heading hierarchies, and search indexability increases organic client acquisition.",
                score_impact=10,
                recommended_service="Technical SEO & On-Page Optimization"
            ))
            
        # Check Conversion / CTA
        if audit.conversion_score < 60:
            evidence = next((i["evidence"] for i in audit.issues if i["category"] == "conversion"), "No prominent CTA or lead capture flow")
            opportunities.append(OpportunityMatch(
                opportunity_type="Conversion Optimization",
                observed_evidence=evidence,
                inferred_benefit="Adding prominent action buttons and optimized inquiry forms converts passive visitors into paying inquiries.",
                score_impact=10,
                recommended_service="Conversion Rate Optimization & Lead Funnel"
            ))
            
        # Check Security
        if audit.security_score < 70:
            evidence = next((i["evidence"] for i in audit.issues if i["category"] == "security"), "Insecure HTTP or missing security headers")
            opportunities.append(OpportunityMatch(
                opportunity_type="Security & SSL Setup",
                observed_evidence=evidence,
                inferred_benefit="Securing the domain with valid SSL and security headers builds customer trust and prevents browser warnings.",
                score_impact=10,
                recommended_service="SSL & Website Security Hardening"
            ))
            
        # Determine primary recommended service
        if opportunities:
            # Sort by score impact
            opportunities.sort(key=lambda x: x.score_impact, reverse=True)
            primary_rec = opportunities[0].recommended_service
        else:
            primary_rec = "Website Maintenance & Ongoing Support"
            
        return opportunities, primary_rec

opportunity_engine = OpportunityEngine()
