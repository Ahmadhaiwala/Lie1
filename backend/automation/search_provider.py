"""API-backed business search providers used by lead-generation jobs."""

import os
import re
from html import unescape
from typing import Dict, List

import aiohttp
from location_config import (
    get_default_location_coords,
    get_default_location_name,
    get_default_search_radius
)


class SearchProvider:
    """Search without a browser, using SerpApi and Google Maps API for business data."""

    SERPAPI_URL = "https://serpapi.com/search.json"
    GOOGLE_PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
    GOOGLE_PLACE_DETAILS_URL = "https://places.googleapis.com/v1/places"

    def __init__(self) -> None:
        self.serpapi_key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERP_API_KEY")
        self.google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_API_KEY")

    @property
    def configured(self) -> bool:
        return bool(self.serpapi_key or self.google_maps_key)

    @property
    def name(self) -> str:
        if self.google_maps_key:
            return "Google Places API (with contact data)"
        if self.serpapi_key:
            return "SerpApi"
        return "unconfigured"

    async def search(self, query: str, limit: int) -> List[Dict[str, str]]:
        """Search for businesses with contact info"""
        if self.google_maps_key:
            return await self._search_google_places_with_details(query, limit)
        if self.serpapi_key:
            return await self._search_serpapi(query, limit)
        raise RuntimeError("No API-backed search provider is configured")

    async def _search_google_places_with_details(self, query: str, limit: int) -> List[Dict[str, str]]:
        """Search Google Places and fetch detailed contact info for each result"""
        # First, search for places
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.google_maps_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.googleMapsUri,places.rating,places.businessStatus",
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(
                self.GOOGLE_PLACES_URL,
                headers=headers,
                json={"textQuery": query, "pageSize": limit}
            ) as response:
                data = await response.json(content_type=None)
                if response.status >= 400:
                    message = data.get("error", {}).get("message", response.reason)
                    raise RuntimeError(f"Google Places search failed ({response.status}): {message}")

        results: List[Dict[str, str]] = []
        for place in data.get("places", [])[:limit]:
            place_id = place.get("id", "")
            name = place.get("displayName", {}).get("text", "")
            phone = place.get("nationalPhoneNumber", "")
            website = place.get("websiteUri", "")
            address = place.get("formattedAddress", "")
            maps_url = place.get("googleMapsUri", "")
            rating = place.get("rating", 0)
            status = place.get("businessStatus", "")
            
            # Get detailed information if we have place_id
            email = ""
            if place_id and not phone:
                email = await self._get_place_email(place_id, session)
            
            if phone or email or website:
                result = {
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "website": website or maps_url,
                    "address": address,
                    "rating": str(rating) if rating else "N/A",
                    "status": status,
                    "type": "google_places",
                    "content": f"{name}\n{address}\nPhone: {phone}\nWebsite: {website}\nRating: {rating}"
                }
                results.append(result)
        
        return results

    async def _get_place_email(self, place_id: str, session: aiohttp.ClientSession) -> str:
        """Fetch email from place details"""
        try:
            headers = {
                "X-Goog-Api-Key": self.google_maps_key,
                "X-Goog-FieldMask": "displayName,formattedAddress,nationalPhoneNumber,internationalPhoneNumber,websiteUri,emailAddress",
            }
            
            async with session.get(
                f"{self.GOOGLE_PLACE_DETAILS_URL}/{place_id}",
                headers=headers
            ) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                    return data.get("emailAddress", "")
        except Exception:
            pass
        return ""

    async def _search_serpapi(self, query: str, limit: int) -> List[Dict[str, str]]:
        # Google Maps produces named business entities, unlike general web
        # search which is dominated by articles, tutorials, and discussions.
        
        # Get configured location
        location_name = get_default_location_name()
        lat, lng = get_default_location_coords()
        
        location_query = f"{query} in {location_name}"
        
        params = {
            "engine": "google_maps", 
            "q": location_query,
            "ll": f"@{lat},{lng},14z",  # Location coordinates with zoom
            "api_key": self.serpapi_key
        }
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.SERPAPI_URL, params=params) as response:
                data = await response.json(content_type=None)
                if response.status >= 400:
                    message = data.get("error", response.reason) if isinstance(data, dict) else response.reason
                    raise RuntimeError(f"SerpApi request failed ({response.status}): {message}")

        results: List[Dict[str, str]] = []
        for item in data.get("local_results", [])[:limit]:
            name = item.get("title", "").strip()
            website = item.get("website") or item.get("links", {}).get("website")
            source_url = item.get("link") or item.get("links", {}).get("website") or website
            if not name or not source_url:
                continue
            location = item.get("address", "")
            industry = item.get("type", "")
            phone = item.get("phone", "")
            
            # Extract coordinates
            gps = item.get("gps_coordinates", {})
            lat = gps.get("latitude")
            lng = gps.get("longitude")
            
            # Calculate distance from configured location center
            distance_km = None
            if lat and lng:
                from discovery.distance_calculator import calculate_distance_km
                center_lat, center_lng = get_default_location_coords()
                distance_km = calculate_distance_km(center_lat, center_lng, lat, lng)
            
            # Build location string with coordinates
            location_info = location
            if lat and lng:
                location_info += f" [Coordinates: {lat:.4f}, {lng:.4f}]"
            if distance_km is not None:
                location_info += f" [Distance: {distance_km:.1f}km from center]"
            
            content = "\n".join(value for value in (name, location, industry, phone, item.get("description", ""), f"Distance: {distance_km:.1f}km" if distance_km else "") if value)
            results.append({
                "url": source_url,
                "website": website or "",
                "business_name": name,
                "location": location_info,
                "industry": industry,
                "phone": phone,
                "content": content,
                "latitude": lat,
                "longitude": lng,
                "distance_km": distance_km,
            })
        
        # Sort by distance (nearest first)
        if any(r.get("distance_km") is not None for r in results):
            results.sort(key=lambda x: x.get("distance_km") or float('inf'))
        
        return results

    async def _search_google_places(self, query: str, limit: int) -> List[Dict[str, str]]:
        # Get configured location
        location_name = get_default_location_name()
        center_lat, center_lng = get_default_location_coords()
        radius_meters = int(get_default_search_radius() * 1000)  # Convert km to meters
        
        location_query = f"{query} in {location_name}"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.google_maps_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.types,places.googleMapsUri,places.rating,places.location",
        }
        
        # Add location bias to configured location
        payload = {
            "textQuery": location_query,
            "pageSize": limit,
            "locationBias": {
                "circle": {
                    "center": {
                        "latitude": center_lat,
                        "longitude": center_lng
                    },
                    "radius": radius_meters
                }
            }
        }
        
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(self.GOOGLE_PLACES_URL, headers=headers, json=payload) as response:
                data = await response.json(content_type=None)
                if response.status >= 400:
                    message = data.get("error", {}).get("message", response.reason)
                    raise RuntimeError(f"Google Places request failed ({response.status}): {message}")

        results: List[Dict[str, str]] = []
        for place in data.get("places", [])[:limit]:
            name = place.get("displayName", {}).get("text", "")
            
            # Skip if no business name
            if not name:
                logger.warning("Skipping Google Places result with no business name")
                continue
            
            # Website is OPTIONAL - missing website should NOT discard the lead
            website = place.get("websiteUri", "")
            google_maps_url = place.get("googleMapsUri", "")
            
            # Use Google Maps URL as fallback for source_url
            url = website or google_maps_url or ""
            
            # Extract coordinates
            location_data = place.get("location", {})
            lat = location_data.get("latitude")
            lng = location_data.get("longitude")
            
            # Calculate distance from configured location center
            distance_km = None
            if lat and lng:
                from discovery.distance_calculator import calculate_distance_km
                center_lat, center_lng = get_default_location_coords()
                distance_km = calculate_distance_km(center_lat, center_lng, lat, lng)
            
            # Build location string with coordinates
            address = place.get("formattedAddress", "")
            location_info = address
            if lat and lng:
                location_info += f" [Coordinates: {lat:.4f}, {lng:.4f}]"
            if distance_km is not None:
                location_info += f" [Distance: {distance_km:.1f}km from center]"
            
            # Get phone number
            phone = place.get("nationalPhoneNumber", "")
            
            # Get rating info
            rating = place.get("rating")
            
            # Build content string for qualification
            content_parts = [
                name,
                address,
                phone,
                ", ".join(place.get("types", [])),
            ]
            if rating:
                content_parts.append(f"Rating: {rating}")
            if distance_km:
                content_parts.append(f"Distance: {distance_km:.1f}km")
            
            content = "\n".join(str(value) for value in content_parts if value)
            
            # Build result dict - url/website can be empty
            result = {
                "url": url,  # May be empty string
                "website": website,  # May be empty string
                "google_maps_url": google_maps_url,
                "business_name": name,
                "location": location_info,
                "address": address,
                "industry": ", ".join(place.get("types", [])),
                "phone": phone,
                "rating": rating,
                "content": content,
                "latitude": lat,
                "longitude": lng,
                "distance_km": distance_km,
            }
            
            results.append(result)
            
            logger.debug(
                "Google Places result: %s | Website: %s | Phone: %s | Distance: %.1fkm",
                name,
                website or "None",
                phone or "None",
                distance_km if distance_km else 0,
            )
        
        # Sort by distance (nearest first)
        if any(r.get("distance_km") is not None for r in results):
            results.sort(key=lambda x: x.get("distance_km") or float('inf'))
        
        return results

    async def fetch_website_text(self, url: str) -> str:
        """Fetch public page text for evidence without launching a browser."""
        if not url.startswith(("https://", "http://")):
            return ""
        timeout = aiohttp.ClientTimeout(total=20)
        headers = {"User-Agent": "LeadBotResearch/1.0 (+business research)"}
        try:
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url, allow_redirects=True) as response:
                    if response.status >= 400 or "html" not in response.headers.get("Content-Type", ""):
                        return ""
                    html = await response.content.read(750_000)
        except (aiohttp.ClientError, TimeoutError):
            return ""

        text = html.decode("utf-8", errors="ignore")
        text = re.sub(r"<(script|style|noscript)[^>]*>.*?</\\1>", " ", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<[^>]+>", " ", text)
        return re.sub(r"\\s+", " ", unescape(text)).strip()[:12_000]
