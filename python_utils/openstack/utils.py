from neutronclient.common import exceptions as nex
from python_utils.common import exceptions


def find_net_by_name_or_id(nc, net_name):
    nets_by_name = [net
                    for net in nc.list_networks()['networks']
                    if net['name'] == net_name]
    if len(nets_by_name) == 0:
        try:
            net_by_id = nc.show_network(net_name)['network']
        except nex.NotFound:
            raise exceptions.ArgMismatchException(
                'Net not found by ID or name: ' + net_name)
    elif len(nets_by_name) > 1:
        raise exceptions.ArgMismatchException(
            'Multiple nets of name found: ' + net_name + '; try with ID.')
    else:
        net_by_id = nets_by_name[0]

    return net_by_id


def find_port_by_name_or_id(nc, port_name):
    ports_by_name = [p
                     for p in nc.list_ports()['ports']
                     if p['name'] == port_name]
    if len(ports_by_name) == 0:
        try:
            port_by_id = nc.show_port(port_name)['port']
        except nex.NotFound:
            raise exceptions.ArgMismatchException(
                'Port not found with name or ID: ' + port_name)
    elif len(ports_by_name) > 1:
        raise exceptions.ArgMismatchException(
            'Multiple ports of name found: ' + port_name + '; try with ID.')
    else:
        port_by_id = ports_by_name[0]
    return port_by_id
