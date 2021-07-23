# scrapli script to configure the desired state for the NTP servers
from scrapli_netconf.driver import NetconfDriver

device = {
    "host": "sbx-nxos-mgmt.cisco.com",
    "auth_username": "admin",
    "auth_password": "Admin_1234!",
    "auth_strict_key": False,
    "port": 830
}

xml_filter = '''
   <System xmlns="http://cisco.com/ns/yang/cisco-nx-os-device">
      <time-items>
         <prov-items>
            <NtpProvider-list />
        </prov-items>
      </time-items>
   </System>
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

conn = NetconfDriver(**device)
conn.open()

# To get the operational and configuration data
get_ntp_config = conn.get(filter_=xml_filter, filter_type='subtree')
print(get_ntp_config.result)

# To get the configuration data only
get_ntp_config = conn.get_config(source="running", filters=xml_filter, filter_type='subtree')
print(get_ntp_config.result)

config_changed = conn.edit_config(config=ntp_config, target="running")
print(config_changed.result)
conn.close()

