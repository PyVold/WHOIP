"""
Unit tests for database functions.
"""
import pytest
from database.country import country_data, clear_cache


class TestCountryData:
    """Test country data retrieval."""

    def test_valid_country_codes(self):
        # Test US
        us_data = country_data('US')
        assert us_data['Name'] == 'United States'
        assert 'USD' in us_data['Currency']

        # Test UK
        uk_data = country_data('GB')
        assert uk_data['Name'] == 'United Kingdom'

    def test_unknown_country_code(self):
        # Should return default structure
        result = country_data('XX')
        assert result['Name'] == 'Unknown'
        assert 'Name' in result
        assert 'Currency' in result

    def test_cache_loading(self):
        # First call loads cache
        data1 = country_data('US')
        # Second call uses cache (should be faster)
        data2 = country_data('US')
        assert data1 == data2

    def test_cache_clear(self):
        country_data('US')  # Load cache
        clear_cache()
        # Should work after clearing
        data = country_data('US')
        assert data['Name'] == 'United States'


class TestGetCountryCode:
    """Test IP to country code lookup."""

    def test_well_known_ips(self):
        # These tests require network access and may be slow
        # Consider mocking the requests in actual test suite
        pass
