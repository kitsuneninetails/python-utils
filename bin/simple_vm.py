#!/usr/bin/env python
import argparse
from python_utils.common import exceptions
from python_utils.openstack import ipnetns_vm


def main():
    # Parse args
    parser = argparse.ArgumentParser(
        description='Create a VM with port and attach to neutron network',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-a', '--add', action='store_true', default=False,
                        help='VM Name', required=False)
    parser.add_argument('-d', '--delete', action='store_true', default=False,
                        help='VM Name', required=False)
    parser.add_argument('-v', '--vm-name', action='store', default=None,
                        help='VM Name', required=True)
    parser.add_argument('-n', '--net', action='store', default=None,
                        help='Net name or ID to start VM', required=False)
    parser.add_argument('-i', '--ip', action='store', default=None,
                        help='IP to assign to VM eth0', required=False)
    parser.add_argument('-p', '--port-id', action='store', default=None,
                        help='Port ID for the VM', required=False)

    args = parser.parse_args()

    if not args.vm_name:
        raise exceptions.ArgMismatchException(
            "Must specify a vm name to add or delete.")

    if args.add:
        if not args.net:
            raise exceptions.ArgMismatchException(
                "Must specify net name or ID to create a VM.")
        ipnetns_vm.create_vm(args.vm_name, args.net, args.ip)
    elif args.delete:
        ipnetns_vm.delete_vm(args.vm_name, args.port_id)
    else:
        raise exceptions.ArgMismatchException(
            "Must specify action to either add (-a) or delete (-d) a VM.")


if __name__ == "__main__":
    main()
