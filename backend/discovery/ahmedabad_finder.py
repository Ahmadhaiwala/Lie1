"""
Ahmedabad Business Finder
Find real businesses in Ahmedabad with contact information
"""
import logging
from typing import List, Dict, Any
import aiohttp

logger = logging.getLogger(__name__)


class AhmedabadBusinessFinder:
    """Specialized finder for Ahmedabad businesses using Google Places API"""
    
    GOOGLE_PLACES_URL = "https://places.googleapis.com/v1/places:searchText"
    
    def __init__(self, google_maps_key: str):
        self.google_maps_key = google_maps_key
    
    async def find_businesses_by_category(self, category: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Find businesses in Ahmedabad by category
        
        Categories:
        - restaurants
        - shops
        - services (salons, gyms, clinics)
        - hotels
        - educational
        - retail
        """
        query = f"{category} in Ahmedabad"
        
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.google_maps_key,
            "X-Goog-FieldMask": "places.id,places.displayName,places.formattedAddress,places.websiteUri,places.nationalPhoneNumber,places.types,places.googleMapsUri,places.rating,places.businessStatus",
        }
        
        try:
            timeout = aiohttp.ClientTimeout(total=30)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.GOOGLE_PLACES_URL,
                    headers=headers,
                    json={"textQuery": query, "pageSize": limit}
                ) as response:
                    data = await response.json(content_type=None)
                    if response.status >= 400:
                        logger.error(f"Google Places API error: {response.status}")
                        return []
            
            businesses = []
            for place in data.get("places", []):
                # Only include operational businesses in Ahmedabad
                if place.get("businessStatus") != "OPERATIONAL":
                    continue
                
                address = place.get("formattedAddress", "")
                if "Ahmedabad" not in address and "Gujarat" not in address:
                    continue
                
                business = {
                    "name": place.get("displayName", {}).get("text", "Unknown"),
                    "phone": place.get("nationalPhoneNumber", ""),
                    "website": place.get("websiteUri", ""),
                    "address": address,
                    "maps_url": place.get("googleMapsUri", ""),
                    "rating": place.get("rating", 0),
                    "types": place.get("types", []),
                    "place_id": place.get("id", ""),
                }
                
                businesses.append(business)
            
            logger.info(f"Found {len(businesses)} businesses for '{category}' in Ahmedabad")
            return businesses
        
        except Exception as e:
            logger.error(f"Error finding businesses: {e}")
            return []
    
    async def find_all_ahmedabad_businesses(self) -> List[Dict[str, Any]]:
        """Find all types of businesses in Ahmedabad"""
        
        categories = [
            "restaurants",
            "cafes",
            "hotels",
            "shops",
            "retail stores",
            "clothing stores",
            "pharmacies",
            "gyms",
            "salons",
            "clinics",
            "hospitals",
            "schools",
            "coaching centers",
            "printing press",
            "automobile service",
            "plumber",
            "electrician",
            "real estate",
            "travel agency",
            "beauty parlor",
        ]
        
        all_businesses = []
        
        for category in categories:
            logger.info(f"Searching for {category} in Ahmedabad...")
            businesses = await self.find_businesses_by_category(category, limit=10)
            all_businesses.extend(businesses)
            
            # Remove duplicates by place_id
            seen_ids = set()
            unique_businesses = []
            for b in all_businesses:
                pid = b.get("place_id")
                if pid and pid not in seen_ids:
                    seen_ids.add(pid)
                    unique_businesses.append(b)
            
            all_businesses = unique_businesses
        
        logger.info(f"Total unique businesses found in Ahmedabad: {len(all_businesses)}")
        return all_businesses
