
import requests


class GeolocateQuery():
    '''Class to take an IP address and/or URL, and retrieve goelocate information'''

    def __init__(self, url, ip_addr):
        QThread.__init__(self)
        self.url = url
        self.ip_addr = ip_addr

    def do_lookup(self):
        if self.ip_addr is None:
            self.ip_addr = socket.gethostbyname(self.url)

        query_url = 'http://ip-api.com/json/' + self.ip_addr
        self.reply = requests.get(query_url).json()

        if self.reply["status"] != "success":
            return None

        return self.reply