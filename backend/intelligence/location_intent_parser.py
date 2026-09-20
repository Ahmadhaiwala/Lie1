"""
Location Intent Parser
----------------------
Parse user queries to extract geographic intent.

Determines:
  - Whether user specified a location
  - If they said "near me" vs explicit city/place
  - Requested radius (explicit or default)
  - Geographic confidence score
"""
import re
from typing import Optional, Tuple
from models.location_intent import LocationIntent, LocationSource


class LocationIntentParser:
    """
    Parse user queries for geographic intent.
    
    Examples:
        "restaurants near me" → NEAR_ME, radius=10km
        "dentists within 5km" → NEAR_ME, radius=5km
        "cafes in London" → EXPLICIT_LOCATION, center="London"
        "restaurants within 25km of Ahmedabad" → EXPLICIT_LOCATION, center="Ahmedabad", radius=25km
        "find businesses" → MISSING
    """
    
    # Patterns for "near me" detection
    NEAR_ME_PATTERNS = [
        r'\bnear\s+me\b',
        r'\bnearby\b',
        r'\baround\s+me\b',
        r'\bclose\s+to\s+me\b',
        r'\bin\s+my\s+area\b',
    ]
    
    # Patterns for radius extraction
    RADIUS_PATTERNS = [
        r'within\s+(\d+(?:\.\d+)?)\s*km\b',
        r'within\s+(\d+(?:\.\d+)?)\s*kilometers?\b',
        r'within\s+(\d+(?:\.\d+)?)\s*miles?\b',
        r'(\d+)\s*km\s+radius\b',
        r'(\d+)\s*mile\s+radius\b',
    ]
    
    # Patterns for explicit location
    LOCATION_PATTERNS = [
        r'\bin\s+([A-Z][a-zA-Z\s]+(?:,\s*[A-Z]{2,})?)\b',  # "in London" or "in San Francisco, CA"
        r'(?:within\s+\d+\s*(?:km|miles?)\s+of\s+)([A-Z][a-zA-Z\s]+)',  # "within 5km of Ahmedabad"
        r'\bat\s+([A-Z][a-zA-Z\s]+)\b',  # "at Mumbai"
    ]
    
    # Default radius based on location type
    DEFAULT_URBAN_RADIUS_KM = 10
    DEFAULT_SUBURBAN_RADIUS_KM = 15
    DEFAULT_RURAL_RADIUS_KM = 30
    
    def parse(
        self,
        query: str,
        user_location: Optional[Tuple[float, float]] = None
    ) -> LocationIntent:
        """
        Parse a user query to extract location intent.
        
        Args:
            query: User's search query
            user_location: Optional (latitude, longitude) of user's current position
        
        Returns:
            LocationIntent object
        """
        query_lower = query.lower()
        
        # Check for "near me" patterns
        has_near_me = self._has_near_me(query_lower)
        
        # Extract radius if specified
        radius_km = self._extract_radius(query_lower)
        
        # Extract explicit location
        explicit_location = self._extract_location(query)
        
        # Determine location source
        if explicit_location and radius_km:
            # "restaurants within 5km of Ahmedabad"
            return LocationIntent(
                location_source=LocationSource.EXPLICIT_LOCATION,
                search_center=explicit_location,
                radius_km=radius_km,
                location_confidence=0.95,
                raw_query=query,
            )
        
        elif explicit_location:
            # "restaurants in London"
            return LocationIntent(
                location_source=LocationSource.EXPLICIT_LOCATION,
                search_center=explicit_location,
                radius_km=None,  # No radius constraint
                location_confidence=0.9,
                raw_query=query,
            )
        
        elif has_near_me and user_location:
            # "restaurants near me" with available user location
            return LocationIntent(
                location_source=LocationSource.NEAR_ME,
                search_center="user_current_location",
                search_center_coords=user_location,
                radius_km=radius_km or self.DEFAULT_URBAN_RADIUS_KM,
                location_confidence=0.85,
                raw_query=query,
            )
        
        elif has_near_me and not user_location:
            # "restaurants near me" but user location not available
            return LocationIntent(
                location_source=LocationSource.NEAR_ME,
                search_center=None,
                radius_km=radius_km or self.DEFAULT_URBAN_RADIUS_KM,
                location_confidence=0.5,
                raw_query=query,
            )
        
        elif radius_km and not explicit_location:
            # "restaurants within 5km" (implies current location)
            if user_location:
                return LocationIntent(
                    location_source=LocationSource.USER_LOCATION,
                    search_center="user_current_location",
                    search_center_coords=user_location,
                    radius_km=radius_km,
                    location_confidence=0.8,
                    raw_query=query,
                )
            else:
                # Has radius but no user location available
                return LocationIntent(
                    location_source=LocationSource.NEAR_ME,
                    search_center=None,
                    radius_km=radius_km,
                    location_confidence=0.5,
                    raw_query=query,
                )
        
        else:
            # No location specified
            return LocationIntent(
                location_source=LocationSource.MISSING,
                location_confidence=0.0,
                raw_query=query,
            )
    
    def _has_near_me(self, query_lower: str) -> bool:
        """Check if query contains 'near me' patterns"""
        for pattern in self.NEAR_ME_PATTERNS:
            if re.search(pattern, query_lower):
                return True
        return False
    
    def _extract_radius(self, query_lower: str) -> Optional[float]:
        """
        Extract radius from query.
        
        Returns:
            Radius in kilometers, or None if not specified
        """
        for pattern in self.RADIUS_PATTERNS:
            match = re.search(pattern, query_lower)
            if match:
                value = float(match.group(1))
                
                # Convert miles to km if needed
                if 'mile' in pattern:
                    value = value * 1.60934
                
                return round(value, 2)
        
        return None
    
    def _extract_location(self, query: str) -> Optional[str]:
        """
        Extract explicit location from query.
        
        Returns:
            Location name (e.g., "London", "Ahmedabad", "New York")
        """
        for pattern in self.LOCATION_PATTERNS:
            match = re.search(pattern, query)
            if match:
                location = match.group(1).strip()
                
                # Clean up
                location = re.sub(r'\s+', ' ', location)
                
                # Remove trailing words that aren't part of location
                stop_words = ['for', 'that', 'who', 'which', 'with', 'without']
                for word in stop_words:
                    if location.lower().endswith(f' {word}'):
                        location = location[:-len(word)-1]
                
                return location
        
        return None
    
    def get_default_radius(
        self,
        location_type: str = "urban"
    ) -> float:
        """
        Get default radius based on location type.
        
        Args:
            location_type: "urban", "suburban", or "rural"
        
        Returns:
            Default radius in kilometers
        """
        if location_type == "urban":
            return self.DEFAULT_URBAN_RADIUS_KM
        elif location_type == "suburban":
            return self.DEFAULT_SUBURBAN_RADIUS_KM
        elif location_type == "rural":
            return self.DEFAULT_RURAL_RADIUS_KM
        else:
            return self.DEFAULT_URBAN_RADIUS_KM


# Convenience function
def parse_location_intent(
    query: str,
    user_location: Optional[Tuple[float, float]] = None
) -> LocationIntent:
    """
    Parse location intent from a query string.
    
    Args:
        query: User's search query
        user_location: Optional (latitude, longitude) of user
    
    Returns:
        LocationIntent object
    """
    parser = LocationIntentParser()
    return parser.parse(query, user_location)
