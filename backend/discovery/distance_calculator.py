"""
Distance Calculator
-------------------
Calculate geographic distances between coordinates using the Haversine formula.
"""
import math
from typing import Optional, Tuple


def calculate_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two coordinates in kilometers using Haversine formula.
    
    Args:
        lat1: Latitude of first point (degrees)
        lon1: Longitude of first point (degrees)
        lat2: Latitude of second point (degrees)
        lon2: Longitude of second point (degrees)
    
    Returns:
        Distance in kilometers
    
    Example:
        >>> # Distance from Ahmedabad to Mumbai
        >>> calculate_distance_km(23.0225, 72.5714, 19.0760, 72.8777)
        441.67
    """
    # Radius of Earth in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Differences
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    # Haversine formula
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    distance = R * c
    
    return round(distance, 2)


def calculate_distance_miles(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
) -> float:
    """
    Calculate distance between two coordinates in miles.
    
    Args:
        lat1: Latitude of first point (degrees)
        lon1: Longitude of first point (degrees)
        lat2: Latitude of second point (degrees)
        lon2: Longitude of second point (degrees)
    
    Returns:
        Distance in miles
    """
    km = calculate_distance_km(lat1, lon1, lat2, lon2)
    return round(km * 0.621371, 2)


def is_within_radius(
    center_coords: Tuple[float, float],
    business_coords: Tuple[float, float],
    radius_km: float
) -> bool:
    """
    Check if a business is within a specified radius of a center point.
    
    Args:
        center_coords: (latitude, longitude) of search center
        business_coords: (latitude, longitude) of business
        radius_km: Radius in kilometers
    
    Returns:
        True if business is within radius, False otherwise
    """
    distance = calculate_distance_km(
        center_coords[0], center_coords[1],
        business_coords[0], business_coords[1]
    )
    return distance <= radius_km


def miles_to_km(miles: float) -> float:
    """Convert miles to kilometers"""
    return round(miles * 1.60934, 2)


def km_to_miles(km: float) -> float:
    """Convert kilometers to miles"""
    return round(km * 0.621371, 2)


class DistanceCalculator:
    """
    Utility class for batch distance calculations.
    """
    
    def __init__(self, center_coords: Tuple[float, float]):
        """
        Initialize calculator with a center point.
        
        Args:
            center_coords: (latitude, longitude) of the reference point
        """
        self.center_lat = center_coords[0]
        self.center_lon = center_coords[1]
    
    def calculate_distance(self, lat: float, lon: float) -> float:
        """
        Calculate distance from center to a point.
        
        Args:
            lat: Latitude of the point
            lon: Longitude of the point
        
        Returns:
            Distance in kilometers
        """
        return calculate_distance_km(
            self.center_lat, self.center_lon,
            lat, lon
        )
    
    def is_within_radius(self, lat: float, lon: float, radius_km: float) -> bool:
        """
        Check if a point is within the specified radius from center.
        
        Args:
            lat: Latitude of the point
            lon: Longitude of the point
            radius_km: Radius in kilometers
        
        Returns:
            True if within radius, False otherwise
        """
        distance = self.calculate_distance(lat, lon)
        return distance <= radius_km
    
    def filter_by_radius(
        self,
        points: list[Tuple[float, float]],
        radius_km: float
    ) -> list[Tuple[float, float, float]]:
        """
        Filter points by radius and return with distances.
        
        Args:
            points: List of (latitude, longitude) tuples
            radius_km: Maximum radius in kilometers
        
        Returns:
            List of (latitude, longitude, distance_km) for points within radius
        """
        results = []
        for lat, lon in points:
            distance = self.calculate_distance(lat, lon)
            if distance <= radius_km:
                results.append((lat, lon, distance))
        
        # Sort by distance (nearest first)
        results.sort(key=lambda x: x[2])
        return results
