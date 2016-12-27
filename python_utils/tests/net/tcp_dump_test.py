import unittest
from python_utils.net import pcap_rules
from python_utils.net.tcp_dump import *
from python_utils.net.tcp_sender import TCPSender
from python_utils.tests.utils.test_utils import run_unit_test


LOOPBACK = LinuxCLI().cmd(
    [['ip', 'l'],
     ['grep', 'LOOPBACK'],
     ['cut', '-f', '2', '-d', ' '],
     ['cut', '-f', '1', '-d', ':']]).stdout


def packet_callback(packet, file_name):
    """
    :type packet: PCAPPacket
    :type file_name: str
    :return:
    """
    with open(file_name, "a" if LinuxCLI().exists(file_name) else "w") as f:
        f.write(packet.to_str())


def send_packet():
    time.sleep(5)
    tcps = TCPSender()
    lo_iface = LOOPBACK.split()[0].rstrip()
    tcps.start_send(interface=lo_iface, packet_type='tcp', count=3,
                    source_ip='127.0.0.1', dest_ip='127.0.0.1',
                    dest_port=6055, source_port=6015)


class TCPDumpTest(unittest.TestCase):
    def setUp(self):
        time.sleep(2)

    def test_read_packet(self):
        tcpd = TCPDump()

        p = multiprocessing.Process(target=send_packet)
        p.start()
        ret = tcpd.read_packet(interface='any', count=3,
                               save_dump_file=True,
                               save_dump_filename='tcp.out')
        p.join()
        ret.get(block=False)
        ret.get(block=False)
        p3 = ret.get(block=False)

        """ :type: PCAPPacket"""
        self.assertTrue(p3 is not None)

    def test_read_packet_buffered(self):
        tcpd = TCPDump()

        lo_iface = LOOPBACK.split()[0].rstrip()

        p = multiprocessing.Process(target=send_packet)
        p.start()
        ret = tcpd.read_packet(
            interface=lo_iface,
            count=3,
            pcap_filter=pcap_rules.And(
                [
                    pcap_rules.Host('localhost', proto='ip',
                                    source=True, dest=True),
                    pcap_rules.Port(6015, proto='tcp', source=True),
                    pcap_rules.Port(6055, proto='tcp', dest=True)
                ]
            ),
            save_dump_file=True, save_dump_filename='tcp.out')
        p.join()
        ret.get(block=False).parse()
        ret.get(block=False).parse()
        p3 = ret.get(block=False).parse()

        """ :type: PCAPPacket"""
        self.assertTrue(p3 is not None)
        self.assertTrue('ethernet' in p3)

    def test_sniff_host_packet(self):
        tcpd = TCPDump()
        tcps = TCPSender()
        try:

            lo_iface = LOOPBACK.split()[0].rstrip()
            tcpd.start_capture(interface=lo_iface, count=1)
            tcps.start_send(interface=lo_iface, packet_type='tcp', count=1,
                            source_ip='127.0.0.1', dest_ip='127.0.0.1',
                            dest_port=6055, source_port=6015)

            ret = tcpd.wait_for_packets(count=1, timeout=3)

            self.assertEqual(1, len(ret))

            self.assertTrue('ethernet' in ret[0].parse())

        finally:
            tcpd.stop_capture()

    def test_sniff_host_packet_immediate(self):
        tcpd = TCPDump()
        tcps = TCPSender()
        try:

            lo_iface = LOOPBACK.split()[0].rstrip()
            tcpd.start_capture(
                interface=lo_iface,
                pcap_filter=pcap_rules.And(
                    [pcap_rules.Port(6015, proto='tcp', source=True),
                     pcap_rules.Port(6055, proto='tcp', dest=True)]))

            tcps.start_send(interface=lo_iface, packet_type='tcp', count=10,
                            source_ip='127.0.0.1', dest_ip='127.0.0.1',
                            dest_port=6055, source_port=6015)

            time.sleep(3)
            tcpd.stop_capture()

            ret = tcpd.wait_for_packets(count=0)

            self.assertAlmostEqual(10, len(ret), delta=4)

            self.assertTrue('ethernet' in ret[0].parse())

        finally:
            tcpd.stop_capture()

    def test_sniff_specific_host_packet(self):
        tcpd = TCPDump()
        tcps = TCPSender()
        try:
            iface = LOOPBACK.split()[0].rstrip()

            tcpd.start_capture(
                timeout=10, interface=iface, count=1,
                pcap_filter=pcap_rules.Or(
                    [
                        pcap_rules.And(
                            [pcap_rules.Host('localhost', proto='ip',
                                             source=True, dest=True),
                             pcap_rules.Port(6015, proto='tcp', source=True),
                             pcap_rules.Port(6055, proto='tcp', dest=True),
                             pcap_rules.LessThanEqual('len', 1500)]),
                        pcap_rules.And(
                            [pcap_rules.Port(80, proto='tcp', dest=True),
                             pcap_rules.PortRange(8000, 8500,
                                                  proto='tcp', source=True),
                             pcap_rules.LessThanEqual('len', 1500)]),
                    ]
                ))

            tcps.start_send(interface=iface, packet_type='tcp', count=1,
                            source_ip='127.0.0.1', dest_ip='127.0.0.1',
                            dest_port=6055, source_port=6015)

            ret = tcpd.wait_for_packets(count=1, timeout=3)
            self.assertEqual(1, len(ret))
        finally:
            tcpd.stop_capture()

    def test_timeout_blocking(self):
        tcpd = TCPDump()

        lo_iface = LOOPBACK.split()[0].rstrip()

        try:
            tcpd.start_capture(
                interface=lo_iface, count=1,
                pcap_filter=pcap_rules.And(
                    [pcap_rules.Host('localhost', proto='ip',
                                     source=True, dest=True),
                     pcap_rules.Port(6015, proto='tcp', source=True),
                     pcap_rules.Port(6055, proto='tcp', dest=True)]),
                blocking=True, timeout=3)
        except exceptions.SubprocessTimeoutException:
            pass
        else:
            self.assertTrue(
                False,
                "Blocking tcpdump call should have timed out "
                "since no packets were sent")
        finally:
            tcpd.stop_capture()

    def test_callback(self):
        tcpd = TCPDump()
        tcps = TCPSender()

        try:
            lo_iface = LOOPBACK.split()[0].rstrip()

            LinuxCLI().rm('tmp.file')

            tcpd.start_capture(
                interface=lo_iface, count=3,
                pcap_filter=pcap_rules.And(
                    [pcap_rules.Host('localhost', proto='ip',
                                     source=True, dest=True),
                     pcap_rules.Port(6015, proto='tcp', source=True),
                     pcap_rules.Port(6055, proto='tcp', dest=True)]),
                callback=packet_callback, callback_args=['tmp.file'],
                save_dump_file=True, save_dump_filename='tcp.callback.out')

            tcps.start_send(interface=lo_iface, packet_type='tcp', count=3,
                            source_ip='127.0.0.1', dest_ip='127.0.0.1',
                            dest_port=6055, source_port=6015)

            ret = tcpd.wait_for_packets(count=3)
            tcpd.stop_capture()
            time.sleep(2)

            self.assertEqual(3, len(ret))

            self.assertTrue(LinuxCLI().exists('tmp.file'))
            file_str = LinuxCLI().read_from_file('tmp.file')
            LinuxCLI().rm('tmp.file')

            self.assertEqual(3, file_str.count('PACKET { time'))
        finally:
            tcpd.stop_capture()

    def test_early_stop(self):
        tcpd = TCPDump()
        tcps = TCPSender()

        try:
            lo_iface = LOOPBACK.split()[0].rstrip()

            tcpd.start_capture(
                interface=lo_iface, count=0,
                pcap_filter=pcap_rules.And(
                    [pcap_rules.Host('localhost', proto='ip',
                                     source=True, dest=True),
                     pcap_rules.Port(6015, proto='tcp', source=True),
                     pcap_rules.Port(6055, proto='tcp', dest=True)]))

            tcps.start_send(interface=lo_iface, packet_type='tcp', count=5,
                            source_ip='127.0.0.1', dest_ip='127.0.0.1',
                            dest_port=6055, source_port=6015)

            ret = tcpd.wait_for_packets(count=3, timeout=3)
            self.assertEqual(3, len(ret))
            ret = tcpd.wait_for_packets(count=1, timeout=3)
            self.assertEqual(1, len(ret))

            tcpd.stop_capture()

            ret = tcpd.wait_for_packets(count=1, timeout=3)
            self.assertEqual(1, len(ret))

        finally:
            tcpd.stop_capture()

    def tearDown(self):
        time.sleep(2)
        LinuxCLI().rm('tcp.callback.out')
        LinuxCLI().rm('tcp.out')

run_unit_test(TCPDumpTest)
