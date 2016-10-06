
import atexit
from pyVim import connect
from pyVmomi import vim,vmodl

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

    parser.add_argument('-o', '--port',
                        required=False,
                        action='store',
                        help="port to use, default 443", default=443)

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use when connecting to host')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use when connecting to host')


    args = parser.parse_args()
    if args.password is None:
        args.password = getpass.getpass(
            prompt='Enter password for host %s and user %s: ' %
                   (args.host, args.user))
    return args


# Change vmware lun policy path to one of 'VMW_PSP_FIXED' 'VMW_PSP_RR' 'VMW_PSP_MRU'
def  change_lun_manage_path_policy(storage_system,manage_policy,lunsubstr):
    result= True

    policy_values=['VMW_PSP_FIXED' ,'VMW_PSP_RR', 'VMW_PSP_MRU']
    if not manage_policy in policy_values:
        result = False
        return (result)

    luns=storage_system.storageDeviceInfo.multipathInfo.lun
    for lun in luns:
        if  (lunsubstr) in lun.path[0].name:
            mpolicy=vim.host.MultipathInfo.LogicalUnitPolicy()
            mpolicy.policy=manage_policy
            try:
                storage_system.SetMultipathLunPolicy(lun.id,mpolicy)
                print('lun '+lun.path[0].name+' change policy to '+manage_policy+' was completed')
            except :
                print('lun '+lun.path[0].name+' change policy to '+manage_policy+' Failed')
    return (result)


def print_lun_summary(storage_system):
       luns=storage_system.storageDeviceInfo.multipathInfo.lun
       for lun in luns:
            print("{}\t{}\t\n".format("lun id:    ", lun.id))
            print("{}\t{}\t\n".format("lun :    ", lun.lun))
            print("{}\t{}\t\n".format("path name :    ",  lun.path[0].name))
            print("{}\t{}\t\n".format("path state :    ", lun.path[0].state))
            print("{}\t{}\t\n".format("lun policy:    ", lun.policy.policy))
            print('\n')


def main():
    """
    Simple command-line program to change esxi luns policy
    """
    args = get_args()

    print(args)
    s = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
    s.verify_mode = ssl.CERT_NONE
    try:
        service_instance = connect.SmartConnect(host=args.host,
                                                user=args.user,
                                                pwd=args.password,
                                                port=args.port,
                                                sslContext=s)

        atexit.register(connect.Disconnect, service_instance)

        content = service_instance.RetrieveContent()
        # Search for all ESXi hosts
        objview = content.viewManager.CreateContainerView(content.rootFolder,
                                                          [vim.HostSystem],
                                                          True)
        esxi_hosts = objview.view
        objview.Destroy()

        for esxi_host in esxi_hosts:
            print(" \n")
            print("{}\t{}\t\n".format("ESXi Host:    ", esxi_host.name))

            # All Filesystems on ESXi host
            storage_system = esxi_host.configManager.storageSystem

            print(" ---- before the change  \n")
            print_lun_summary(storage_system)
            # change the lun policy
            lunsubstr='vmhba1:C0:T3:L0'  #sub string of lun name that need to update
            manage_policy='VMW_PSP_RR'   #'VMW_PSP_FIXED' 'VMW_PSP_RR' 'VMW_PSP_MRU'
            change_lun_manage_path_policy(storage_system,manage_policy,lunsubstr)
            print(" ---- after the change  \n")
            print_lun_summary(storage_system)

    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()

