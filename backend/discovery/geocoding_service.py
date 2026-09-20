"""
Geocoding Service
-----------------
Convert location strings to geographic coordinates.

Supports:
  - Google Maps Geocoding API (primary)
  - OpenStreetMap Nominatim (free fallback)
  - Caching to minimize API calls
"""
import os
import logging
from typing import Optional, Tuple, Dict
import aiohttp
import json


logger = logging.getLogger(__name__)


class GeocodingService:
    """
    Convert location strings to coordinates using geocoding APIs.
    """
    
    GOOGLE_GEOCODING_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    
    def __init__(self):
        self.google_api_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self._cache: Dict[str, Tuple[float, float, float]] = {}  # location -> (lat, lng, confidence)
    
    async def geocode(
        self,
        location_string: str
    ) -> Tuple[Optional[float], Optional[float], float]:
        """
        Geocode a location string to coordinates.
        
        Args:
            location_string: Location to geocode (e.g., "London", "Ahmedabad, India")
        
        Returns:
            Tuple of (latitude, longitude, confidence_score)
            Returns (None, None, 0.0) if geocoding fails
        """
        if not location_string:
            return None, None, 0.0
        
        # Check cache
        cache_key = location_string.lower().strip()
        if cache_key in self._cache:
            logger.debug(f"Geocoding cache hit for: {location_string}")
            return self._cache[cache_key]
        
        # Try Google Maps API first (more accurate)
        if self.google_api_key:
            try:
                result = await self._geocode_google(location_string)
                if result[0] is not None:
                    self._cache[cache_key] = result
                    return result
            except Exception as e:
                logger.warning(f"Google geocoding failed for {location_string}: {e}")
        
        # Fallback to Nominatim (free, no API key required)
        try:
            result = await self._geocode_nominatim(location_string)
            if result[0] is not None:
                self._cache[cache_key] = result
                return result
        except Exception as e:
            logger.warning(f"Nominatim geocoding failed for {location_string}: {e}")
        
        logger.error(f"All geocoding methods failed for: {location_string}")
        return None, None, 0.0
    
    async def _geocode_google(
        self,
        location_string: str
    ) -> Tuple[Optional[float], Optional[float], float]:
        """
        Geocode using Google Maps Geocoding API.
        
        Returns:
            (latitude, longitude, confidence_score)
        """
        params = {
            "address": location_string,
            "key": self.google_api_key,
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.GOOGLE_GEOCODING_URL, params=params) as response:
                if response.status != 200:
                    logger.error(f"Google Geocoding API error: {response.status}")
                    return None, None, 0.0
                
                data = await response.json()
                
                if data.get("status") != "OK":
                    logger.warning(f"Google Geocoding status: {data.get('status')}")
                    return None, None, 0.0
                
                results = data.get("results", [])
                if not results:
                    return None, None, 0.0
                
                # Get first result (most relevant)
                location = results[0].get("geometry", {}).get("location", {})
                lat = location.get("lat")
                lng = location.get("lng")
                
                if lat is None or lng is None:
                    return None, None, 0.0
                
                # Determine confidence based on location type
                location_type = results[0].get("geometry", {}).get("location_type", "")
                confidence = self._calculate_google_confidence(location_type)
                
                logger.info(f"Google geocoded '{location_string}' to ({lat}, {lng}) with confidence {confidence}")
                return lat, lng, confidence
    
    async def _geocode_nominatim(
        self,
        location_string: str
    ) -> Tuple[Optional[float], Optional[float], float]:
        """
        Geocode using OpenStreetMap Nominatim API (free, no API key).
        
        Returns:
            (latitude, longitude, confidence_score)
        """
        params = {
            "q": location_string,
            "format": "json",
            "limit": 1,
        }
        
        headers = {
            "User-Agent": "B2B-Lead-Discovery/1.0"  # Required by Nominatim
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.NOMINATIM_URL, params=params, headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Nominatim API error: {response.status}")
                    return None, None, 0.0
                
                data = await response.json()
                
                if not data:
                    return None, None, 0.0
                
                # Get first result
                result = data[0]
                lat = float(result.get("lat", 0))
                lng = float(result.get("lon", 0))
                
                if lat == 0 and lng == 0:
                    return None, None, 0.0
                
                # Nominatim provides importance score
                importance = float(result.get("importance", 0.5))
                confidence = min(importance, 1.0) * 0.8  # Scale to 0-0.8 (lower than Google)
                
                logger.info(f"Nominatim geocoded '{location_string}' to ({lat}, {lng}) with confidence {confidence}")
                return lat, lng, confidence
    
    def _calculate_google_confidence(self, location_type: str) -> float:
        """
        Calculate confidence score based on Google's location_type.
        
        Google location types:
          - ROOFTOP: Most precise (address-level)
          - RANGE_INTERPOLATED: Interpolated between two points
          - GEOMETRIC_CENTER: Center of a location (street, city, etc.)
          - APPROXIMATE: Approximate location (city/region level)
        """
        confidence_map = {
            "ROOFTOP": 1.0,
            "RANGE_INTERPOLATED": 0.9,
            "GEOMETRIC_CENTER": 0.85,
            "APPROXIMATE": 0.75,
        }
        return confidence_map.get(location_type, 0.7)
    
    def normalize_location_string(self, location_string: str) -> str:
        """
        Normalize location string for consistency.
        
        Args:
            location_string: Raw location string
        
        Returns:
            Normalized location string
        """
        # Remove extra whitespace
        normalized = " ".join(location_string.split())
        
        # Capitalize properly
        normalized = normalized.title()
        
        return normalized
    
    async def reverse_geocode(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[str]:
        """
        Reverse geocode coordinates to a location string.
        
        Args:
            latitude: Latitude
            longitude: Longitude
        
        Returns:
            Location string (e.g., "London, UK") or None
        """
        if not self.google_api_key:
            logger.warning("Reverse geocoding requires Google Maps API key")
            return None
        
        params = {
            "latlng": f"{latitude},{longitude}",
            "key": self.google_api_key,
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.GOOGLE_GEOCODING_URL, params=params) as response:
                if response.status != 200:
                    return None
                
                data = await response.json()
                
                if data.get("status") != "OK":
                    return None
                
                results = data.get("results", [])
                if not results:
                    return None
                
                # Get formatted address
                return results[0].get("formatted_address")
    
    def clear_cache(self):
        """Clear the geocoding cache"""
        self._cache.clear()
        logger.info("Geocoding cache cleared")


# Convenience functions
_service = None

def get_geocoding_service() -> GeocodingService:
    """Get or create the singleton geocoding service"""
    global _service
    if _service is None:
        _service = GeocodingService()
    return _service


async def geocode(location_string: str) -> Tuple[Optional[float], Optional[float], float]:
    """
    Quick geocoding function.
    
    Args:
        location_string: Location to geocode
    
    Returns:
        (latitude, longitude, confidence)
    """
    service = get_geocoding_service()
    return await service.geocode(location_string)
