import time
from configuration import Configuration
from util import singleton

import network
from rtc import RTC
import time
import ntptime
import localPTZtime

@singleton
class WLAN:
    def __init__(self, scheduler):
        self.scheduler = scheduler
        self.configuration = Configuration().wifi_config
        self.wlan = None
        self.rtc = RTC()
        if self.configuration.enabled:
            self.connect_to_wifi()

    def connect_to_wifi(self):
        import network
        print("Connecting to WiFi")
        #network.hostname(self.configuration.hostname)
        self.wlan = network.WLAN(network.STA_IF)

        self.wlan.active(True)
        self.wlan.config(pm=0xa11140)  # type: ignore - Disable powersave mode
        self.wlan.connect(self.configuration.ssid,
                          self.configuration.passphrase)

        # Wait for connect or fail
        max_wait = 20
        while max_wait > 0:
            if self.wlan.status() < 0 or self.wlan.status() >= 3:
                break
            max_wait -= 1
            print('Waiting for connection...')
            time.sleep(1)

        # Handle connection error
        if self.wlan.status() != 3:
            raise RuntimeError('WiFi connection failed')
        else:
            status = self.wlan.ifconfig()
            print('IP = ' + status[0])

            if self.configuration.ntp_enabled:
                if self.configuration.ntp_host != "":
                    ntptime.host = self.configuration.ntp_host
                    print("Using NTP Host: " + self.configuration.ntp_host)
                try:
                    ntptime.settime()
                    local_time= localPTZtime.tztime(time.time(), self.configuration.ntp_ptz)
                    self.rtc.save_time(local_time[:8])
                except:
                    print("Could not sync time via NTP")
