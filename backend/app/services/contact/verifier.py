import re
import dns.resolver
from typing import Dict, Any, Optional
import datetime

DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com",
    "throwawaymail.com", "yopmail.com", "trashmail.com"
}

ROLE_BASED_PREFIXES = {
    "admin", "info", "contact", "support", "sales", "billing", "hello", "help",
    "office", "team", "marketing", "press", "jobs", "careers", "enquiries"
}

class EmailVerificationProvider:
    @staticmethod
    async def verify(email: str) -> Dict[str, Any]:
        """
        Rigorous email verification separating:
        - syntax_valid: RFC 5322 regex conformance
        - domain_valid: DNS domain existence
        - mx_valid: DNS MX records configured (DOMAIN_MAIL_ENABLED)
        - mailbox_verified: Direct SMTP response / delivery confirmation
        """
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()

        if not email or not isinstance(email, str):
            return {
                "syntax_valid": False,
                "domain_valid": False,
                "mx_valid": False,
                "mailbox_verified": False,
                "status": "INVALID",
                "reason": "Email address is empty or null",
                "confidence": 1.0,
                "verified_at": now_iso
            }
            
        clean_email = email.strip().lower()
        
        # 1. Syntax Check
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(pattern, clean_email):
            return {
                "syntax_valid": False,
                "domain_valid": False,
                "mx_valid": False,
                "mailbox_verified": False,
                "status": "INVALID",
                "reason": "Malformed email syntax (does not match RFC 5322)",
                "confidence": 1.0,
                "verified_at": now_iso
            }
            
        local_part, domain_part = clean_email.split("@", 1)
        
        # 2. Disposable Domain Check
        if domain_part in DISPOSABLE_DOMAINS:
            return {
                "syntax_valid": True,
                "domain_valid": True,
                "mx_valid": False,
                "mailbox_verified": False,
                "status": "DISPOSABLE",
                "reason": "Disposable or temporary mailbox service",
                "confidence": 0.98,
                "verified_at": now_iso
            }
            
        # 3. DNS MX Record Check
        mx_valid = False
        domain_valid = False
        mx_hosts = []
        try:
            answers = dns.resolver.resolve(domain_part, 'MX')
            if answers:
                mx_valid = True
                domain_valid = True
                mx_hosts = [str(r.exchange).rstrip('.') for r in answers]
        except (dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            return {
                "syntax_valid": True,
                "domain_valid": False,
                "mx_valid": False,
                "mailbox_verified": False,
                "status": "INVALID",
                "reason": f"Domain '{domain_part}' does not exist in public DNS",
                "confidence": 0.95,
                "verified_at": now_iso
            }
        except dns.resolver.NoAnswer:
            # Check A record
            try:
                a_answers = dns.resolver.resolve(domain_part, 'A')
                domain_valid = bool(a_answers)
            except Exception:
                domain_valid = False
            return {
                "syntax_valid": True,
                "domain_valid": domain_valid,
                "mx_valid": False,
                "mailbox_verified": False,
                "status": "SYNTAX_VALID_ONLY",
                "reason": "Domain exists but has no configured MX mail exchange servers",
                "confidence": 0.90,
                "verified_at": now_iso
            }
        except Exception as e:
            # DNS lookup timeout/network error
            domain_valid = True
            
        is_role = local_part in ROLE_BASED_PREFIXES
        
        if mx_valid:
            status_label = "DOMAIN_MAIL_ENABLED"
            reason = f"Active MX records verified ({', '.join(mx_hosts[:2])})"
            if is_role:
                reason += f" — Identified as generic business inbox ({local_part}@)"
        else:
            status_label = "SYNTAX_VALID_ONLY"
            reason = "Syntax valid; MX record verification pending or unconfirmed"

        return {
            "syntax_valid": True,
            "domain_valid": domain_valid,
            "mx_valid": mx_valid,
            "mailbox_verified": False, # Explicitly False unless direct SMTP handshake probe executed
            "status": status_label,
            "is_role_based": is_role,
            "mx_hosts": mx_hosts,
            "reason": reason,
            "confidence": 0.90 if mx_valid else 0.50,
            "verified_at": now_iso
        }

email_verifier = EmailVerificationProvider()
