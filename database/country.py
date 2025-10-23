"""
IP geolocation data retrieval module.
Handles IP to country mapping and country metadata lookup with caching.
"""
import pandas as pd
import os
import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

# Module-level cache for country data
_country_data_cache: Optional[Dict] = None
dir = os.path.dirname(__file__)


def _load_country_data() -> Dict:
    """
    Load country data from CSV file once and cache it.

    Returns:
        Dictionary of country data indexed by country code

    Raises:
        FileNotFoundError: If data.csv is not found
        Exception: If CSV parsing fails
    """
    global _country_data_cache

    if _country_data_cache is None:
        try:
            csv_path = os.path.join(dir, 'data.csv')
            logger.info(f"Loading country data from {csv_path}")

            # Load CSV and convert to dictionary for fast lookup
            datafile = pd.read_csv(csv_path, index_col='Code')
            _country_data_cache = datafile.to_dict('index')

            logger.info(f"Loaded {len(_country_data_cache)} country records")

        except FileNotFoundError as e:
            logger.error(f"Country data file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading country data: {e}")
            raise

    return _country_data_cache


def country_data(country_code: str) -> Dict:
    """
    Get country metadata for a given country code.

    Args:
        country_code: Two-letter ISO country code (e.g., 'US', 'GB')

    Returns:
        Dictionary with country information (Name, Native, Phone, Currency, etc.)

    Raises:
        KeyError: If country code not found in database
    """
    cache = _load_country_data()

    try:
        return cache[country_code]
    except KeyError:
        logger.warning(f"Country code not found: {country_code}")
        # Return a default structure for unknown countries
        return {
            'Name': 'Unknown',
            'Native': 'Unknown',
            'Phone': '',
            'Currency': '',
            'Languages': '',
            'Continent': '',
            'Capital': ''
        }


def get_country_code(ipaddr: str, timeout: int = 5) -> str:
    """
    Retrieve country code for a given IP address using RIPE NCC MaxMind API.

    Args:
        ipaddr: IPv4 or IPv6 address string
        timeout: Request timeout in seconds (default: 5)

    Returns:
        Two-letter ISO country code or 'private' if lookup fails

    Note:
        Returns 'private' for:
        - Private IP ranges (10.x.x.x, 192.168.x.x, etc.)
        - Failed API requests
        - Invalid responses
    """
    try:
        # Import config at runtime to avoid circular imports
        try:
            from config import Config
            api_url = Config.RIPE_API_URL
            api_timeout = Config.RIPE_API_TIMEOUT
        except (ImportError, AttributeError):
            api_url = 'https://stat.ripe.net/data/maxmind-geo-lite/data.json'
            api_timeout = timeout

        url = f"{api_url}?resource={ipaddr}"

        logger.debug(f"Querying IP geolocation for {ipaddr}")

        # Make request with timeout
        response = requests.get(url, timeout=api_timeout)
        response.raise_for_status()

        # Parse response
        data = response.json()
        locations = data['data']['located_resources'][0]['locations']

        # Extract country code from first location
        if locations and len(locations) > 0:
            country_code = locations[0].get('country')

            if country_code:
                logger.debug(f"IP {ipaddr} mapped to country {country_code}")
                return country_code

        logger.warning(f"No country found for IP {ipaddr}")
        return 'private'

    except requests.exceptions.Timeout:
        logger.warning(f"Timeout querying geolocation for IP {ipaddr}")
        return 'private'

    except requests.exceptions.RequestException as e:
        logger.warning(f"Request error for IP {ipaddr}: {e}")
        return 'private'

    except (KeyError, IndexError, TypeError) as e:
        logger.warning(f"Invalid response structure for IP {ipaddr}: {e}")
        return 'private'

    except Exception as e:
        logger.error(f"Unexpected error getting country code for IP {ipaddr}: {e}")
        return 'private'


def clear_cache():
    """Clear the country data cache. Useful for testing or data updates."""
    global _country_data_cache
    _country_data_cache = None
    logger.info("Country data cache cleared")