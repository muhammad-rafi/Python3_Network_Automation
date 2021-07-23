# ncclient script to configure the desired state for the NTP servers 
from ncclient import manager

device = {
    'host': 'sbx-nxos-mgmt.cisco.com',
    'username': 'admin',
    'password': 'Admin_1234!',
    'port': 830,
    'hostkey_verify': False
}

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

ntp_config = """
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
        <time-items>
          <prov-items operation="replace">
            <NtpProvider-list>
              <name>172.16.1.12</name>
              <keyId>1</keyId>
              <maxPoll>6</maxPoll>
              <minPoll>4</minPoll>
              <preferred>false</preferred>
              <provT>peer</provT>
              <vrf>management</vrf>
            </NtpProvider-list>
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

conn = manager.connect(**device)

# # To get the operational and configuration data
# get_ntp_config = conn.get(xml_filter)
# print(get_ntp_config.data_xml)

# # To get the configuration data only
# get_ntp_config = conn.get_config(source='running', filter=xml_filter)
# print(get_ntp_config.data_xml)

config_changed = conn.edit_config(config=ntp_config, target="running")
print(config_changed.xml)
conn.close_session()
