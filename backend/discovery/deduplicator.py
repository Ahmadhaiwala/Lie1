"""
Deduplicator
Identifies and merges duplicate business records
"""
from typing import List, Set, Dict, Tuple, Optional
import hashlib
from difflib import SequenceMatcher

from models.business import Business


class Deduplicator:
    """Identifies and merges duplicate business records"""
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize deduplicator
        
        Args:
            similarity_threshold: Minimum similarity score to consider duplicates (0-1)
        """
        self.similarity_threshold = similarity_threshold
        self._seen_hashes: Set[str] = set()
    
    async def deduplicate(
        self,
        businesses: List[Business]
    ) -> List[Business]:
        """
        Deduplicate a list of businesses
        
        Args:
            businesses: List of businesses to deduplicate
            
        Returns:
            Deduplicated list of businesses
        """
        if not businesses:
            return []
        
        # First pass: exact duplicates using hash
        unique_businesses = self._remove_exact_duplicates(businesses)
        
        # Second pass: fuzzy matching
        final_businesses = await self._remove_fuzzy_duplicates(unique_businesses)
        
        return final_businesses
    
    def _remove_exact_duplicates(
        self,
        businesses: List[Business]
    ) -> List[Business]:
        """
        Remove exact duplicates using hash comparison
        
        Args:
            businesses: List of businesses
            
        Returns:
            List without exact duplicates
        """
        unique = []
        seen_hashes = set()
        
        for business in businesses:
            biz_hash = self._generate_business_hash(business)
            
            if biz_hash not in seen_hashes:
                seen_hashes.add(biz_hash)
                unique.append(business)
            else:
                # Mark as duplicate
                business.is_duplicate = True
        
        return unique
    
    async def _remove_fuzzy_duplicates(
        self,
        businesses: List[Business]
    ) -> List[Business]:
        """
        Remove fuzzy duplicates using similarity matching
        
        Args:
            businesses: List of businesses
            
        Returns:
            List without fuzzy duplicates
        """
        if len(businesses) <= 1:
            return businesses
        
        # Build similarity matrix
        n = len(businesses)
        duplicates_map: Dict[int, int] = {}  # Maps index to canonical index
        
        for i in range(n):
            if i in duplicates_map:
                continue
            
            for j in range(i + 1, n):
                if j in duplicates_map:
                    continue
                
                similarity = self.calculate_similarity(
                    businesses[i],
                    businesses[j]
                )
                
                if similarity >= self.similarity_threshold:
                    # Mark j as duplicate of i
                    duplicates_map[j] = i
                    businesses[j].is_duplicate = True
                    businesses[j].duplicate_of = businesses[i].id
        
        # Keep only non-duplicates
        unique = [
            business for idx, business in enumerate(businesses)
            if idx not in duplicates_map
        ]
        
        return unique
    
    def calculate_similarity(
        self,
        business1: Business,
        business2: Business
    ) -> float:
        """
        Calculate similarity score between two businesses
        
        Args:
            business1: First business
            business2: Second business
            
        Returns:
            Similarity score (0-1)
        """
        scores = []
        weights = []
        
        # Name similarity (high weight)
        name_sim = self._string_similarity(
            business1.name.lower(),
            business2.name.lower()
        )
        scores.append(name_sim)
        weights.append(0.5)
        
        # Website similarity (if both have websites)
        if business1.contact.website and business2.contact.website:
            website_sim = 1.0 if str(business1.contact.website).lower() == str(business2.contact.website).lower() else 0.0
            scores.append(website_sim)
            weights.append(0.3)
        
        # Phone similarity (if both have phones)
        if business1.contact.phone and business2.contact.phone:
            phone1 = self._normalize_phone(business1.contact.phone)
            phone2 = self._normalize_phone(business2.contact.phone)
            phone_sim = 1.0 if phone1 == phone2 else 0.0
            scores.append(phone_sim)
            weights.append(0.3)
        
        # Email similarity (if both have emails)
        if business1.contact.email and business2.contact.email:
            email_sim = 1.0 if business1.contact.email.lower() == business2.contact.email.lower() else 0.0
            scores.append(email_sim)
            weights.append(0.3)
        
        # Location similarity
        if business1.locations and business2.locations:
            loc1 = business1.locations[0]
            loc2 = business2.locations[0]
            
            loc_sim = self._location_similarity(loc1, loc2)
            scores.append(loc_sim)
            weights.append(0.2)
        
        # Weighted average
        if not scores:
            return 0.0
        
        total_weight = sum(weights[:len(scores)])
        weighted_sum = sum(s * w for s, w in zip(scores, weights[:len(scores)]))
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def _location_similarity(self, loc1, loc2) -> float:
        """Calculate location similarity"""
        score = 0.0
        count = 0
        
        if loc1.city and loc2.city:
            score += 1.0 if loc1.city.lower() == loc2.city.lower() else 0.0
            count += 1
        
        if loc1.state and loc2.state:
            score += 1.0 if loc1.state.lower() == loc2.state.lower() else 0.0
            count += 1
        
        if loc1.postal_code and loc2.postal_code:
            score += 1.0 if loc1.postal_code == loc2.postal_code else 0.0
            count += 1
        
        return score / count if count > 0 else 0.0
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalize phone number for comparison"""
        # Remove all non-digit characters
        import re
        digits = re.sub(r'\D', '', phone)
        
        # Take last 10 digits (US phone numbers)
        return digits[-10:] if len(digits) >= 10 else digits
    
    def _generate_business_hash(self, business: Business) -> str:
        """
        Generate hash for exact duplicate detection
        
        Args:
            business: Business to hash
            
        Returns:
            Hash string
        """
        # Combine key fields
        parts = [
            business.name.lower().strip(),
            str(business.contact.website or '').lower(),
            business.contact.phone or '',
            business.contact.email or '',
        ]
        
        # Add location if available
        if business.locations:
            loc = business.locations[0]
            parts.extend([
                loc.city or '',
                loc.state or '',
                loc.postal_code or '',
            ])
        
        # Create hash
        combined = '|'.join(parts)
        return hashlib.md5(combined.encode()).hexdigest()
    
    def merge_businesses(
        self,
        primary: Business,
        duplicate: Business
    ) -> Business:
        """
        Merge duplicate business into primary
        
        Args:
            primary: Primary business to keep
            duplicate: Duplicate business to merge in
            
        Returns:
            Merged business
        """
        # Merge contacts
        if not primary.contact.email and duplicate.contact.email:
            primary.contact.email = duplicate.contact.email
        
        if not primary.contact.phone and duplicate.contact.phone:
            primary.contact.phone = duplicate.contact.phone
        
        if not primary.contact.website and duplicate.contact.website:
            primary.contact.website = duplicate.contact.website
        
        # Merge social media
        for platform, url in duplicate.contact.social_media.items():
            if platform not in primary.contact.social_media:
                primary.contact.social_media[platform] = url
        
        # Merge locations (avoid duplicates)
        for loc in duplicate.locations:
            if not any(self._location_similarity(loc, pl) > 0.9 for pl in primary.locations):
                loc.is_primary = False
                primary.locations.append(loc)
        
        # Merge technologies
        for tech in duplicate.technologies:
            if tech not in primary.technologies:
                primary.technologies.append(tech)
        
        # Merge custom data
        for key, value in duplicate.custom_data.items():
            if key not in primary.custom_data:
                primary.custom_data[key] = value
        
        return primary
