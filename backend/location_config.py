"""
Location Configuration
----------------------
Centralized configuration for geographic targeting.

Change these values to target a different location.
"""
import os

# Default location: Ahmedabad, Gujarat, India
DEFAULT_LOCATION_NAME = os.getenv("DEFAULT_LOCATION_NAME", "Ahmedabad, Gujarat, India")
DEFAULT_LOCATION_CITY = os.getenv("DEFAULT_LOCATION_CITY", "Ahmedabad")
DEFAULT_LOCATION_STATE = os.getenv("DEFAULT_LOCATION_STATE", "Gujarat")
DEFAULT_LOCATION_COUNTRY = os.getenv("DEFAULT_LOCATION_COUNTRY", "India")
DEFAULT_LOCATION_LAT = float(os.getenv("DEFAULT_LOCATION_LAT", "23.0225"))
DEFAULT_LOCATION_LNG = float(os.getenv("DEFAULT_LOCATION_LNG", "72.5714"))
DEFAULT_SEARCH_RADIUS_KM = float(os.getenv("DEFAULT_SEARCH_RADIUS_KM", "20"))

def get_default_location_coords():
    """Get default location coordinates as tuple"""
    return (DEFAULT_LOCATION_LAT, DEFAULT_LOCATION_LNG)

def get_default_location_name():
    """Get default location name"""
    return DEFAULT_LOCATION_NAME

def get_default_search_radius():
    """Get default search radius in km"""
    return DEFAULT_SEARCH_RADIUS_KM


# Quick reference for major Indian cities
CITY_COORDINATES = {
    "Ahmedabad": (23.0225, 72.5714),
    "Mumbai": (19.0760, 72.8777),
    "Delhi": (28.7041, 77.1025),
    "Bangalore": (12.9716, 77.5946),
    "Hyderabad": (17.3850, 78.4867),
    "Chennai": (13.0827, 80.2707),
    "Kolkata": (22.5726, 88.3639),
    "Pune": (18.5204, 73.8567),
    "Jaipur": (26.9124, 75.7873),
    "Surat": (21.1702, 72.8311),
}

def get_city_coords(city_name: str):
    """Get coordinates for a known city"""
    return CITY_COORDINATES.get(city_name, get_default_location_coords())
