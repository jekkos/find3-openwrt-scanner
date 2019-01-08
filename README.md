# find3-openwrt-scanner #
This folder contains a couple of scripts that can be used with an OpenWrt router and turn it into as a [find3](https://www.internalpositioning.com) cli scanner.

All of this runs on two [GLiInet b-1300 model](https://www.gl-inet.com/products/gl-b1300/) routers running a nightly snapshot build.

The setup consists of a monitor interface on which tcpdump will log probe requests, which will be submitted by a pythnon script to the 
find3 server backend.

## Requirements ##

First make sure you find a usb dongle that has monitor mode enabled on OpenWrt. For this I used an rtl8192cu chipset. 
These are tiny, cheap and small and can be ordered in your local electronics shop.

You can choose to run the scanner using `airodump-ng` or `tcpdump`. The procd initialization script only supports the latter.
Initially I wanted to use airodump but for some reason it always stopped the packet capture (probably a driver issue).

## Configuration ##

### Wireless ###

* To enable the dongle in OpenWrt, first install the wifi driver using `opkg install kmod-rtl8192cu`
* Next you need to tell OpenWrt userspace that you want to use this dongle in monitor mode by typing `wifi config`.
This will add the needed config section to the `/etc/config/wireless` configuration file. Now open this file with your editor of choice.

* Enable the dongle by setting the `disabled` flag to 0 for the newly created interface
* Change the mone line  `mode 'monitor'` to enable monitor mode. Remove all lines related to authentication (key, ssid, encryption)
* Start the interface by `wifi up <radio2>`. You should see the packet count increasing when typing `ifconfig`
* Don't forget to replace the last value with the interface name that was added in the config file.

### tcpdump + python scanner ###
* you need to setup tcpdump and the needed python packages so you can submit fingerprints to the find3 server. Enter following commnad `opkg install tcpdump python3-codecs python3-light python3-email python3-openssl`
* adapt the `URL` and `FAMILY` variables in the `find3_scanner` procd script and copy it to `/etc/init.d` on the router using scp.
* type `/etc/init.d/find3_scanner enable` to enable it on startup.

To make the tcpdump output available for the python script, configure `/etc/config/system` as follows

```
config system
  option log_file '/tmp/logfile'
```

Log output can be monitored using `logread` in the router's SSH session.

### airodump-ng + python scanner ###
This setup might give you more control on how the wifi driver behaves in monitor mode by using specific airodump-ng parameters.

* first install aircrack suite using `opkg install aircrack-ng python3-codecs python3-light python3-email python3-openssl`
* next start a monitor interface `sudo airmong-ng start <interface>`
* then start airodump-ng and write the results to an output file `sudo airodump-ng wlan1mon --output-format csv -w /tmp/dump.csv`
* next you can start the airodump script using `python3 airodumpscan.py -f <family> -i /tmp/dump.csv`

### Setup collectd ###
Finally, not needed for find3 but nice as an addon to use with grafana and influxdb

```
opkg install collectd-mod-network collectd-mod-uptime collectd-mod-interface collectd-mod-memory collectd-mod-cpu collectd-mod-load collectd-mod-iwinfo
/etc/init.d/collectd enable
```
