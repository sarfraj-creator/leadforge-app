import re
from typing import Dict, Any, Optional

class PhoneVerifier:
    """
    Normalizes international and local phone numbers to standard E.164
    and validates ITU-T format compliance.
    """

    @staticmethod
    def verify_and_normalize(phone: Optional[str], default_country_code: str = "+1") -> Dict[str, Any]:
        if not phone or not phone.strip():
            return {
                "raw_phone": None,
                "normalized_e164": None,
                "validation_status": "UNVERIFIED",
                "is_valid": False
            }

        raw = phone.strip()
        # Remove extra whitespace and special characters except '+'
        digits_only = re.sub(r"[^\d+]", "", raw)

        # Basic international validation
        if digits_only.startswith("+"):
            digits = digits_only[1:]
            if 7 <= len(digits) <= 15:
                return {
                    "raw_phone": raw,
                    "normalized_e164": f"+{digits}",
                    "validation_status": "VALID_E164",
                    "is_valid": True
                }
            else:
                return {
                    "raw_phone": raw,
                    "normalized_e164": None,
                    "validation_status": "INVALID",
                    "is_valid": False
                }
        else:
            # Local number format
            digits = re.sub(r"\D", "", digits_only)
            if 7 <= len(digits) <= 12:
                # Store local format
                return {
                    "raw_phone": raw,
                    "normalized_e164": f"{default_country_code}{digits}" if not digits.startswith("0") else f"+{digits}",
                    "validation_status": "LOCAL_FORMAT",
                    "is_valid": True
                }
            else:
                return {
                    "raw_phone": raw,
                    "normalized_e164": None,
                    "validation_status": "INVALID",
                    "is_valid": False
                }

phone_verifier = PhoneVerifier()
