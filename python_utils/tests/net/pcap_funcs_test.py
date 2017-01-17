import unittest
from python_utils.common import exceptions
from python_utils.net import pcap_funcs
from python_utils.tests.utils.test_utils import run_unit_test


class PCAPFuncsTest(unittest.TestCase):
    def test_start_cap_no_iface(self):
        pcap = pcap_funcs.Pcap('blarg')
        self.assertRaises(exceptions.SubprocessFailedException,
                          pcap.start_capture)

run_unit_test(PCAPFuncsTest)
