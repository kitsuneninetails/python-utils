import unittest
from python_utils.net import pcap_rules
from python_utils.tests.utils.test_utils import run_unit_test


class PCAPTest(unittest.TestCase):
    def test_host_rules(self):
        simple_rule = pcap_rules.Host('foo')
        proto_rule = pcap_rules.Host('foo', proto='ether')
        proto_with_src_rule = pcap_rules.Host('foo', 'ether', source=True)
        src_and_dest_rule = pcap_rules.Host('foo', source=True, dest=True)
        dest_rule = pcap_rules.Host('foo', dest=True)

        self.assertEqual('host foo', simple_rule.to_str())
        self.assertEqual('ether host foo', proto_rule.to_str())
        self.assertEqual('ether src host foo', proto_with_src_rule.to_str())
        self.assertEqual('src and dst host foo', src_and_dest_rule.to_str())
        self.assertEqual('dst host foo', dest_rule.to_str())

    def test_port_rules(self):
        simple_rule = pcap_rules.Port(80)
        proto_rule = pcap_rules.Port(80, proto='ether')
        proto_with_src_rule = pcap_rules.Port(80, 'ether', source=True)
        src_and_dest_rule = pcap_rules.Port(80, source=True, dest=True)
        dest_rule = pcap_rules.Port(80, dest=True)

        self.assertEqual('port 80', simple_rule.to_str())
        self.assertEqual('ether port 80', proto_rule.to_str())
        self.assertEqual('ether src port 80', proto_with_src_rule.to_str())
        self.assertEqual('src and dst port 80', src_and_dest_rule.to_str())
        self.assertEqual('dst port 80', dest_rule.to_str())

        range_simple_rule = pcap_rules.PortRange(80, 90)
        range_proto_rule = pcap_rules.PortRange(80, 90, proto='ether')
        range_proto_with_src_rule = pcap_rules.PortRange(80, 90, 'ether',
                                                         source=True)
        range_src_and_dest_rule = pcap_rules.PortRange(80, 90, source=True,
                                                       dest=True)
        range_dest_rule = pcap_rules.PortRange(80, 90, dest=True)

        self.assertEqual('portrange 80-90', range_simple_rule.to_str())
        self.assertEqual('ether portrange 80-90', range_proto_rule.to_str())
        self.assertEqual('ether src portrange 80-90',
                         range_proto_with_src_rule.to_str())
        self.assertEqual('src and dst portrange 80-90',
                         range_src_and_dest_rule.to_str())
        self.assertEqual('dst portrange 80-90', range_dest_rule.to_str())

    def test_net_rules(self):
        simple_rule = pcap_rules.Net('192.168.0')
        proto_rule = pcap_rules.Net('192.168.0', proto='ether')
        proto_with_src_rule = pcap_rules.Net('192.168.0', '', 'ether', source=True)
        src_and_dest_rule = pcap_rules.Net('192.168.0', source=True, dest=True)
        dest_rule = pcap_rules.Net('192.168.0', dest=True)
        cidr_rule = pcap_rules.Net('192.168.0.0/24')
        netmask_rule = pcap_rules.Net('192.168.0.0', '255.255.255.0')

        self.assertEqual('net 192.168.0', simple_rule.to_str())
        self.assertEqual('ether net 192.168.0', proto_rule.to_str())
        self.assertEqual('ether src net 192.168.0',
                         proto_with_src_rule.to_str())
        self.assertEqual('src and dst net 192.168.0',
                         src_and_dest_rule.to_str())
        self.assertEqual('dst net 192.168.0', dest_rule.to_str())
        self.assertEqual('net 192.168.0.0/24', cidr_rule.to_str())
        self.assertEqual('net 192.168.0.0 mask 255.255.255.0',
                         netmask_rule.to_str())

    def test_ip_proto_rules(self):
        tcp_rule = pcap_rules.IPProto('tcp')
        icmp_rule = pcap_rules.IPProto('icmp')
        udp_rule = pcap_rules.IPProto('udp')

        self.assertEqual('ip proto \\tcp', tcp_rule.to_str())
        self.assertEqual('ip proto \\icmp', icmp_rule.to_str())
        self.assertEqual('ip proto \\udp', udp_rule.to_str())

    def test_ether_proto_rules(self):
        ip_rule = pcap_rules.EtherProto('ip')
        arp_rule = pcap_rules.EtherProto('arp')
        stp_rule = pcap_rules.EtherProto('stp')

        self.assertEqual('ether proto ip', ip_rule.to_str())
        self.assertEqual('ether proto arp', arp_rule.to_str())
        self.assertEqual('ether proto stp', stp_rule.to_str())

    def test_cast_rules(self):
        ether_mc_rule = pcap_rules.Multicast('ether')
        ether_default_mc_rule = pcap_rules.Multicast()
        ip_mc_rule = pcap_rules.Multicast('ip')

        self.assertEqual('ether multicast', ether_mc_rule.to_str())
        self.assertEqual('ether multicast', ether_default_mc_rule.to_str())
        self.assertEqual('ip multicast', ip_mc_rule.to_str())

        ether_bc_rule = pcap_rules.Broadcast('ether')
        ether_default_bc_rule = pcap_rules.Broadcast()
        ip_bc_rule = pcap_rules.Broadcast('ip')

        self.assertEqual('ether broadcast', ether_bc_rule.to_str())
        self.assertEqual('ether broadcast', ether_default_bc_rule.to_str())
        self.assertEqual('ip broadcast', ip_bc_rule.to_str())

    def test_comparison_rules(self):
        gt_rule = pcap_rules.GreaterThan('len', '500')
        gt_flip_rule = pcap_rules.GreaterThan('500', 'len')
        gte_rule = pcap_rules.GreaterThanEqual('len', '500')
        e_rule = pcap_rules.Equal('len', '500')
        ne_rule = pcap_rules.NotEqual('len', '500')
        lt_rule = pcap_rules.LessThan('len', '500')
        lte_rule = pcap_rules.LessThanEqual('len', '500')

        self.assertEqual('len > 500', gt_rule.to_str())
        self.assertEqual('500 > len', gt_flip_rule.to_str())
        self.assertEqual('len >= 500', gte_rule.to_str())
        self.assertEqual('len = 500', e_rule.to_str())
        self.assertEqual('len != 500', ne_rule.to_str())
        self.assertEqual('len < 500', lt_rule.to_str())
        self.assertEqual('len <= 500', lte_rule.to_str())

    def test_unary_boolean_rules(self):
        not_single_rule = pcap_rules.Not(pcap_rules.Simple('foo'))
        self.assertEqual('not ( foo )', not_single_rule.to_str())

    def test_binary_boolean_rules(self):
        and_single_rule = pcap_rules.And([pcap_rules.Simple('foo')])
        and_double_rule = pcap_rules.And([pcap_rules.Simple('foo'), pcap_rules.Simple('bar')])
        and_triple_rule = pcap_rules.And([pcap_rules.Simple('foo'),
                                          pcap_rules.Simple('bar'), pcap_rules.Simple('baz')])
        and_null_rule = pcap_rules.And([])
        or_single_rule = pcap_rules.Or([pcap_rules.Simple('foo')])
        or_double_rule = pcap_rules.Or([pcap_rules.Simple('foo'), pcap_rules.Simple('bar')])
        or_triple_rule = pcap_rules.Or([pcap_rules.Simple('foo'),
                                        pcap_rules.Simple('bar'), pcap_rules.Simple('baz')])
        or_null_rule = pcap_rules.Or([])

        self.assertEqual('( foo )', and_single_rule.to_str())
        self.assertEqual('( foo ) and ( bar )', and_double_rule.to_str())
        self.assertEqual('( foo ) and ( bar ) and ( baz )',
                         and_triple_rule.to_str())
        self.assertEqual('', and_null_rule.to_str())
        self.assertEqual('( foo )', or_single_rule.to_str())
        self.assertEqual('( foo ) or ( bar )', or_double_rule.to_str())
        self.assertEqual('( foo ) or ( bar ) or ( baz )',
                         or_triple_rule.to_str())
        self.assertEqual('', or_null_rule.to_str())

    def test_complex_rules(self):
        complex_rule = pcap_rules.And([
            pcap_rules.And([
                pcap_rules.Not(pcap_rules.Multicast()),
                pcap_rules.Or([
                    pcap_rules.Host('bar', proto='ether', source=True),
                    pcap_rules.Net('192.168.0.0', '255.255.255.0')
                ]),
                pcap_rules.GreaterThan('len', '80')
            ]),
            pcap_rules.Port(80, dest=True),
            pcap_rules.Or([
                pcap_rules.PortRange(30000, 50000, source=True),
                pcap_rules.IPProto('tcp'),
                pcap_rules.Not(pcap_rules.Broadcast())
            ]),
            pcap_rules.And([
                pcap_rules.NotEqual('ether[0] & 1', '0'),
                pcap_rules.NotEqual('ip[0] & 0xf', '5'),
                pcap_rules.LessThanEqual('len', '1500')
            ])
        ])

        expected_str = \
            '( ' \
            '( not ( ether multicast ) ) and ' \
            '( ' \
            '( ether src host bar ) or ' \
            '( net 192.168.0.0 mask 255.255.255.0 ) ' \
            ') and ' \
            '( len > 80 ) ' \
            ') and ' \
            '( dst port 80 ) and ' \
            '( ' \
            '( src portrange 30000-50000 ) or ' \
            '( ip proto \\tcp ) or ' \
            '( not ( ether broadcast ) ) ' \
            ') and ' \
            '( ' \
            '( ether[0] & 1 != 0 ) and ' \
            '( ip[0] & 0xf != 5 ) and ' \
            '( len <= 1500 ) ' \
            ')'

        self.assertEqual(expected_str, complex_rule.to_str())

run_unit_test(PCAPTest)
