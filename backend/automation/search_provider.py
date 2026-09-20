"""API-backed business search providers used by lead-generation jobs."""

import os
from typing import Dict, List

import aiohttp


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
        params = {"engine": "google", "q": query, "num": str(limit), "api_key": self.serpapi_key}
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(self.SERPAPI_URL, params=params) as response:
                data = await response.json(content_type=None)
                if response.status >= 400:
                    message = data.get("error", response.reason) if isinstance(data, dict) else response.reason
                    raise RuntimeError(f"SerpApi request failed ({response.status}): {message}")

        results: List[Dict[str, str]] = []
        for item in data.get("organic_results", [])[:limit]:
            url = item.get("link")
            if url:
                results.append({"url": url, "content": f"{item.get('title', '')}\n{item.get('snippet', '')}".strip()})
        return results

