import csv
import io
import hashlib
from typing import List, Dict, Any, Optional
from backend.app.services.discovery.base import LeadSourceAdapter, DiscoveredRecord

class DirectoryAdapter(LeadSourceAdapter):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(source_name="PublicDirectory", config=config)

    async def health_check(self) -> Dict[str, Any]:
        return {
            "status": "CONNECTED",
            "provider": "Public Commercial Registries & Tech Indexes",
            "rate_limit_per_min": 60
        }

    async def discover(
        self,
        query: str,
        location: str,
        industry: Optional[str] = None,
        limit: int = 50
    ) -> List[DiscoveredRecord]:
        # Extensible directory adapter for permitted public datasets
        return []

class CSVImportAdapter(LeadSourceAdapter):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(source_name="CSVImport", config=config)

    async def health_check(self) -> Dict[str, Any]:
        return {"status": "CONNECTED", "provider": "User CSV/Dataset Parser"}

    async def discover(
        self,
        query: str,
        location: str,
        industry: Optional[str] = None,
        limit: int = 50
    ) -> List[DiscoveredRecord]:
        return []

    def parse_csv(
        self,
        file_content: str,
        column_mapping: Optional[Dict[str, str]] = None,
        source_label: str = "User CSV Import"
    ) -> List[DiscoveredRecord]:
        """
        Robust parser with intelligent field auto-detection for CSV/TSV uploads:
        Auto-detects columns: Business Name, Company, Website, Domain, URL, Phone, Telephone, Email, City, Country, Address.
        """
        records: List[DiscoveredRecord] = []
        mapping = column_mapping or {}

        # Auto-detect delimiter (, or \t or ;)
        sample = file_content[:2048]
        delimiter = ","
        if "\t" in sample and sample.count("\t") > sample.count(","):
            delimiter = "\t"
        elif ";" in sample and sample.count(";") > sample.count(","):
            delimiter = ";"

        reader = csv.DictReader(io.StringIO(file_content), delimiter=delimiter)
        
        for idx, row in enumerate(reader):
            # Clean keys to lowercase
            clean_row = {k.strip().lower(): (v.strip() if v else "") for k, v in row.items() if k}

            # Field resolution
            b_name = (
                row.get(mapping.get("business_name", ""))
                or clean_row.get("business_name")
                or clean_row.get("company_name")
                or clean_row.get("company")
                or clean_row.get("business")
                or clean_row.get("name")
            )
            if not b_name or len(b_name.strip()) < 2:
                continue

            website = (
                row.get(mapping.get("website", ""))
                or clean_row.get("website")
                or clean_row.get("domain")
                or clean_row.get("url")
                or clean_row.get("site")
            )
            phone = (
                row.get(mapping.get("phone", ""))
                or clean_row.get("phone")
                or clean_row.get("phone_number")
                or clean_row.get("telephone")
                or clean_row.get("tel")
            )
            email = (
                row.get(mapping.get("email", ""))
                or clean_row.get("email")
                or clean_row.get("business_email")
                or clean_row.get("contact_email")
            )
            city = (
                row.get(mapping.get("city", ""))
                or clean_row.get("city")
                or clean_row.get("town")
            )
            country = (
                row.get(mapping.get("country", ""))
                or clean_row.get("country")
                or clean_row.get("nation")
            )
            industry = (
                row.get(mapping.get("industry", ""))
                or clean_row.get("industry")
                or clean_row.get("category")
                or clean_row.get("sector")
            )

            record_hash = hashlib.sha256(f"{b_name}_{website}_{idx}".encode("utf-8")).hexdigest()[:12]

            rec = DiscoveredRecord(
                business_name=b_name.strip(),
                source="CSVImport",
                source_record_id=f"csv_{record_hash}",
                source_url=website,
                website=website,
                phone=phone,
                email=email,
                city=city,
                country=country,
                industry=industry or "Commercial",
                confidence=1.0,
                raw_data=row
            )
            if self.validate(rec):
                records.append(self.normalize(rec))

        return records
