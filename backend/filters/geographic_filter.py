"""
Geographic Filter
-----------------
Filter leads by geographic constraints BEFORE qualification.

Purpose:
  Apply location/radius filters early in the pipeline to avoid
  wasting LLM tokens on businesses outside the target area.
"""
import logging
from typing import List, Optional, Tuple
from dataclasses import dataclass

from models.location_intent import LocationIntent
from discovery.distance_calculator import calculate_distance_km, DistanceCalculator


logger = logging.getLogger(__name__)


@dataclass
class GeographicFilterResult:
    """Result of geographic filtering"""
    total_input: int
    missing_coordinates: int
    within_radius: int
    outside_radius: int
    filtered_leads: List  # List of leads that passed the filter


class GeographicFilter:
    """
    Filter businesses/leads by geographic constraints.
    
    Usage:
        filter = GeographicFilter(location_intent)
        result = filter.filter_leads(leads)
    """
    
    def __init__(self, location_intent: LocationIntent):
        """
        Initialize geographic filter.
        
        Args:
            location_intent: Location constraints to apply
        """
        self.location_intent = location_intent
        self.calculator = None
        
        if location_intent.search_center_coords:
            self.calculator = DistanceCalculator(location_intent.search_center_coords)
    
    def filter_leads(self, leads: List) -> GeographicFilterResult:
        """
        Filter leads by geographic constraints.
        
        Args:
            leads: List of Lead objects with location data
        
        Returns:
            GeographicFilterResult with filtered leads and statistics
        """
        if self.location_intent.is_missing:
            # No geographic constraints, return all leads
            logger.info("No geographic constraints, returning all leads")
            return GeographicFilterResult(
                total_input=len(leads),
                missing_coordinates=0,
                within_radius=len(leads),
                outside_radius=0,
                filtered_leads=leads,
            )
        
        if not self.location_intent.has_radius_constraint:
            # Has location but no radius constraint, just calculate distances
            logger.info(f"No radius constraint, calculating distances only")
            self._calculate_distances(leads)
            return GeographicFilterResult(
                total_input=len(leads),
                missing_coordinates=0,
                within_radius=len(leads),
                outside_radius=0,
                filtered_leads=leads,
            )
        
        # Apply radius filtering
        return self._filter_by_radius(leads)
    
    def _calculate_distances(self, leads: List) -> None:
        """
        Calculate distance for each lead without filtering.
        
        Updates lead.location dictionary with distance_km field.
        """
        if not self.calculator:
            logger.warning("Cannot calculate distances: no search center coordinates")
            return
        
        for lead in leads:
            location = self._get_lead_location(lead)
            if location and location.get("latitude") and location.get("longitude"):
                distance = self.calculator.calculate_distance(
                    location["latitude"],
                    location["longitude"]
                )
                location["distance_km"] = distance
                logger.debug(f"Lead '{self._get_lead_name(lead)}' is {distance:.2f}km away")
    
    def _filter_by_radius(self, leads: List) -> GeographicFilterResult:
        """
        Filter leads by radius constraint.
        
        Args:
            leads: List of Lead objects
        
        Returns:
            GeographicFilterResult
        """
        if not self.calculator:
            logger.error("Cannot filter by radius: no search center coordinates")
            return GeographicFilterResult(
                total_input=len(leads),
                missing_coordinates=len(leads),
                within_radius=0,
                outside_radius=0,
                filtered_leads=[],
            )
        
        radius_km = self.location_intent.radius_km
        logger.info(f"Filtering {len(leads)} leads by {radius_km}km radius")
        
        filtered = []
        missing_coords = 0
        outside_radius = 0
        
        for lead in leads:
            location = self._get_lead_location(lead)
            
            if not location or not location.get("latitude") or not location.get("longitude"):
                missing_coords += 1
                logger.debug(f"Lead '{self._get_lead_name(lead)}' missing coordinates, excluding")
                continue
            
            # Calculate distance
            distance = self.calculator.calculate_distance(
                location["latitude"],
                location["longitude"]
            )
            
            # Add distance to location
            location["distance_km"] = distance
            
            # Check if within radius
            if distance <= radius_km:
                filtered.append(lead)
                logger.debug(f"✓ Lead '{self._get_lead_name(lead)}' within radius ({distance:.2f}km)")
            else:
                outside_radius += 1
                logger.debug(f"✗ Lead '{self._get_lead_name(lead)}' outside radius ({distance:.2f}km > {radius_km}km)")
        
        # Sort by distance (nearest first)
        filtered.sort(key=lambda l: self._get_lead_location(l).get("distance_km", float("inf")))
        
        logger.info(f"Geographic filter results: {len(filtered)}/{len(leads)} within {radius_km}km")
        
        return GeographicFilterResult(
            total_input=len(leads),
            missing_coordinates=missing_coords,
            within_radius=len(filtered),
            outside_radius=outside_radius,
            filtered_leads=filtered,
        )
    
    def _get_lead_location(self, lead) -> Optional[dict]:
        """
        Extract location dictionary from lead object.
        
        Handles both dict and object attribute access.
        """
        if isinstance(lead, dict):
            return lead.get("location")
        else:
            return getattr(lead, "location", None)
    
    def _get_lead_name(self, lead) -> str:
        """Get business name from lead object"""
        if isinstance(lead, dict):
            return lead.get("business_name", "Unknown")
        else:
            return getattr(lead, "business_name", "Unknown")


def filter_by_geography(
    leads: List,
    location_intent: LocationIntent
) -> GeographicFilterResult:
    """
    Convenience function to filter leads by geography.
    
    Args:
        leads: List of Lead objects
        location_intent: Location constraints
    
    Returns:
        GeographicFilterResult
    """
    geofilter = GeographicFilter(location_intent)
    return geofilter.filter_leads(leads)


def add_distances_to_leads(
    leads: List,
    center_coords: Tuple[float, float]
) -> None:
    """
    Add distance_km field to all leads.
    
    Args:
        leads: List of Lead objects
        center_coords: (latitude, longitude) of search center
    """
    calculator = DistanceCalculator(center_coords)
    
    for lead in leads:
        if isinstance(lead, dict):
            location = lead.get("location", {})
        else:
            location = getattr(lead, "location", {})
        
        if location and location.get("latitude") and location.get("longitude"):
            distance = calculator.calculate_distance(
                location["latitude"],
                location["longitude"]
            )
            location["distance_km"] = distance
