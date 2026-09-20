"""
Location Resolver
Resolves and normalizes location data
"""
from typing import Optional, Dict, Any, Tuple
import re

from models.business import BusinessLocation


class LocationResolver:
    """Resolves and standardizes location information"""
    
    def __init__(self):
        """Initialize location resolver"""
        self._geocoding_cache: Dict[str, Tuple[float, float]] = {}
    
    async def resolve_location(
        self,
        location_string: str
    ) -> Optional[BusinessLocation]:
        """
        Resolve a location string to a structured location
        
        Args:
            location_string: Raw location string (e.g., "San Francisco, CA")
            
        Returns:
            Structured BusinessLocation or None
        """
        if not location_string:
            return None
        
        # Parse location components
        components = self._parse_location_string(location_string)
        
        # Get coordinates
        lat, lng = await self._geocode(location_string)
        
        return BusinessLocation(
            address=components.get("address"),
            city=components.get("city"),
            state=components.get("state"),
            country=components.get("country", "USA"),
            postal_code=components.get("postal_code"),
            latitude=lat,
            longitude=lng,
            is_primary=True
        )
    
    def _parse_location_string(
        self,
        location_string: str
    ) -> Dict[str, str]:
        """
        Parse location string into components
        
        Args:
            location_string: Raw location string
            
        Returns:
            Dictionary with location components
        """
        components = {}
        
        # Common patterns
        # "City, State" - "San Francisco, CA"
        if ", " in location_string:
            parts = [p.strip() for p in location_string.split(",")]
            if len(parts) >= 2:
                components["city"] = parts[0]
                components["state"] = parts[1]
                if len(parts) >= 3:
                    components["country"] = parts[2]
        else:
            # Just a city name
            components["city"] = location_string.strip()
        
        # Extract postal code if present
        postal_match = re.search(r'\b\d{5}(?:-\d{4})?\b', location_string)
        if postal_match:
            components["postal_code"] = postal_match.group()
        
        return components
    
    async def _geocode(
        self,
        location_string: str
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Get coordinates for a location
        
        Args:
            location_string: Location to geocode
            
        Returns:
            Tuple of (latitude, longitude) or (None, None)
        """
        # Check cache
        if location_string in self._geocoding_cache:
            return self._geocoding_cache[location_string]
        
        # Mock implementation
        # In production: Use geocoding API (Google Maps, Mapbox, etc.)
        
        # Mock coordinates for common cities
        mock_coordinates = {
            "San Francisco, CA": (37.7749, -122.4194),
            "New York, NY": (40.7128, -74.0060),
            "Los Angeles, CA": (34.0522, -118.2437),
            "Chicago, IL": (41.8781, -87.6298),
            "Houston, TX": (29.7604, -95.3698),
            "Seattle, WA": (47.6062, -122.3321),
            "Boston, MA": (42.3601, -71.0589),
            "Austin, TX": (30.2672, -97.7431),
        }
        
        # Try exact match first
        coords = mock_coordinates.get(location_string, (None, None))
        
        # Cache the result
        self._geocoding_cache[location_string] = coords
        
        return coords
    
    def normalize_location_string(self, location_string: str) -> str:
        """
        Normalize location string for consistency
        
        Args:
            location_string: Raw location string
            
        Returns:
            Normalized location string
        """
        if not location_string:
            return ""
        
        # Basic normalization
        normalized = location_string.strip()
        
        # Expand state abbreviations if needed
        state_map = {
            "CA": "California",
            "NY": "New York",
            "TX": "Texas",
            "FL": "Florida",
            "IL": "Illinois",
            "WA": "Washington",
            "MA": "Massachusetts",
            # Add more as needed
        }
        
        for abbr, full_name in state_map.items():
            normalized = re.sub(
                rf'\b{abbr}\b',
                full_name,
                normalized,
                flags=re.IGNORECASE
            )
        
        return normalized
    
    def calculate_distance(
        self,
        location1: BusinessLocation,
        location2: BusinessLocation
    ) -> Optional[float]:
        """
        Calculate distance between two locations in miles
        
        Args:
            location1: First location
            location2: Second location
            
        Returns:
            Distance in miles or None if coordinates missing
        """
        if not all([
            location1.latitude, location1.longitude,
            location2.latitude, location2.longitude
        ]):
            return None
        
        # Haversine formula
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1 = radians(location1.latitude), radians(location1.longitude)
        lat2, lon2 = radians(location2.latitude), radians(location2.longitude)
        
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        
        # Earth radius in miles
        radius_miles = 3959
        distance = radius_miles * c
        
        return distance
    
    def is_within_radius(
        self,
        location: BusinessLocation,
        center: BusinessLocation,
        radius_miles: float
    ) -> bool:
        """
        Check if location is within radius of center
        
        Args:
            location: Location to check
            center: Center point
            radius_miles: Radius in miles
            
        Returns:
            True if within radius, False otherwise
        """
        distance = self.calculate_distance(location, center)
        if distance is None:
            return False
        
        return distance <= radius_miles
