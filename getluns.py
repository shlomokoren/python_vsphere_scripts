import atexit

from pyVim import connect
#from pyVmomi import vmodl
from pyVmomi import vim
import ssl

# first commit
# noinspection PyPackageRequirements
import tools.cli_momo as cli
def change_lun_Multipath_to_VMW_PSP_MRU(storage_system):
       luns=storage_system.storageDeviceInfo.multipathInfo.lun
       for lun in luns:
           if not (':T0') in lun.path[0].name:
              mpolicy=vim.host.MultipathInfo.LogicalUnitPolicy()   #'VMW_PSP_FIXED' 'VMW_PSP_RR' 'VMW_PSP_MRU'
              mpolicy.policy='VMW_PSP_MRU'
              storage_system.SetMultipathLunPolicy(lun.id,mpolicy)

def change_lun_Multipath_to_VMW_PSP_FIXED(storage_system):
       luns=storage_system.storageDeviceInfo.multipathInfo.lun
       for lun in luns:
           if not (':T0') in lun.path[0].name:
              mpolicy=vim.host.MultipathInfo.LogicalUnitPolicy()   #'VMW_PSP_FIXED' 'VMW_PSP_RR' 'VMW_PSP_MRU'
              mpolicy.policy='VMW_PSP_FIXED'
              storage_system.SetMultipathLunPolicy(lun.id,mpolicy)

def change_lun_Multipath_to_VMW_PSP_RR(storage_system):
       luns=storage_system.storageDeviceInfo.multipathInfo.lun
       for lun in luns:
           if not (':T0') in lun.path[0].name:
              mpolicy=vim.host.MultipathInfo.LogicalUnitPolicy()   #'VMW_PSP_FIXED' 'VMW_PSP_RR' 'VMW_PSP_MRU'
              mpolicy.policy='VMW_PSP_RR'
              storage_system.SetMultipathLunPolicy(lun.id,mpolicy)



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
    Simple command-line program for listing the virtual machines on a system.
    """

    args = cli.ConnectVars()
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

            print_lun_summary(storage_system)
            #change_lun_Multipath_to_VMW_PSP_MRU(storage_system)
            #change_lun_Multipath_to_VMW_PSP_FIXED(storage_system)
            change_lun_Multipath_to_VMW_PSP_RR(storage_system)
            print(" ---- after change  \n")
            print_lun_summary(storage_system)




    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()

