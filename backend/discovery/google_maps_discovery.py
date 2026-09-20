"""
Google Maps Business Discovery
-------------------------------
Primary discovery source for location-aware lead generation.

Uses:
  - Google Maps Places API (preferred)
  - SerpApi Google Maps engine (alternative)

Features:
  - Extract full business data including coordinates
  - Apply location + radius constraints
  - Calculate distances from search center
  - Return structured Business objects
"""
import os
import logging
from typing import List, Optional, Tuple
import aiohttp

from models.business import Business, BusinessLocation, BusinessContact, BusinessStatus
from models.location_intent import LocationIntent
from discovery.distance_calculator import DistanceCalculator


logger = logging.getLogger(__name__)


class GoogleMapsDiscovery:
    """
    Discover businesses from Google Maps with location awareness.
    """
    
    GOOGLE_PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
    SERPAPI_URL = "https://serpapi.com/search.json"
    
    def __init__(self):
        self.google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_API_KEY")
        self.serpapi_key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERP_API_KEY")
    
    @property
    def is_configured(self) -> bool:
        """Check if any API is configured"""
        return bool(self.google_maps_key or self.serpapi_key)
    
    @property
    def provider_name(self) -> str:
        """Get the active provider name"""
        if self.google_maps_key:
            return "Google Places API"
        elif self.serpapi_key:
            return "SerpApi (Google Maps)"
        return "None"
    
    async def discover_businesses(
        self,
        query: str,
        location_intent: LocationIntent,
        max_results: int = 50
    ) -> List[Business]:
        """
        Discover businesses from Google Maps.
        
        Args:
            query: Search query (e.g., "restaurants", "dental clinics")
            location_intent: Location constraints
            max_results: Maximum number of results
        
        Returns:
            List of Business objects with location data
        """
        if not self.is_configured:
            logger.error("No Google Maps API configured. Set GOOGLE_MAPS_API_KEY or SERPAPI_API_KEY")
            return []
        
        # Build location-aware query
        full_query = self._build_query(query, location_intent)
        logger.info(f"Discovering businesses: '{full_query}' via {self.provider_name}")
        
        # Call appropriate API
        if self.google_maps_key:
            businesses = await self._discover_via_google_places(full_query, location_intent, max_results)
        else:
            businesses = await self._discover_via_serpapi(full_query, location_intent, max_results)
        
        # Calculate distances if we have search center coordinates
        if location_intent.search_center_coords and businesses:
            self._add_distances(businesses, location_intent.search_center_coords)
        
        # Filter by radius if specified
        if location_intent.has_radius_constraint:
            businesses = self._filter_by_radius(businesses, location_intent.radius_km)
        
        logger.info(f"Discovered {len(businesses)} businesses within constraints")
        return businesses
    
    def _build_query(self, query: str, location_intent: LocationIntent) -> str:
        """
        Build location-aware search query.
        
        Args:
            query: Base query (e.g., "restaurants")
            location_intent: Location constraints
        
        Returns:
            Full query string (e.g., "restaurants in London")
        """
        if location_intent.search_center and location_intent.search_center != "user_current_location":
            return f"{query} in {location_intent.search_center}"
        return query
    
    async def _discover_via_google_places(
        self,
        query: str,
        location_intent: LocationIntent,
        max_results: int
    ) -> List[Business]:
        """
        Discover businesses using Google Places API.
        """
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.google_maps_key,
            "X-Goog-FieldMask": (
                "places.id,"
                "places.displayName,"
                "places.formattedAddress,"
                "places.location,"
                "places.websiteUri,"
                "places.nationalPhoneNumber,"
                "places.internationalPhoneNumber,"
                "places.types,"
                "places.googleMapsUri,"
                "places.rating,"
                "places.userRatingCount,"
                "places.businessStatus"
            ),
        }
        
        payload = {
            "textQuery": query,
            "pageSize": min(max_results, 20),  # Google Places max is 20
        }
        
        # Add location bias if we have coordinates
        if location_intent.search_center_coords:
            lat, lng = location_intent.search_center_coords
            payload["locationBias"] = {
                "circle": {
                    "center": {"latitude": lat, "longitude": lng},
                    "radius": (location_intent.radius_km * 1000) if location_intent.radius_km else 50000  # meters
                }
            }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(self.GOOGLE_PLACES_URL, headers=headers, json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Google Places API error {response.status}: {error_text}")
                    return []
                
                data = await response.json()
                places = data.get("places", [])
                
                if not places:
                    logger.warning(f"No places found for query: {query}")
                    return []
                
                logger.info(f"Google Places returned {len(places)} results")
                return self._parse_google_places_results(places)
    
    async def _discover_via_serpapi(
        self,
        query: str,
        location_intent: LocationIntent,
        max_results: int
    ) -> List[Business]:
        """
        Discover businesses using SerpApi Google Maps engine.
        """
        params = {
            "engine": "google_maps",
            "q": query,
            "api_key": self.serpapi_key,
        }
        
        # Add location parameter if available
        if location_intent.search_center and location_intent.search_center != "user_current_location":
            params["ll"] = f"@{location_intent.search_center}"
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.SERPAPI_URL, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"SerpApi error {response.status}: {error_text}")
                    return []
                
                data = await response.json(content_type=None)
                
                if "error" in data:
                    logger.error(f"SerpApi error: {data['error']}")
                    return []
                
                local_results = data.get("local_results", [])
                
                if not local_results:
                    logger.warning(f"No local results found for query: {query}")
                    return []
                
                logger.info(f"SerpApi returned {len(local_results)} results")
                return self._parse_serpapi_results(local_results[:max_results])
    
    def _parse_google_places_results(self, places: List[dict]) -> List[Business]:
        """Parse Google Places API results into Business objects"""
        businesses = []
        
        for place in places:
            try:
                # Extract location data
                location_data = place.get("location", {})
                lat = location_data.get("latitude")
                lng = location_data.get("longitude")
                
                # Parse address components
                address = place.get("formattedAddress", "")
                address_parts = self._parse_address(address)
                
                location = BusinessLocation(
                    address=address,
                    city=address_parts.get("city"),
                    state=address_parts.get("state"),
                    country=address_parts.get("country"),
                    postal_code=address_parts.get("postal_code"),
                    latitude=lat,
                    longitude=lng,
                    is_primary=True,
                )
                
                # Extract contact data
                contact = BusinessContact(
                    website=place.get("websiteUri"),
                    phone=place.get("nationalPhoneNumber") or place.get("internationalPhoneNumber"),
                )
                
                # Extract business data
                business = Business(
                    id=place.get("id"),
                    name=place.get("displayName", {}).get("text", "Unknown Business"),
                    industry=", ".join(place.get("types", [])[:3]),
                    contact=contact,
                    locations=[location],
                    source="google_places",
                    source_id=place.get("id"),
                    status=BusinessStatus.DISCOVERED,
                    custom_data={
                        "google_maps_url": place.get("googleMapsUri"),
                        "rating": place.get("rating"),
                        "rating_count": place.get("userRatingCount"),
                        "business_status": place.get("businessStatus"),
                    }
                )
                
                businesses.append(business)
                
            except Exception as e:
                logger.error(f"Error parsing Google Places result: {e}")
                continue
        
        return businesses
    
    def _parse_serpapi_results(self, results: List[dict]) -> List[Business]:
        """Parse SerpApi results into Business objects"""
        businesses = []
        
        for item in results:
            try:
                # Extract location data
                gps_coords = item.get("gps_coordinates", {})
                lat = gps_coords.get("latitude")
                lng = gps_coords.get("longitude")
                
                address = item.get("address", "")
                address_parts = self._parse_address(address)
                
                location = BusinessLocation(
                    address=address,
                    city=address_parts.get("city"),
                    state=address_parts.get("state"),
                    country=address_parts.get("country"),
                    postal_code=address_parts.get("postal_code"),
                    latitude=lat,
                    longitude=lng,
                    is_primary=True,
                )
                
                # Extract contact data
                website = item.get("website") or item.get("links", {}).get("website")
                contact = BusinessContact(
                    website=website,
                    phone=item.get("phone"),
                )
                
                # Extract business data
                business = Business(
                    id=item.get("place_id"),
                    name=item.get("title", "Unknown Business"),
                    description=item.get("description"),
                    industry=item.get("type", ""),
                    contact=contact,
                    locations=[location],
                    source="serpapi_google_maps",
                    source_id=item.get("place_id"),
                    status=BusinessStatus.DISCOVERED,
                    custom_data={
                        "google_maps_url": item.get("link"),
                        "rating": item.get("rating"),
                        "reviews": item.get("reviews"),
                    }
                )
                
                businesses.append(business)
                
            except Exception as e:
                logger.error(f"Error parsing SerpApi result: {e}")
                continue
        
        return businesses
    
    def _parse_address(self, address: str) -> dict:
        """Parse address string into components"""
        # Simple heuristic parsing
        # In production, use a proper address parsing library
        parts = {}
        
        if not address:
            return parts
        
        # Split by comma
        components = [c.strip() for c in address.split(",")]
        
        if len(components) >= 2:
            # Last component often contains state/country
            parts["state"] = components[-2] if len(components) >= 2 else None
            parts["country"] = components[-1]
        
        if len(components) >= 3:
            parts["city"] = components[-3]
        
        # Try to extract postal code
        import re
        postal_match = re.search(r'\b\d{5,6}\b', address)
        if postal_match:
            parts["postal_code"] = postal_match.group()
        
        return parts
    
    def _add_distances(
        self,
        businesses: List[Business],
        center_coords: Tuple[float, float]
    ) -> None:
        """Add distance_km to each business location"""
        calculator = DistanceCalculator(center_coords)
        
        for business in businesses:
            if business.locations and business.locations[0].latitude and business.locations[0].longitude:
                distance = calculator.calculate_distance(
                    business.locations[0].latitude,
                    business.locations[0].longitude
                )
                business.locations[0].distance_km = distance
    
    def _filter_by_radius(
        self,
        businesses: List[Business],
        radius_km: float
    ) -> List[Business]:
        """Filter businesses by radius"""
        filtered = [
            b for b in businesses
            if b.locations and b.locations[0].distance_km is not None
            and b.locations[0].distance_km <= radius_km
        ]
        
        # Sort by distance (nearest first)
        filtered.sort(key=lambda b: b.locations[0].distance_km or float('inf'))
        
        logger.info(f"Filtered to {len(filtered)}/{len(businesses)} businesses within {radius_km}km")
        return filtered
