import os_client_config
import subprocess
from python_utils.openstack import utils


def create_neutron_client():
    return os_client_config.make_client("network")


def make_gateway_ip(real_ip):
    # Figure out a default gw based on IP, usually
    # (IP & subnet_mask + 1)
    subnet_mask = [255, 255, 255, 255]
    cidr_pos = real_ip.find('/')
    if cidr_pos != -1:
        subnet = real_ip[cidr_pos + 1:]
        real_ip = real_ip[:cidr_pos]
    else:
        subnet = ""

    if subnet != "":
        smask = int(subnet)
        subnet_mask = []

        current_mask = smask
        for i in range(0, 4):
            if current_mask > 8:
                subnet_mask.append(255)
            else:
                lastmask = 0
                for j in range(0, current_mask):
                    lastmask += pow(2, 8 - (j + 1))
                subnet_mask.append(lastmask)
            current_mask -= 8

    split_ip = real_ip.split(".")
    gw_ip_split = []
    for ip_part in split_ip:
        gw_ip_split.append(int(ip_part) &
                           subnet_mask[len(gw_ip_split)])

    gw_ip_split[3] += 1
    gw_ip = '.'.join(map(lambda x: str(x), gw_ip_split))
    return gw_ip.strip()


def create_vm(vm_name, net_name, ip_addr=None):
    nc = create_neutron_client()
    net_by_id = utils.find_net_by_name_or_id(nc, net_name)

    netns_add_cmd = ['sudo', 'ip', 'netns', 'add', vm_name]
    netns_del_cmd = ['sudo', 'ip', 'netns', 'del', vm_name]

    try:
        subprocess.call(netns_add_cmd)
        port = {
            'port': {
                'name': vm_name,
                'network_id': net_by_id['id'],
                'device_owner': 'compute:nova'}}
        if ip_addr:
            port['port']['fixed_ips'] = [{'ip_address': str(ip_addr)}]
        vm_port = nc.create_port(port)['port']
        print("port created: " + str(vm_port))
    except:
        subprocess.call(netns_del_cmd)
        raise

    vm_port_id = vm_port['id']
    vm_port_mac = vm_port['mac_address']
    vm_port_ipaddr = vm_port['fixed_ips'][0]['ip_address']
    vm_tap = 'tap' + vm_port_id[0:11]
    vm_tap_peer = vm_tap[0:11] + '.p'

    if vm_port_ipaddr.find('/') == -1:
        vm_port_ipaddr += '/24'

    link_add_cmd = ['sudo', 'ip', 'link', 'add',
                    vm_tap,
                    'type', 'veth',
                    'peer', 'name', vm_tap_peer]
    link_del_cmd = ['sudo', 'ip', 'link', 'del',
                    vm_tap]
    link_up_cmd = ['sudo', 'ip', 'link', 'set', 'dev', vm_tap, 'up']

    link_set_ns_eth0_cmd = ['sudo', 'ip', 'link', 'set',
                            'dev', vm_tap_peer, 'netns', vm_name,
                            'name', 'eth0']
    mac_addr_ns_eth0_cmd = ['sudo', 'ip', 'netns', 'exec', vm_name,
                            'ip', 'link', 'set', 'eth0',
                            'address', vm_port_mac]
    ip_addr_ns_eth0_cmd = ['sudo', 'ip', 'netns', 'exec', vm_name,
                           'ip', 'addr', 'add', vm_port_ipaddr,
                           'dev', 'eth0']
    link_up_ns_eth0_cmd = ['sudo', 'ip', 'netns', 'exec', vm_name,
                           'ip', 'link', 'set', 'dev', 'eth0', 'up']

    mm_ctl_cmd = ['sudo', 'mm-ctl', '--bind-port', vm_port_id, vm_tap]

    def_route_ns_eth0_cmd = ['sudo', 'ip', 'netns', 'exec', vm_name,
                             'ip', 'route', 'add', 'default', 'via',
                             make_gateway_ip(vm_port_ipaddr)]

    try:
        print (' '.join(link_add_cmd))
        if subprocess.call(link_add_cmd):
            raise Exception("Link add failed")

        print (' '.join(link_set_ns_eth0_cmd))
        if subprocess.call(link_set_ns_eth0_cmd):
            raise Exception("Link set onto NS failed")

        print (' '.join(mac_addr_ns_eth0_cmd))
        if subprocess.call(mac_addr_ns_eth0_cmd):
            raise Exception("MAC Addr set failed")

        print (' '.join(ip_addr_ns_eth0_cmd))
        if subprocess.call(ip_addr_ns_eth0_cmd):
            raise Exception("IP Addr set failed")

        print (' '.join(link_up_ns_eth0_cmd))
        if subprocess.call(link_up_ns_eth0_cmd):
            raise Exception("Eth0 UP failed")

        print (' '.join(link_up_cmd))
        if subprocess.call(link_up_cmd):
            raise Exception("Tap UP failed")

        print (' '.join(mm_ctl_cmd))
        if subprocess.call(mm_ctl_cmd):
            raise Exception("MM CTL failed")

        print (' '.join(def_route_ns_eth0_cmd))
        if subprocess.call(def_route_ns_eth0_cmd):
            raise Exception("Add default route failed")

    except:
        subprocess.call(['sudo', 'ip', 'netns', 'exec', vm_name, 'ip', 'a'])
        nc.delete_port(vm_port_id)
        subprocess.call(link_del_cmd)
        subprocess.call(netns_del_cmd)
        raise


def delete_vm(vm_name, port_id=None):
    nc = create_neutron_client()

    vm_port_id = utils.find_port_by_name_or_id(
        nc, port_id if port_id else vm_name)['id']

    mm_ctl_cmd = ['sudo', 'mm-ctl', '--unbind-port', vm_port_id]
    netns_del_cmd = ['sudo', 'ip', 'netns', 'del', vm_name]

    vm_tap = 'tap' + vm_port_id[0:11]

    link_del_cmd = ['sudo', 'ip', 'link', 'del',
                    vm_tap]

    subprocess.call(mm_ctl_cmd)

    nc.delete_port(vm_port_id)
    subprocess.call(link_del_cmd)
    subprocess.call(netns_del_cmd)
