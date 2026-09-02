from typing import Dict, Any, Optional

# Canonical Industry Names
INDUSTRY_RESTAURANT = "Restaurant"
INDUSTRY_DENTIST = "Dentist / Dental Clinic"
INDUSTRY_LAW_FIRM = "Law Firm"
INDUSTRY_REAL_ESTATE = "Real Estate"
INDUSTRY_HOTEL = "Hotel / Hospitality"
INDUSTRY_GYM = "Gym / Fitness"
INDUSTRY_RETAIL = "E-Commerce / Retail"
INDUSTRY_HEALTHCARE = "Healthcare"
INDUSTRY_GENERAL = "General Business"

# Explicit OSM Tag to Industry Mapping
OSM_EXPLICIT_TAG_MAP = {
    # Food & Beverage / Restaurants
    ("amenity", "restaurant"): INDUSTRY_RESTAURANT,
    ("amenity", "cafe"): INDUSTRY_RESTAURANT,
    ("amenity", "fast_food"): INDUSTRY_RESTAURANT,
    ("amenity", "bar"): INDUSTRY_RESTAURANT,
    ("amenity", "pub"): INDUSTRY_RESTAURANT,
    ("amenity", "food_court"): INDUSTRY_RESTAURANT,
    ("amenity", "bistro"): INDUSTRY_RESTAURANT,
    
    # Dental & Medical
    ("amenity", "dentist"): INDUSTRY_DENTIST,
    ("amenity", "clinic"): INDUSTRY_DENTIST,
    ("amenity", "doctors"): INDUSTRY_HEALTHCARE,
    ("amenity", "hospital"): INDUSTRY_HEALTHCARE,
    ("amenity", "pharmacy"): INDUSTRY_HEALTHCARE,
    
    # Legal
    ("office", "lawyer"): INDUSTRY_LAW_FIRM,
    ("office", "legal"): INDUSTRY_LAW_FIRM,
    ("office", "notary"): INDUSTRY_LAW_FIRM,
    
    # Real Estate
    ("office", "estate_agent"): INDUSTRY_REAL_ESTATE,
    ("office", "property_management"): INDUSTRY_REAL_ESTATE,
    ("office", "real_estate"): INDUSTRY_REAL_ESTATE,
    
    # Hospitality / Hotels
    ("tourism", "hotel"): INDUSTRY_HOTEL,
    ("tourism", "motel"): INDUSTRY_HOTEL,
    ("tourism", "hostel"): INDUSTRY_HOTEL,
    ("tourism", "guest_house"): INDUSTRY_HOTEL,
    
    # Fitness / Gyms
    ("leisure", "fitness_centre"): INDUSTRY_GYM,
    ("leisure", "sports_centre"): INDUSTRY_GYM,
    ("leisure", "dance_studio"): INDUSTRY_GYM,
    
    # Retail / E-Commerce / Shops
    ("shop", "clothes"): INDUSTRY_RETAIL,
    ("shop", "clothing"): INDUSTRY_RETAIL,
    ("shop", "fashion"): INDUSTRY_RETAIL,
    ("shop", "boutique"): INDUSTRY_RETAIL,
    ("shop", "department_store"): INDUSTRY_RETAIL,
    ("shop", "shoes"): INDUSTRY_RETAIL,
    ("shop", "jewelry"): INDUSTRY_RETAIL,
    ("shop", "supermarket"): INDUSTRY_RETAIL,
    ("shop", "convenience"): INDUSTRY_RETAIL,
    ("shop", "bakery"): INDUSTRY_RESTAURANT,
}

QUERY_FALLBACK_MAP = {
    "restaurant": INDUSTRY_RESTAURANT,
    "food": INDUSTRY_RESTAURANT,
    "cafe": INDUSTRY_RESTAURANT,
    "dentist": INDUSTRY_DENTIST,
    "dental": INDUSTRY_DENTIST,
    "clinic": INDUSTRY_DENTIST,
    "lawyer": INDUSTRY_LAW_FIRM,
    "law": INDUSTRY_LAW_FIRM,
    "legal": INDUSTRY_LAW_FIRM,
    "real_estate": INDUSTRY_REAL_ESTATE,
    "real estate": INDUSTRY_REAL_ESTATE,
    "property": INDUSTRY_REAL_ESTATE,
    "hotel": INDUSTRY_HOTEL,
    "hospitality": INDUSTRY_HOTEL,
    "gym": INDUSTRY_GYM,
    "fitness": INDUSTRY_GYM,
    "clothing": INDUSTRY_RETAIL,
    "retail": INDUSTRY_RETAIL,
    "shop": INDUSTRY_RETAIL,
    "e-commerce": INDUSTRY_RETAIL,
    "ecommerce": INDUSTRY_RETAIL,
}

def resolve_industry_from_source(
    raw_tags: Optional[Dict[str, Any]],
    source_category: Optional[str] = None,
    query_industry: Optional[str] = None
) -> str:
    """
    Provenance-backed industry taxonomy resolution.
    Priority:
    1. Explicit verified source tag (e.g. amenity=restaurant, office=lawyer)
    2. Explicit source category
    3. Query / campaign fallback
    """
    tags = raw_tags or {}
    
    # 1. Check explicit OSM primary tags
    for tag_key in ["amenity", "office", "tourism", "leisure", "shop"]:
        tag_val = tags.get(tag_key)
        if tag_val:
            tag_val_clean = str(tag_val).lower().strip()
            # Direct tuple match
            if (tag_key, tag_val_clean) in OSM_EXPLICIT_TAG_MAP:
                return OSM_EXPLICIT_TAG_MAP[(tag_key, tag_val_clean)]
            
            # Generic category fallback
            if tag_key == "shop":
                return INDUSTRY_RETAIL
            if tag_key == "tourism" and "hotel" in tag_val_clean:
                return INDUSTRY_HOTEL
            if tag_key == "leisure" and ("fitness" in tag_val_clean or "gym" in tag_val_clean):
                return INDUSTRY_GYM
            if tag_key == "office" and "law" in tag_val_clean:
                return INDUSTRY_LAW_FIRM
            if tag_key == "office" and ("estate" in tag_val_clean or "property" in tag_val_clean):
                return INDUSTRY_REAL_ESTATE
            if tag_key == "amenity" and ("restaurant" in tag_val_clean or "cafe" in tag_val_clean or "food" in tag_val_clean):
                return INDUSTRY_RESTAURANT
            if tag_key == "amenity" and ("dentist" in tag_val_clean or "dental" in tag_val_clean):
                return INDUSTRY_DENTIST

    # 2. Check source_category
    if source_category:
        cat_clean = str(source_category).lower().strip()
        for k, v in QUERY_FALLBACK_MAP.items():
            if k in cat_clean:
                return v

    # 3. Fallback to query_industry
    if query_industry:
        q_clean = str(query_industry).lower().replace("_", " ").strip()
        for k, v in QUERY_FALLBACK_MAP.items():
            if k in q_clean or q_clean in k:
                return v
        return query_industry.replace("_", " ").title()

    return INDUSTRY_GENERAL
