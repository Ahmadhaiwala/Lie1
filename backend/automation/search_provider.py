"""API-backed business search providers used by lead-generation jobs."""

import os
from typing import Dict, List

import aiohttp


class SearchProvider:
    """Search without a browser, preferring SerpApi over Google Places."""

    SERPAPI_URL = "https://serpapi.com/search.json"
    GOOGLE_PLACES_URL = "https://places.googleapis.com/v1/places:searchText"

    def __init__(self) -> None:
        self.serpapi_key = os.getenv("SERPAPI_API_KEY") or os.getenv("SERP_API_KEY")
        self.google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("GOOGLE_API_KEY")

    @property
    def configured(self) -> bool:
        return bool(self.serpapi_key or self.google_maps_key)

    @property
    def name(self) -> str:
        if self.serpapi_key:
            return "SerpApi"
        if self.google_maps_key:
            return "Google Places API"
        return "unconfigured"

    async def search(self, query: str, limit: int) -> List[Dict[str, str]]:
        if self.serpapi_key:
            return await self._search_serpapi(query, limit)
        if self.google_maps_key:
            return await self._search_google_places(query, limit)
        raise RuntimeError("No API-backed search provider is configured")

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

    async def _search_google_places(self, query: str, limit: int) -> List[Dict[str, str]]:
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.google_maps_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.types,places.googleMapsUri,places.rating",
        }
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post(self.GOOGLE_PLACES_URL, headers=headers, json={"textQuery": query, "pageSize": limit}) as response:
                data = await response.json(content_type=None)
                if response.status >= 400:
                    message = data.get("error", {}).get("message", response.reason)
                    raise RuntimeError(f"Google Places request failed ({response.status}): {message}")

        results: List[Dict[str, str]] = []
        for place in data.get("places", [])[:limit]:
            url = place.get("websiteUri") or place.get("googleMapsUri")
            if not url:
                continue
            name = place.get("displayName", {}).get("text", "")
            content = "\n".join(str(value) for value in (name, place.get("formattedAddress", ""), place.get("nationalPhoneNumber", ""), ", ".join(place.get("types", [])), f"Rating: {place['rating']}" if place.get("rating") else "") if value)
            results.append({"url": url, "content": content})
        return results
