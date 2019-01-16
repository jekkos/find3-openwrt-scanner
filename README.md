# find3-openwrt-scanner #
This folder contains a couple of scripts that can be used with an OpenWrt router and turn it into as a [find3](https://www.internalpositioning.com) cli scanner.

All of this runs on two [GLiInet b-1300 model](https://www.gl-inet.com/products/gl-b1300/) routers running a nightly snapshot build.

The setup consists of a monitor interface on which tcpdump will log probe requests, which will be submitted by a pythnon script to the 
find3 server backend.

## Requirements ##

First make sure you find a usb dongle that has monitor mode enabled on OpenWrt. For this I used an rtl8192cu chipset. 
These are tiny, cheap and small and can be ordered in your local electronics shop. For example a 8188cus dongle should work.

You can choose to run the scanner using `airodump-ng` or `tcpdump`. 
Initially I wanted to use airodump but for some reason it always stopped the packet capture (probably a driver issue). This issue was caused
by the alternative ieee80211 rtl8xxx linux driver that did not seem to be very stable for my specific hardware.

## Configuration ##

### wireless driver + monitor mode ###
To enable the dongle in OpenWrt, first install the wifi driver 

* In my case I installed the driver using `opkg install kmod-rtl8192cu`. 
* Next you need to tell OpenWrt userspace that you want to use this dongle in monitor mode by typing `wifi config`.
This will add the needed config section to the `/etc/config/wireless` configuration file. Now open this file with your editor of choice.

* Enable the dongle by setting the `disabled` flag to 0 for the newly created interface
* Change the `mode` line to `mode 'monitor'` to enable monitor mode. Remove all lines related to authentication (`key`, `ssid`, `encryption`)
* Start the interface by `wifi up <radio2>`. You should see the packet count increasing when typing `ifconfig`
* Don't forget to replace the last value with the interface name that was added in the config file.

### tcpdump + python scanner ###
You need to setup tcpdump and the needed python packages so you can submit fingerprints to the find3 server. 

* Enter following commnad `opkg install tcpdump python3-codecs python3-light python3-email python3-openssl`
* Adapt the `URL` and `FAMILY` variables and Copy the `tcpdumpscan` procd init script to `/etc/init.d` using scp.
* Finally type `/etc/init.d/tcpdumpscan enable` to enable both on startup.

Log output can be monitored using `logread` in the router's SSH session.

### airodump-ng + python scanner ###
This setup might give you more control on how the wifi driver behaves in monitor mode by using specific airodump-ng parameters.

* First install aircrack suite `opkg install aircrack-ng python3-codecs python3-light python3-email python3-openssl`
* Adapt the `URL` and `FAMILY` variables and Copy the `airodump` and `airodumpscan` procd init scripts to `/etc/init.d` using scp.

* Finally type `/etc/init.d/airodump enable` and `/etc/init.d/airodumpscan enable` to enable both on startup.

### Setup collectd ###
Not needed for find3 but nice as an addon to use with grafana and influxdb

```
opkg install collectd-mod-network collectd-mod-uptime collectd-mod-interface collectd-mod-memory collectd-mod-cpu collectd-mod-load collectd-mod-iwinfo
/etc/init.d/collectd enable
```
