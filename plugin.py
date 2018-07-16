"""
miio_domoticz Plugin

Author: fubar, 2018

Version:    1.0.0: Initial Release

"""

"""
<plugin key="miio_plugin" name="Xiaomi mi mini wifi controller" author="fubar"
  version="1.0.0" wikilink="http://www.domoticz.com/wiki/plugins/"
  externallink="">
     <description>
        <h3>----------------------------------------------------------------------</h3>
        <h2>miio mi mini plug wifi  v.1.0.1</h2><br/>
        <h2>Requires python-miio to be installed and working in your system python3</h2>
        <h2>When that's installed, use "miio discover" to discover the IP and token for your device</h2>
        <h3>----------------------------------------------------------------------</h3>
     </description>
     <params>
        <param field="Mode1" label="IP address" width="300px" required="true" default="your_device_IP_address"/>
        <param field="Mode2" label="Token" width="300px" required="true" default="your_device_token"/>
        <param field="Mode3" label="Poll interval (seconds)" width="100px" required="true" default="60"/>
        <param field="Mode4" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug"/>
                <option label="False" value="Normal"  default="True" />
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import miio
import json
from datetime import datetime
from datetime import timedelta
from time import sleep

icons = {}

# status returns <ChuangmiPlugStatus power=True, usb_power=None, temperature=39load_power=None, wifi_led=None>


class BasePlugin:

    def __init__(self):
        self.myip = Parameters["Mode1"]
        self.mytoken = Parameters["Mode2"]
        self.myplug = miio.chuangmi_plug.ChuangmiPlug(ip=self.myip,token=self.mytoken)
        self.debug = False
        self.nextupdate = datetime.now()
        self.pollinterval = 60  # default polling interval in minutes
        self.error = False
        self.reload = True
        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        if Parameters["Mode4"] == 'Debug':
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()
        else:
            Domoticz.Debugging(0)
        self.stat = self.myplug.status()
        self.power = self.stat.power 
        self.temperature = self.stat.temperature
        self.load_power = self.stat.load_power
        self.usb_power = self.stat.usb_power
        self.wifi_led = self.stat.wifi_led

        # create the mandatory child device if it does not yet exist
        if 1 not in Devices:
            Domoticz.Device(Name="miio_plugin", Unit=1, TypeName="Custom",Options={"Custom": "1;Power"},Used=1).Create()
        # check polling interval parameter
        try:
            polli = int(Parameters["Mode3"])
        except:
            Domoticz.Error("Invalid polling interval parameter")
        else:
            if polli < 60:
                polli = 60  # minimum polling interval
                Domoticz.Error("Specified polling interval too short: changed to 60 minutes")
            elif polli > 1440:
                polli = 1440  # maximum polling interval is 1 day
                Domoticz.Error("Specified polling interval too long: changed to 1440 minutes (24 hours)")
            self.pollinterval =  polli
        Domoticz.Log("Using polling interval of {} minutes".format(str(self.pollinterval)))

    def onStop(self):
        Domoticz.Debug("onStop called")
        Domoticz.Debugging(0)

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        now = datetime.now()
        if now >= self.nextupdate:
            self.nextupdate = now + timedelta(minutes=self.pollinterval)
            self.stat = self.myplug.status()
            self.power = self.stat.power 
            self.temperature = self.stat.temperature
            self.load_power = self.stat.load_power
            self.usb_power = self.stat.usb_power
            self.wifi_led = self.stat.wifi_led
            Domoticz.Debug('miio plugin status: %s' % self.stat)


    def UpdateDevice(self, turn_on=False):
        Domoticz.Debug("UpdateDevice called")
        # Make sure that the Domoticz device still exists (they can be deleted) before updating it
        if 1 in Devices:
            if turn_on:
                self.myplug.on()
            else:
                self.myplug.off()
            sleep(1)
            self.stat = self.myplug.status()
            if self.stat.power:
                is_on = 'On'
            else:
                is_on = 'Off' 
            titl = "1;status, %s" % is_on
            Domoticz.Debug("Setting Custom to" + titl)
            try:
               Devices[1].Update(nValue=0,  sValue=is_on, Options={"Custom": titl})
            except:
               Domoticz.Error("Failed to update device unit 1 with values %s:%s:" % (lune,luneage))

        return



global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug("'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
    return
