#!/usr/bin/env python3
"""
Weather API Tool

This tool provides weather information using WeatherAPI (https://www.weatherapi.com).
"""

from app.tools import tool
from app.config.settings import settings
from app.utils.logger import get_logger
import requests
from typing import Dict, Any

logger = get_logger(__name__)


def _get_current_weather(city: str) -> Dict[str, Any]:
    """Get current weather for a city
    
    Args:
        city: City name
        
    Returns:
        Weather data dictionary
    """
    if not settings.WEATHER_API_KEY:
        return {
            "status": "error",
            "message": "WEATHER_API_KEY not configured. Please set it in your .env file."
        }
    
    base_url = "http://api.weatherapi.com/v1/current.json"
    params = {
        "key": settings.WEATHER_API_KEY,
        "q": city,
        "aqi": "yes"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        location = data.get("location", {})
        current = data.get("current", {})
        condition = current.get("condition", {})
        air_quality = current.get("air_quality", {})
        
        return {
            "status": "success",
            "location": {
                "name": location.get("name"),
                "region": location.get("region"),
                "country": location.get("country"),
                "lat": location.get("lat"),
                "lon": location.get("lon"),
                "timezone": location.get("tz_id"),
                "local_time": location.get("localtime")
            },
            "current": {
                "temperature_c": current.get("temp_c"),
                "temperature_f": current.get("temp_f"),
                "condition": condition.get("text"),
                "condition_icon": condition.get("icon"),
                "wind_mph": current.get("wind_mph"),
                "wind_kph": current.get("wind_kph"),
                "wind_degree": current.get("wind_degree"),
                "wind_dir": current.get("wind_dir"),
                "pressure_mb": current.get("pressure_mb"),
                "pressure_in": current.get("pressure_in"),
                "precip_mm": current.get("precip_mm"),
                "precip_in": current.get("precip_in"),
                "humidity": current.get("humidity"),
                "cloud": current.get("cloud"),
                "feelslike_c": current.get("feelslike_c"),
                "feelslike_f": current.get("feelslike_f"),
                "vis_km": current.get("vis_km"),
                "vis_miles": current.get("vis_miles"),
                "uv": current.get("uv"),
                "gust_mph": current.get("gust_mph"),
                "gust_kph": current.get("gust_kph"),
                "last_updated": current.get("last_updated")
            },
            "air_quality": {
                "co": air_quality.get("co"),
                "no2": air_quality.get("no2"),
                "o3": air_quality.get("o3"),
                "so2": air_quality.get("so2"),
                "pm2_5": air_quality.get("pm2_5"),
                "pm10": air_quality.get("pm10"),
                "us_epa_index": air_quality.get("us-epa-index"),
                "gb_defra_index": air_quality.get("gb-defra-index")
            },
            "message": f"Successfully retrieved weather data for {city}"
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API request error: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch weather data: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error in weather tool: {e}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


def _get_weather_forecast(city: str, days: int = 3) -> Dict[str, Any]:
    """Get weather forecast for a city
    
    Args:
        city: City name
        days: Number of days to forecast (1-14)
        
    Returns:
        Forecast data dictionary
    """
    if not settings.WEATHER_API_KEY:
        return {
            "status": "error",
            "message": "WEATHER_API_KEY not configured. Please set it in your .env file."
        }
    
    days = max(1, min(14, days))
    
    base_url = "http://api.weatherapi.com/v1/forecast.json"
    params = {
        "key": settings.WEATHER_API_KEY,
        "q": city,
        "days": days,
        "aqi": "yes",
        "alerts": "yes"
    }
    
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        location = data.get("location", {})
        current = data.get("current", {})
        forecast = data.get("forecast", {}).get("forecastday", [])
        alerts = data.get("alerts", {}).get("alert", [])
        
        forecast_days = []
        for day in forecast:
            day_data = day.get("day", {})
            condition = day_data.get("condition", {})
            forecast_days.append({
                "date": day.get("date"),
                "max_temp_c": day_data.get("maxtemp_c"),
                "max_temp_f": day_data.get("maxtemp_f"),
                "min_temp_c": day_data.get("mintemp_c"),
                "min_temp_f": day_data.get("mintemp_f"),
                "avg_temp_c": day_data.get("avgtemp_c"),
                "avg_temp_f": day_data.get("avgtemp_f"),
                "max_wind_mph": day_data.get("maxwind_mph"),
                "max_wind_kph": day_data.get("maxwind_kph"),
                "total_precip_mm": day_data.get("totalprecip_mm"),
                "total_precip_in": day_data.get("totalprecip_in"),
                "avg_visibility_km": day_data.get("avgvis_km"),
                "avg_visibility_miles": day_data.get("avgvis_miles"),
                "avg_humidity": day_data.get("avghumidity"),
                "daily_will_it_rain": day_data.get("daily_will_it_rain"),
                "daily_chance_of_rain": day_data.get("daily_chance_of_rain"),
                "daily_will_it_snow": day_data.get("daily_will_it_snow"),
                "daily_chance_of_snow": day_data.get("daily_chance_of_snow"),
                "condition": condition.get("text"),
                "condition_icon": condition.get("icon"),
                "uv": day_data.get("uv")
            })
        
        alert_list = []
        for alert in alerts:
            alert_list.append({
                "headline": alert.get("headline"),
                "msgtype": alert.get("msgtype"),
                "severity": alert.get("severity"),
                "urgency": alert.get("urgency"),
                "areas": alert.get("areas"),
                "category": alert.get("category"),
                "certainty": alert.get("certainty"),
                "event": alert.get("event"),
                "note": alert.get("note"),
                "effective": alert.get("effective"),
                "expires": alert.get("expires"),
                "desc": alert.get("desc"),
                "instruction": alert.get("instruction")
            })
        
        return {
            "status": "success",
            "location": {
                "name": location.get("name"),
                "region": location.get("region"),
                "country": location.get("country"),
                "timezone": location.get("tz_id"),
                "local_time": location.get("localtime")
            },
            "forecast": forecast_days,
            "alerts": alert_list,
            "message": f"Successfully retrieved {days}-day weather forecast for {city}"
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Weather API forecast request error: {e}")
        return {
            "status": "error",
            "message": f"Failed to fetch weather forecast: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Unexpected error in weather forecast tool: {e}")
        return {
            "status": "error",
            "message": f"Unexpected error: {str(e)}"
        }


@tool
def get_current_weather(city: str) -> dict:
    """Get current weather conditions for a city
    
    Args:
        city: Name of the city to get weather for (e.g., "Beijing", "New York", "London")
        
    Returns:
        Current weather data including temperature, conditions, wind, humidity, etc.
    """
    return _get_current_weather(city)


@tool
def get_weather_forecast(city: str, days: int = 3) -> dict:
    """Get weather forecast for a city
    
    Args:
        city: Name of the city to get forecast for (e.g., "Beijing", "New York", "London")
        days: Number of days to forecast (1-14, default: 3)
        
    Returns:
        Weather forecast data including daily temperatures, conditions, and alerts if any
    """
    return _get_weather_forecast(city, days)
