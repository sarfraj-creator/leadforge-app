import ssl
import socket
import datetime
import logging
from typing import Dict, Any, Optional, List
import dns.resolver

logger = logging.getLogger("leadforge.domain.intel")

class DomainIntelligence:
    """
    Extracts public DNS records, TLS/SSL certificates, and RDAP registration metadata.
    """

    @staticmethod
    async def get_domain_intel(domain: str) -> Dict[str, Any]:
        clean_domain = domain.strip().lower().replace("http://", "").replace("https://", "").split("/")[0]
        intel: Dict[str, Any] = {
            "domain": clean_domain,
            "dns_a_records": [],
            "dns_mx_records": [],
            "dns_ns_records": [],
            "has_mx": False,
            "tls_valid": False,
            "tls_issuer": None,
            "tls_expires_at": None,
            "registrar": None,
            "registration_date": None,
            "expiration_date": None,
            "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
        }

        # 1. DNS Resolution (A, MX, NS)
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 4.0
            resolver.lifetime = 4.0

            # A Records
            try:
                a_answers = resolver.resolve(clean_domain, "A")
                intel["dns_a_records"] = [rdata.to_text() for rdata in a_answers]
            except Exception:
                pass

            # MX Records
            try:
                mx_answers = resolver.resolve(clean_domain, "MX")
                intel["dns_mx_records"] = [rdata.exchange.to_text() for rdata in mx_answers]
                intel["has_mx"] = len(intel["dns_mx_records"]) > 0
            except Exception:
                pass

            # NS Records
            try:
                ns_answers = resolver.resolve(clean_domain, "NS")
                intel["dns_ns_records"] = [rdata.to_text() for rdata in ns_answers]
            except Exception:
                pass
        except Exception as e:
            logger.debug("DNS lookup failed for %s: %s", clean_domain, e)

        # 2. TLS/SSL Certificate Inspection
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE  # Safe inspection
            with socket.create_connection((clean_domain, 443), timeout=3.0) as sock:
                with ctx.wrap_socket(sock, server_hostname=clean_domain) as ssock:
                    cert = ssock.getpeercert(binary_form=False)
                    if cert:
                        intel["tls_valid"] = True
                        issuer = dict(x[0] for x in cert.get("issuer", []))
                        intel["tls_issuer"] = issuer.get("organizationName") or issuer.get("commonName")
                        not_after = cert.get("notAfter")
                        if not_after:
                            intel["tls_expires_at"] = not_after
        except Exception:
            intel["tls_valid"] = False

        # 3. RDAP Public Lookup (ICANN public RDAP API)
        try:
            import httpx
            rdap_url = f"https://rdap.org/domain/{clean_domain}"
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.get(rdap_url)
                if res.status_code == 200:
                    data = res.json()
                    # Extract registrar
                    entities = data.get("entities", [])
                    for ent in entities:
                        roles = ent.get("roles", [])
                        if "registrar" in roles:
                            vcard = ent.get("vcardArray", [None, []])[1]
                            for item in vcard:
                                if item[0] == "fn":
                                    intel["registrar"] = item[3]
                    # Extract events (registration / expiration)
                    events = data.get("events", [])
                    for ev in events:
                        action = ev.get("eventAction")
                        date = ev.get("eventDate")
                        if action == "registration":
                            intel["registration_date"] = date
                        elif action == "expiration":
                            intel["expiration_date"] = date
        except Exception:
            pass

        return intel
