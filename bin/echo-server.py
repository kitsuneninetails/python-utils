#!/usr/bin/env python
import errno
import getopt
import logging
import select
import signal
import socket
import sys
import threading
import time

from python_utils.common import exceptions
from python_utils.logging import log_manager

DEFAULT_ECHO_PORT = 5080
TIMEOUT = 5
TERMINATION_STRING = chr(0x03) + chr(0x04)
ECHO_SERVER_TIMEOUT = 3


def usage():
    print('Usage: echo-server.py [-i <ip>] [-p <port>] [-d] [-c <protocol>]')
    print('                      [-o <output_string>] [-t <timeout>]')
    print('                      [-l <log_file>] [-r <log_root>]')


arg_map, _ = getopt.getopt(
    sys.argv[1:],
    'i:'
    'p:'
    'd'
    'c:'
    'o:'
    't:'
    'l:'
    'r:'
    'n:'
    'h',
    ['help', 'ip=', 'port=', 'debug', 'out-str=', 'protocol=',
     'timeout=', 'log-file=', 'log-dir=', 'log-name='])

ip_addr = 'localhost'
port = DEFAULT_ECHO_PORT
debug = False
echo_reply_string = "pong"
protocol = "tcp"
timeout = 3600
log_dir = '/tmp'
log_file = 'echo-server-status.log'
log_name = 'echo_server'

for arg, value in arg_map:
    if arg in ('-i', 'ip'):
        ip_addr = value
    elif arg in ('-p', 'port'):
        port = int(value)
    elif arg in ('-d', 'debug'):
        debug = True
    elif arg in ('-c', 'protocol'):
        protocol = value
    elif arg in ('-o', 'out-string'):
        echo_reply_string = value
    elif arg in ('-t', 'timeout'):
        timeout = value
    elif arg in ('-l', 'log-file'):
        log_file = value
    elif arg in ('-r', 'log-dir'):
        log_dir = value
    elif arg in ('-n', 'name'):
        log_name = value
    elif arg in ('-h', 'help'):
        usage()
        exit(0)
    else:
        usage()
        raise exceptions.ArgMismatchException(
            "Option not recognized: " + arg)

lm = log_manager.LogManager(root_dir=log_dir)
LOG = lm.add_tee_logger(
    file_name=log_file, name=log_name,
    file_log_level=logging.DEBUG if debug else logging.INFO,
    stdout_log_level=logging.DEBUG if debug else logging.INFO)

stop_event = threading.Event()
finished_event = threading.Event()


def term_handler(_, __):
    print("Exiting...")
    LOG.info('Stopping based on signal')
    stop_event.set()
    LOG.info('Exiting based on signal')
    exit(0)

signal.signal(signal.SIGTERM, term_handler)
signal.signal(signal.SIGINT, term_handler)


stop_event.clear()
LOG.info('Starting Echo Server on IP: ' + ip_addr + ', port: ' + str(port))
try:
    if protocol == 'tcp':
        _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # TODO(micucci): Enable UDP
    # elif protocol == 'udp':
    #     _socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
    #                             socket.IPPROTO_UDP)
    else:
        raise exceptions.ArgMismatchException(
            'Unsupported protocol: ' + protocol)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    _socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    _socket.setblocking(0)
    _socket.bind((ip_addr, port))
    if protocol == 'tcp':
        _socket.listen(2)
        LOG.debug('Listener TCP Socket listening')

    deadline = time.time() + int(timeout)
    while not stop_event.is_set():
        if time.time() > deadline:
            stop_event.set()
            LOG.debug('Listener TCP Socket timeout reached')
            break

        ready_list, _, _ = select.select([_socket], [], [], 0)
        if ready_list:

            if protocol == 'tcp':
                debug and LOG.debug(
                    'Listener TCP Socket connected')
                conn, addr = ready_list[0].accept()
                conn.setblocking(0)

            data = ''
            addr = None
            while True:
                try:
                    if protocol == 'tcp':
                        new_data = conn.recv(
                            1024, socket.MSG_WAITALL)
                    elif protocol == 'udp':
                        new_data, addr = _socket.recvfrom(
                            1024, socket.MSG_WAITALL)
                except socket.error as e:
                    if (e.args[0] == errno.EAGAIN or
                            e.args[0] == errno.EWOULDBLOCK):
                        continue
                debug and LOG.debug(
                    'Listener Socket read some ' +
                    protocol + ' data: ' + new_data)
                pos = new_data.find(TERMINATION_STRING)
                if pos != -1:
                    data += new_data[0:pos]
                    break
                else:
                    data += new_data

            debug and LOG.debug(
                'Listener Socket received all  ' +
                protocol + ' data: ' + data)

            send_data = echo_reply_string + TERMINATION_STRING
            if protocol == 'tcp':
                conn.sendall(data + ':' + send_data)
            elif protocol == 'udp':
                _socket.sendto(data + ':' + send_data, addr)

            debug and LOG.debug(
                'Listener Socket sent appended ' +
                protocol + ' data: ' + send_data)

            if protocol == 'tcp':
                conn.close()
            elif protocol == 'udp':
                _socket.close()
        time.sleep(0)

    LOG.debug('Listener Socket terminating')
    if protocol == 'tcp':
        _socket.shutdown(socket.SHUT_RDWR)
    _socket.close()
    LOG.debug('Listener Socket finished')
except Exception as e:
    LOG.error('SERVER ERROR: ' + str(e))
    raise
except socket.error as e:
    LOG.error('SOCKET-SETUP ERROR: ' + str(e))
    raise
