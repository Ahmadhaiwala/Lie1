"""
Location Intent Models
----------------------
Models for parsing and representing geographic intent from user queries.
"""
from dataclasses import dataclass
from typing import Optional, Tuple
from enum import Enum


class LocationSource(str, Enum):
    """Source of the location constraint"""
    USER_LOCATION = "user_location"      # User's current location
    EXPLICIT_LOCATION = "explicit_location"  # User specified a place
    NEAR_ME = "near_me"                  # User said "near me" / "nearby"
    COUNTRY = "country"                  # Country-level search
    MISSING = "missing"                  # No location specified


@dataclass
class LocationIntent:
    """
    Parsed geographic intent from user query.
    
    Examples:
        "restaurants near me" → 
            location_source=NEAR_ME, radius_km=10
        
        "dentists within 5km of Ahmedabad" → 
            location_source=EXPLICIT_LOCATION, 
            search_center="Ahmedabad", 
            radius_km=5
        
        "cafes in London" → 
            location_source=EXPLICIT_LOCATION,
            search_center="London",
            radius_km=None
        
        "Find businesses" → 
            location_source=MISSING
    """
    location_source: LocationSource
    search_center: Optional[str] = None  # City/place name
    search_center_coords: Optional[Tuple[float, float]] = None  # (lat, lng)
    radius_km: Optional[float] = None
    location_confidence: float = 1.0  # 0.0 - 1.0
    
    # Original query for debugging
    raw_query: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "location_source": self.location_source.value,
            "search_center": self.search_center,
            "search_center_coords": self.search_center_coords,
            "radius_km": self.radius_km,
            "location_confidence": self.location_confidence,
            "raw_query": self.raw_query,
        }
    
    @property
    def is_missing(self) -> bool:
        """Check if location is missing"""
        return self.location_source == LocationSource.MISSING
    
    @property
    def has_radius_constraint(self) -> bool:
        """Check if radius filtering should be applied"""
        return self.radius_km is not None
    
    @property
    def requires_user_location(self) -> bool:
        """Check if user's current location is needed"""
        return self.location_source in (LocationSource.USER_LOCATION, LocationSource.NEAR_ME)


@dataclass
class SearchContext:
    """
    Metadata about the geographic search scope.
    Included in lead output for transparency.
    """
    location_source: str
    search_center: Optional[str]
    search_center_coords: Optional[Tuple[float, float]]
    radius_km: Optional[float]
    business_categories: list[str]
    location_confidence: float
    total_discovered: int = 0
    within_radius: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            "location_source": self.location_source,
            "search_center": self.search_center,
            "radius_km": self.radius_km,
            "business_categories": self.business_categories,
            "location_confidence": self.location_confidence,
            "total_discovered": self.total_discovered,
            "within_radius": self.within_radius,
        }
