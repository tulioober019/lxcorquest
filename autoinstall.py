# * Este script autoinstala os contenedores, perfís e redes. * #

import json as js
import argparse as arg
import os

def proyect_config():
    try:
        file = open("config.json","r")
        file_data = js.load(file)
        return file_data
    
    except:
        return 0

def init_proyect():
    os.system("touch " + os.getcwd() + "/config.json")

def create_networks():
    network_data = proyect_config()[0]['networks']

    for net in network_data:
        net_name = net['name']

        net_args = ""

        net_config_ipv4_enabled = net['config']['ipv4']['enable']
        net_config_ipv6_enabled = net['config']['ipv6']['enable']

        # If ipv4 settings are enabled.
        if net_config_ipv4_enabled == True:
            net_config_ipv4_address = net['config']['ipv4']['address']
            net_config_ipv4_dhcp_enabled = net['config']['ipv4']['dhcp']['enable']

            net_args += " ipv4.nat=true ipv4.address=" + net_config_ipv4_address + " ipv4.dhcp=true" #+ str(net_config_ipv4_dhcp_enabled).translate(str.maketrans("T","t")).translate(str.maketrans("F","f"))

            if net_config_ipv4_dhcp_enabled == True:
                net_config_ipv4_dhcp_range_start = net['config']['ipv4']['dhcp']['range']['start']
                net_config_ipv4_dhcp_range_end = net['config']['ipv4']['dhcp']['range']['end']
                
                net_args += " ipv4.dhcp.ranges=" + net_config_ipv4_dhcp_range_start + "-" + net_config_ipv4_dhcp_range_end


        # If ipv6 settings are enabled. 
        if net_config_ipv6_enabled == True:
            net_config_ipv6_address = net['config']['ipv6']['address']
            net_config_ipv6_dhcp_enabled = net['config']['ipv6']['dhcp']['enable']

            net_args += " ipv6.nat=true ipv6.address=" + net_config_ipv6_address + " ipv6.dhcp=true" #+ str(net_config_ipv6_dhcp_enabled).translate(str.maketrans("T","t")).translate(str.maketrans("F","f"))

            if net_config_ipv6_dhcp_enabled == True:
                net_config_ipv6_dhcp_range_start = net['config']['ipv6']['dhcp']['range']['start']
                net_config_ipv6_dhcp_range_end = net['config']['ipv6']['dhcp']['range']['end']

                net_args += " ipv6.dhcp.ranges=" + net_config_ipv6_dhcp_range_start + "-" + net_config_ipv6_dhcp_range_end

        #print("lxc network create " + net_name + net_args)

        print("Creando a rede " + net_name)
        os.system("lxc network create " + net_name + net_args)
        os.system("lxc network set " + net_name + " -p description=\"" + net['description'] + "\"")

def create_profiles():
    profile_data = proyect_config()[0]['profiles']

    for profile in profile_data:
        # Generacion de los perfiles.
        os.system("lxc profile copy default " + profile['name'])

        # Anidacion da descricion.
        os.system("lxc profile set " +  profile['name'] + " -p description=\"" + profile['description'] + "\"")

        os.system("lxc profile device remove " + profile['name'] + " eth0")

        # Configuración das interfaces de rede.
        for net in profile['network']:

            net_name = ""

            for network in proyect_config()[0]['networks']:
                if network['id'] == net['net']:
                    net_name = network['name']

            os.system("lxc profile device add " + profile['name'] + " " + net['adapter'] + " nic name=" + net['adapter'] + " network=" + net_name)

            #os.system("lxc profile device set " + profile['name'] + " " + net['adapter'] + " ipv4.gateway=" + net['gateway'])

        # Configuracion do hardware.
        
        #os.system("lxc profile  set " + profile['name'] + " limits.cpu=" + str(profile['hardware']['cpu']['cores']))

        #os.system("lxc profile  set " + profile['name'] + " limits.memory=" + str(profile['hardware']['memory']['limit']))

def create_machines():
    machine_data = proyect_config()[0]['servers']

    for machine in machine_data:

        profile_name = ""
        for prof in proyect_config()[0]['profiles']:
            if prof['id'] == machine['profile']:
                profile_name = prof['name']

        os.system("lxc launch " + machine['os'] + " " + machine['name'] + " --profile=" + profile_name)

        # IP assigment.

        for interface in machine['network']:

            if interface['config'] == "static":
                if interface['ipv4']['enable'] == True:
                    os.system("lxc config device override " + machine['name'] + " " + interface['adapter'] + " ipv4.address=" + interface['ipv4']['address'])
                    #os.system("lxc config device override " + machine['name'] + " " + interface['adapter'] + " ipv4.gateway=" + interface['ipv4']['gateway'])

                if interface['ipv6']['enable'] == True:
                    os.system("lxc config device override " + machine['name'] + " " + interface['adapter'] + " ipv6.address=" + interface['ipv6']['address'])
                    #os.system("lxc config device override " + machine['name'] + " " + interface['adapter'] + " ipv6.gateway=" + interface['ipv6']['gateway'])

        os.system("lxc restart " + machine['name'])

        # Machine provisioning.

        for command in machine['provision']:
            os.system("lxc exec " + machine['name'] + " " + command)
            
        # Profile assigment.
        #os.system("lxc profile remove " + machine['name'] + " default")
        #os.system("lxc profile add " + machine['name'] + " " + profile_name)

def deploy_project():
    # Network deployment.
    create_networks()

    # Machine deployment
    create_profiles()

    # Machine deployment
    create_machines()

    

def destroy_proyect():
    machine_data = proyect_config()[0]['servers']
    for machine in machine_data:
        os.system("lxc delete " + machine['name'] + " --force")

    profile_data = proyect_config()[0]['profiles']
    for profile in profile_data:
        os.system("lxc profile delete " + profile['name'])
        
    network_data = proyect_config()[0]['networks']
    for net in network_data:
        os.system("lxc network delete " + net['name'])


def main():
    parser = arg.ArgumentParser(
        prog='Autoinstall',
        description='Autoinstall'
    )

    subparser = parser.add_subparsers(dest='subcommand', help='Available subcommands')
    subparser.add_parser('init',help='Initiates a config.json file')
    subparser.add_parser('deploy',help='Deploys a proyect')
    subparser.add_parser('destroy',help='Deploys a proyect')

    args = parser.parse_args()

    if args.subcommand == 'init':
        init_proyect()
        print("Initiating a config file in root directory.")
    
    elif args.subcommand == 'deploy':
        deploy_project()
        print("Deploying proyect!")
    
    elif args.subcommand == 'destroy':
        destroy_proyect()
        print("Destroying proyect!")
    
    else:
        print("Subcommand dosent exist")

main()