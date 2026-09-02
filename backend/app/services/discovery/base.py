from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import datetime
import hashlib
import json
from backend.app.core.deduplication import (
    normalize_domain,
    normalize_business_name,
    normalize_phone,
    normalize_email,
    compute_dedup_hash,
)

class DiscoveredRecord:
    def __init__(
        self,
        business_name: str,
        source: str,
        source_record_id: Optional[str] = None,
        source_url: Optional[str] = None,
        website: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        address: Optional[str] = None,
        city: Optional[str] = None,
        state: Optional[str] = None,
        country: Optional[str] = None,
        postal_code: Optional[str] = None,
        industry: Optional[str] = None,
        category: Optional[str] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        description: Optional[str] = None,
        employee_count: Optional[int] = None,
        confidence: float = 1.0,
        raw_data: Optional[Dict[str, Any]] = None,
    ):
        self.business_name = business_name.strip() if business_name else "Unknown Business"
        self.normalized_name = normalize_business_name(self.business_name)
        self.source = source
        self.source_record_id = source_record_id or f"{source}_{abs(hash(self.business_name))}"
        self.source_url = source_url
        self.website = website
        self.domain = normalize_domain(website) if website else None
        self.phone = normalize_phone(phone)
        self.email = normalize_email(email)
        self.address = address
        self.city = city
        self.state = state
        self.country = country
        self.postal_code = postal_code
        self.industry = industry
        self.category = category
        self.latitude = latitude
        self.longitude = longitude
        self.description = description
        self.employee_count = employee_count
        self.confidence = confidence
        self.raw_data = raw_data or {}
        self.discovered_at = datetime.datetime.now(datetime.timezone.utc)
        self.collected_at = self.discovered_at
        self.raw_data_hash = hashlib.sha256(
            json.dumps(self.raw_data, sort_keys=True, default=str).encode("utf-8")
        ).hexdigest()
        self.dedup_hash = compute_dedup_hash(
            business_name=self.business_name,
            domain=self.domain,
            phone=self.phone,
            city=self.city,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "business_name": self.business_name,
            "normalized_name": self.normalized_name,
            "source": self.source,
            "source_record_id": self.source_record_id,
            "source_url": self.source_url,
            "website": self.website,
            "domain": self.domain,
            "phone": self.phone,
            "business_email": self.email,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
            "industry": self.industry,
            "category": self.category,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "description": self.description,
            "employee_count": self.employee_count,
            "confidence": self.confidence,
            "raw_data_hash": self.raw_data_hash,
            "dedup_hash": self.dedup_hash,
            "discovered_at": self.discovered_at.isoformat(),
            "collected_at": self.collected_at.isoformat(),
        }

class LeadSourceAdapter(ABC):
    def __init__(self, source_name: str, config: Optional[Dict[str, Any]] = None):
        self.source_name = source_name
        self.config = config or {}

    @abstractmethod
    async def discover(
        self,
        query: str,
        location: str,
        industry: Optional[str] = None,
        limit: int = 50,
    ) -> List[DiscoveredRecord]:
        """Discovers raw business records based on parameters."""
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """Validates adapter connectivity, latency, and status."""
        pass

    def validate(self, record: DiscoveredRecord) -> bool:
        """Validates record meets minimal entity integrity requirements."""
        if not record.business_name or record.business_name.strip().lower() in ["unknown", "n/a", "null", "none"]:
            return False
        return True

    def get_rate_limit(self) -> int:
        """Returns allowed requests per minute."""
        return self.config.get("rate_limit_per_min", 30)

    def get_provenance(self) -> Dict[str, Any]:
        """Returns provenance metadata for the adapter."""
        return {
            "source_name": self.source_name,
            "adapter_type": self.__class__.__name__,
            "is_permitted_public": True,
            "rate_limit_per_min": self.get_rate_limit(),
        }

    def normalize(self, record: DiscoveredRecord) -> DiscoveredRecord:
        """Applies normalization to discovered fields."""
        record.domain = normalize_domain(record.website)
        record.phone = normalize_phone(record.phone)
        record.email = normalize_email(record.email)
        record.normalized_name = normalize_business_name(record.business_name)
        record.dedup_hash = compute_dedup_hash(
            business_name=record.business_name,
            domain=record.domain,
            phone=record.phone,
            city=record.city,
        )
        return record
