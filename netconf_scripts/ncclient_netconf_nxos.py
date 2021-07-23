# ncclient script to get running config for NTP servers
from ncclient import manager
import difflib
import logging
import sys

# logging.basicConfig(filename='debug_nxos.log',level=logging.DEBUG)

def create_netconf_session(host, username, password, netconf_port=830):
    """ creates netconf session with the remote device"""
    try:
        netconf_session = manager.connect(host=host,
                                        port=netconf_port,
                                        username=username,
                                        password=password,
                                        hostkey_verify=False)

    except Exception as error: 
        sys.exit(error)

    return netconf_session


def get_capabilities(netconf_session, host):
    """ print all NETCONF supported capabilities """

    print('\n~~~~~ Supported Capabilities for {} ~~~~~\n'.format(host))
    for capability in netconf_session.server_capabilities:
        print(capability.split('?')[0])


def get_running_config(netconf_session, xml_filter):
    """ Gets intended running configurations with xml subtree filter """

    try:
        # To return the config in XML format (default)
        running_config = netconf_session.get_config(source='running', filter=xml_filter).data_xml

    except Exception as error: 
        sys.exit(error)

    return running_config

def replace_config(netconf_session, config):
    """ Replaces the part of running configurations 
        or set the desired state configuration
    """

    try:
        # To replace the config
        replaced_config = netconf_session.edit_config(target='running', config=config)

    except Exception as error: 
        sys.exit(error)

    return replaced_config

if __name__ == '__main__':

    # Remote device parameters define in dictionary format 
    device = {
        'host': 'sbx-nxos-mgmt.cisco.com',
        'netconf_port': 830,
        'username': 'admin',
        'password': 'Admin_1234!'
    }

    # Get config using the subtree filter in the body of the xml rpc
    xml_filter = '''
        <filter type="subtree" xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
                <time-items>
                    <prov-items>
                        <NtpProvider-list/>
                    </prov-items>
                </time-items>
            </System>
        </filter>
        '''

    # Updating NTP server configuration, using the "operation=replace"
    ntp_config = """
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
          <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
            <time-items>
              <prov-items operation="replace">
                <NtpProvider-list>
                  <name>172.16.1.11</name>
                  <keyId>1</keyId>
                  <maxPoll>6</maxPoll>
                  <minPoll>4</minPoll>
                  <preferred>false</preferred>
                  <provT>peer</provT>
                  <vrf>management</vrf>
                </NtpProvider-list>
                <NtpProvider-list>
                  <name>172.16.0.1</name>
                  <maxPoll>6</maxPoll>
                  <minPoll>4</minPoll>
                  <preferred>false</preferred>
                  <provT>server</provT>
                </NtpProvider-list>
              </prov-items>
            </time-items>
          </System>
        </config>
    """

    # Create a netconf session 
    netconf_session = create_netconf_session(**device)

    # Get the device netconf supported capabilities 
    # netconf_capabilities = get_capabilities(netconf_session, device['host'])
    # sys.exit(netconf_capabilities)

    # Get the current ntp servers config 
    ntp_config_current = get_running_config(netconf_session, xml_filter)
    # print(ntp_config_current)

    # Update the ntp servers config and set the desired state 
    ntp_config_desired = replace_config(netconf_session, config=ntp_config)

    # Get the updated config for NTP servers after above change
    ntp_config_updated = get_running_config(netconf_session, xml_filter)
    # print(ntp_config_updated)
    
    # comparing the output of the ntp configuration using difflib
    if ntp_config_updated != ntp_config_current:
        for lines in difflib.unified_diff(ntp_config_current.splitlines(), ntp_config_updated.splitlines(), lineterm=''):
            print(lines)
    else:
        print('No changes have been made!')


