from python_utils.shell.cli import LinuxCLI
from python_utils.common.exceptions import ArgMismatchException
from python_utils.common.exceptions import SubprocessFailedException

import multiprocessing


def send_packet(tcp_event, **kwargs):
    TCPSender.send_packet(tcp_ready=tcp_event, **kwargs)


class TCPSender(object):

    def __init__(self):
        self.process = None

    def start_send(self, blocking=True, **kwargs):
        if self.process is not None:
            raise SubprocessFailedException(
                'tcp send process already started')

        tcp_ready = multiprocessing.Event()
        tcp_ready.clear()
        self.process = multiprocessing.Process(
            target=send_packet,
            args=(tcp_ready,), kwargs=kwargs)
        self.process.daemon = True
        self.process.start()
        if tcp_ready.wait(10) is False:
            raise SubprocessFailedException(
                "mz failed to send within timeout")

        if blocking is True:
            self.process.join()

    def stop_send(self, term=False):
        if self.process is None:
            raise SubprocessFailedException('tcp send process not started')

        if term is True:
            self.process.terminate()
        else:
            self.process.join()
        self.process = None

    @staticmethod
    def send_packet(cli=LinuxCLI(), tcp_ready=None,
                    interface='any', packet_type=None,
                    source_port=None, dest_port=None,
                    source_ip=None, dest_ip=None, source_mac=None,
                    dest_mac=None, packet_options=None, count=None,
                    delay=None, byte_data=None, payload=None, timeout=None):
        """
        :type cli: LinuxCLI
        :type tcp_ready: multiprocessing.Event
        :type interface: str
        :type packet_type: str|None
        :type source_port: int|None
        :type dest_port: int|None
        :type source_ip: str|None
        :type dest_ip: str|None
        :type source_mac: str|None
        :type dest_mac: str|None
        :type packet_options: dict[str, str]|None
        :type count: int|None
        :type delay: int|None
        :type byte_data: str|None
        :type payload: str|None
        :type timeout: int|None
        :return: CommandStatus
        """

        count_str = ['-c', str(count)] if count is not None else []
        src_mac_str = ['-a', source_mac] if source_mac is not None else []
        dest_mac_str = ['-b', dest_mac] if dest_mac is not None else []
        arg_str = count_str + src_mac_str + dest_mac_str

        # Bytes-only mode, only -a, -b, -c, and -p are supported by mz
        if packet_type is None:
            if byte_data is None:
                raise ArgMismatchException(
                    'The "byte_data" parameter is required if "packet_type" '
                    'is not present')
            full_cmd_str = (['mz', interface] + arg_str + [byte_data])
            out = cli.cmd([full_cmd_str], timeout=timeout)
            if tcp_ready is not None:
                tcp_ready.set()
            return out

        # Packet-builder mode, supports various opts (supported opts depend
        # on packet type)
        pkt_type_str = ['-t', packet_type] if packet_type is not None else []
        src_ip_str = ['-A', source_ip] if source_ip is not None else []
        dest_ip_str = ['-B', dest_ip] if dest_ip is not None else []
        delay_str = ['-d', str(delay)] if delay is not None else []
        payload_str = ['-P', payload] if payload is not None else []
        pkt_bldr_arg_str = src_ip_str + dest_ip_str + delay_str + payload_str

        if packet_type is 'arp' or packet_type is 'icmp':
            if 'command' not in packet_options:
                raise ArgMismatchException('arp and icmp packets need a '
                                           'command or type')
            cmd_opt = packet_options.pop('command')
            opt_list = (', '.join(
                '%(k)s=%(v)s' % {'k': k, 'v': v}
                for k, v in packet_options.iteritems())
                        if packet_options is not None else '')
            cmd_str = cmd_opt + (', ' + opt_list if opt_list != '' else '')
        elif packet_type is 'tcp' or packet_type is 'udp':
            source_port_str = 'sp=%(sp)d' % {'sp': source_port} \
                if source_port is not None else ''
            dest_port_str = 'dp=%(dp)d' % {'dp': dest_port} \
                if dest_port is not None else ''
            cmd_str = ','.join((source_port_str, dest_port_str))
        else:
            cmd_str = (', '.join(
                '%(k)s=%(v)s' % {'k': k, 'v': v}
                for k, v in packet_options.iteritems())
                       if packet_options is not None else '')

        full_cmd_str = (['mz', interface] + arg_str +
                        pkt_bldr_arg_str + pkt_type_str + [cmd_str])
        prev = cli.log_cmd
        cli.log_cmd = True
        out = cli.cmd([full_cmd_str], timeout=timeout)
        if tcp_ready is not None:
            tcp_ready.set()
        cli.log_cmd = prev
        return out
