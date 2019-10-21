import dns.resolver
import requests
import json
import os
import datetime
import time
import sys
import uuid
from urllib.request import urlopen
from bs4 import BeautifulSoup
from Firepower import Firepower

# Config Paramters
CONFIG_FILE     = "config_file.json"
CONFIG_DATA     = None

DoH_IP_ADDRESSES = []

# A function to load CONFIG_DATA from file
def loadConfig():

    global CONFIG_DATA

    print("\n")
    print("Loading config data...")
    print("\n")

    # If we have a stored config file, then use it, otherwise create an empty one
    if os.path.isfile(CONFIG_FILE):

        # Open the CONFIG_FILE and load it
        with open(CONFIG_FILE, 'r') as config_file:
            CONFIG_DATA = json.loads(config_file.read())

        print("Config loading complete.")
        print("\n")
        print("\n")

    else:

        print("Config file not found, loading empty defaults...")
        print("\n")
        print("\n")

        # Set the CONFIG_DATA defaults
        CONFIG_DATA = {
            "FMC_IP": "",
            "FMC_USER": "",
            "FMC_PASS": "",
            "DoH_UUID": "",
            "SERVICE": false,
            "SSL_VERIFY": false,
            "SSL_CERT": "/path/to/certificate",
            "AUTO_DEPLOY": false
        }

# A function to store CONFIG_DATA to file
def saveConfig():

    print("Saving config data...")
    print("\n")

    with open(CONFIG_FILE, 'w') as output_file:
        json.dump(CONFIG_DATA, output_file, indent=4)

# A function to deploy pending policy pushes
def DeployPolicies(fmc):

    # Get pending deployments
    pending_deployments = fmc.getPendingDeployments()

    # Setup a dict to hold our deployments
    deployments = {}

    # See if there are pending deployments
    if pending_deployments['paging']['count'] > 0:

        # Iterate through pending deployments
        for item in pending_deployments['items']:

            # Only get ones that can be deployed
            if item['canBeDeployed']:

                # Only get ones that don't cause traffic interruption
                if item['trafficInterruption'] == "NO":

                    # If there are multiple devices, append them
                    if item['version'] in deployments:
                        device_list = deployments[item['version']]
                        device_list.append(item['device']['id'])
                        deployments[item['version']] = device_list
                    else:
                        deployments[item['version']] = [item['device']['id']]

        # Build JSON for each of our deployments
        for version, devices in deployments.items():

            deployment_json = {
                "type": "DeploymentRequest",
                "version": version,
                "forceDeploy": False,
                "ignoreWarning": True,
                "deviceList": devices,
            }

            fmc.postDeployments(deployment_json)

        print("All pending deployments have been requested.\n")
    
    else:

        print("There were zero pending deployments.\n")

# Function that can be used to schedule the O365WebServiceParser to refresh at intervals. Caution: this creates an infinite loop.
# Takes the O365WebServiceParser function and the interval as parameters. 
def intervalScheduler(function, interval):

    # user feedback
    print("\n")
    print(f"DoH IP Parser will be refreshed every {interval} seconds. Please use ctrl-C to exit.\n")
    print("\n")

    # interval loop, unless keyboard interrupt
    try:
        while True:
            function()
            # get current time, for user feedback
            date_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print("\n")
            print(f"{date_time} DoH IP Parser executed by IntervalScheduler, current interval is {interval} seconds. Please use ctrl-C to exit.\n")
            print("\n")
            # sleep for X amount of seconds and then run again. Caution: this creates an infinite loop to check the Web Service Feed for changes
            time.sleep(interval)

    # handle keyboard interrupt
    except (KeyboardInterrupt, SystemExit):
        print("\n")
        print("\n")
        print("Exiting... DoH IP Parser will not be automatically refreshed anymore.\n")
        print("\n")
        sys.stdout.flush()
        pass

def parse_doh_list():
    doh_overview_link = "https://github.com/curl/curl/wiki/DNS-over-HTTPS"
    # retrieve text with html parser
    html = urlopen(doh_overview_link).read()
    soup = BeautifulSoup(html, "html.parser")

    doh_domains = []

    # super ugly parsing function.... please change to regex (but be careful to only grab the href domains), it works though....
    for table in soup(["tbody"]):
        for row in table(["tr"]):
            for index, data in enumerate(row(["td"])):
                if index == 1:
                    string_td = (str(data))
                    split_string_td = string_td.split()
                    for item in split_string_td:
                        if item.startswith('href="https://'):
                            stripped_item = item.strip('href="https://')
                            for index, char in enumerate(stripped_item):
                                if char == '/':
                                    doh_domains.append(stripped_item[:index])
                                    break
        break

    for domain in doh_domains:
        try:
            dns_a_records = dns.resolver.query(domain,'A')
            if dns_a_records:
                for a_server in dns_a_records:
                    DoH_IP_ADDRESSES.append(str(a_server))
        except:
            print(f"No IPv4 record for: {domain}.")
        
        try:
            dns_aaaa_records = dns.resolver.query(domain,'AAAA')
            if dns_aaaa_records:
                for aaaa_server in dns_aaaa_records:
                    DoH_IP_ADDRESSES.append(str(aaaa_server))
        except:
            print(f"No IPv6 record for: {domain}.")

    return DoH_IP_ADDRESSES

def upload_to_fmc(DoH_IP_ADDRESSES):
    
    # Instantiate a Firepower object
    fmc = Firepower(CONFIG_DATA)

    # If there's no defined Network Object, make one, then store the UUID - else, get the current object
    if CONFIG_DATA['DoH_UUID'] is '':

        # Create the JSON to submit
        object_json = {
            'name': 'DoH_IP_Addresses',
            'type': 'NetworkGroup',
            'overridable': True,
        }

        # Create the Network Group object in the FMC
        DoH_group_object = fmc.createObject('networkgroups', object_json)

        # Save the UUID of the object
        CONFIG_DATA['DoH_UUID'] = DoH_group_object['id']
        saveConfig()
    else:
        # Get the Network Group object of the specified UUID
        DoH_group_object = fmc.getObject('networkgroups', CONFIG_DATA['DoH_UUID'])

    # Reset the fetched Network Group object to clear the 'literals'
    DoH_group_object['literals'] = []
    DoH_group_object.pop('links', None)

    # Add all the fetched IPs to the 'literals'of the Network Group object
    for ip_address in DoH_IP_ADDRESSES:
        DoH_group_object['literals'].append({'type': 'Network', 'value': ip_address})

    # Update the NetworkGroup object
    fmc.updateObject('networkgroups', CONFIG_DATA['DoH_UUID'], DoH_group_object)

     # user feed back
    print("\n")
    print(f"DoH IP addresses have been successfully updated to FMC!\n")
    print("\n")

    saveConfig()

    # If the user wants us to deploy policies, then do it
    if CONFIG_DATA['AUTO_DEPLOY']:
        DeployPolicies(fmc)

if __name__ == "__main__":

    # Load config data from file
    loadConfig()

    # Save the FMC data
    saveConfig()

    try:
        if CONFIG_DATA['SERVICE']:
            # Calls the intervalScheduler for automatic refreshing (pass O365WebServiceParser function and interval in seconds (1 hour = 3600 seconds))
            intervalScheduler(upload_to_fmc, 3600) #set to 1 hour
        else:
            # Execute O365WebServiceParser just once
            DoH_IP_ADDRESSES = parse_doh_list()
            upload_to_fmc(DoH_IP_ADDRESSES)

    except (KeyboardInterrupt, SystemExit):
        print("\n\nExiting...\n\n")
        sys.stdout.flush()
        pass
