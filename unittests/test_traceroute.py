import unittest

from traceroute import TraceRouteUtils


class TestTraceRoute(unittest.TestCase):
    '''
    Test cases for the traceroute functionality
    '''

    def test_extract_ip_address(self):
        traceRouteUtils = TraceRouteUtils()

        test_cases = [
            (" 1  laptop.domain.com (192.168.2.1)  0.614 ms  1.494 ms  1.594 ms", "192.168.2.1"),
            (" 3  109.255.251.29 (109.255.251.29)  31.888 ms  32.196 ms  32.288 ms", "109.255.251.29"),
            (" 4  nl-ams02a-rd2-xe-5-0-1.aorta.net (84.116.130.33)  140.127 ms  140.409 ms  140.529 ms",
             "84.116.130.33"),
            (" 6  xe-5-0-3 (204.148.11.109)  137.299 ms  135.577 ms  135.589 ms", "204.148.11.109"),
            ("14  www.opensuse.org (130.57.66.6)  243.286 ms  249.508 ms *", "130.57.66.6")]

        for line, ip in test_cases:
            extracted_ip = traceRouteUtils.extract_ip_address(line)
            assert extracted_ip == ip


    def test_lines_with_no_route_info(self):
        traceRouteUtils = TraceRouteUtils()

        test_cases = [
            "traceroute to www.opensuse.org (130.57.66.6), 30 hops max, 60 byte packets",
            " 2  * * *"]

        for line in test_cases:
            extracted_ip = traceRouteUtils.extract_ip_address(line)
            assert extracted_ip is None

