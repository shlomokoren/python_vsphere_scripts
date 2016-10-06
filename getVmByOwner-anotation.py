#!/usr/bin/env python
# VMware vSphere Python SDK
# Copyright (c) 2008-2013 VMware, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Python program for listing the vms base on owner in anotation on an ESX / vCenter host
The anotation have to include Owner:[ownername]

"""

import atexit

from pyVim import connect
from pyVmomi import vmodl
from pyVmomi import vim
import ssl
import argparse
import getpass

__author__ =  'Momo'

def get_args():
    parser = argparse.ArgumentParser(description='Script change esxi servers lun policy')

    parser.add_argument('-s', '--host',
                        required=True,
                        action='store',
                        help='Remote host to connect to')

    parser.add_argument('-p', '--port',
                        required=False,
                        action='store',
                        help="port to use, default 443",
                        default=443)

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-P', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')
    parser.add_argument('-o', '--owner',
                        required=True,
                        action='store',
                        help='virtual machine owner ')


    args = parser.parse_args()
    if args.password is None:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args



def print_vm_info(virtual_machine,owner):
    """
    Print information for a particular virtual machine or recurse into a
    folder with depth protection

    """
    summary = virtual_machine.summary
    annotation = summary.config.annotation
    if annotation:
        if 'owner:'+owner in annotation.lower():
            print("Annotation : ", annotation)
            print("Name       : ", summary.config.name)
            print("Template   : ", summary.config.template)
            print("Path       : ", summary.config.vmPathName)
            print("Guest      : ", summary.config.guestFullName)
            print("Instance UUID : ", summary.config.instanceUuid)
            print("Bios UUID     : ", summary.config.uuid)
            print("State      : ", summary.runtime.powerState)
            if summary.guest is not None:
                ip_address = summary.guest.ipAddress
                tools_version = summary.guest.toolsStatus
                if tools_version is not None:
                    print("VMware-tools: ", tools_version)
                else:
                    print("Vmware-tools: None")
                if ip_address:
                    print("IP         : ", ip_address)
                else:
                    print("IP         : None")
            if summary.runtime.question is not None:
                print("Question  : ", summary.runtime.question.text)
            print("")


def main():
    """
    Simple command-line program for listing the virtual machines on a system.
    """


    args = get_args()

    s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    s.verify_mode = ssl.CERT_NONE
    try:
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=443,
                                                sslContext=s)

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()

        container = content.rootFolder  # starting point to look into
        viewType = [vim.VirtualMachine]  # object types to look for
        recursive = True  # whether we should look into it recursively
        containerView = content.viewManager.CreateContainerView(
            container, viewType, recursive)

        children = containerView.view
        for child in children:
            print_vm_info(child,args.owner)

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()
