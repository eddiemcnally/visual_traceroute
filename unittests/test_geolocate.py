import unittest

from geolocate import GeolocateQuery


class TestGeolocate(unittest.TestCase):
    '''
    Test cases for the geolocation service
    '''

    def test_invalid_ip_address(self):
        ip_addr = "127.0.0.1"
        query = GeolocateQuery(ip_addr)
        geoinfo = query.do_lookup()
        self.assertEquals(geoinfo, None)

    def test_valid_ip_address(self):
        ip_addr = "130.89.148.14"  # www.debian.org
        query = GeolocateQuery(ip_addr)
        geoinfo = query.do_lookup()
        self.assertEquals(geoinfo["status"], "success")



