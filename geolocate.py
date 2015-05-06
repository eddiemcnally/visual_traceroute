import requests


class GeolocateQuery():
    """
    Uses http://ip-api.com to retrieve geolocation data for an IP address
    """

    def __init__(self, ip_addr):
        self.ip_addr = ip_addr

    def do_lookup(self):
        query_url = 'http://ip-api.com/json/' + self.ip_addr
        reply = requests.get(query_url).json()

        if reply["status"] != "success":
            return None

        return reply