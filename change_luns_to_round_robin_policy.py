
import atexit
from pyVim import connect
from pyVmomi import vim
import ssl
# Owner : Momo
#version 0.01b
import tools.cli_momo as cli



# Change vmware lun policy path   to 'VMW_PSP_FIXED' 'VMW_PSP_RR' 'VMW_PSP_MRU'
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
            # change the lun policy
            #change_lun_Multipath_to_VMW_PSP_MRU(storage_system)
            #change_lun_Multipath_to_VMW_PSP_FIXED(storage_system)
            #change_lun_Multipath_to_VMW_PSP_RR(storage_system)
            lunsubstr='vmhba1:C0:T3:L0'  #sub string of lun name that need to update
            manage_policy='VMW_PSP_RR'
            change_lun_manage_path_policy(storage_system,manage_policy,lunsubstr)
            print(" ---- after change  \n")
            print_lun_summary(storage_system)





    except vmodl.MethodFault as error:
        print("Caught vmodl fault : " + error.msg)
        return -1

    return 0

# Start program
if __name__ == "__main__":
    main()

