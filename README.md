# find3-openwrt-scanner #
This folder contains a couple of scripts that can be used with an OpenWrt router and turn it into as a [find3](https://www.internalpositioning.com) cli scanner.

All of this runs on two [GLiInet b-1300 model](https://www.gl-inet.com/products/gl-b1300/) routers running a custom snapshot build.

The setup consists of a monitor interface on which tcpdump will log probe requests, which will be submitted by a pythnon script to the 
find3 server backend.

## Requirements ##

First make sure you find a usb dongle that has monitor mode enabled on OpenWrt. For this I used an rtl8192cu chipset which can be found
in those rtl8818cus dongles, which became very popular for use with a raspberry pi.  

You can choose to run the scanner using `airodump-ng` or `tcpdump`. 
Initially I wanted to use airodump but for some reason it always stopped the packet capture (probably a driver issue). This issue was caused
by the alternative ieee80211 rtl8xxx linux driver that did not seem to be very stable for my specific hardware.

The scripts can now also be installed using a prepackaged ipk added here in the [release](https://github.com/jekkos/find3-openwrt-scanner/releases/tag/v1) section.

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

## Installation ##
Over time I tried three different setups. The most stable (and recommended one) is the *tcpdumpscan + ash scanner* variant. This is also
the version that is packaged and available for download under the release section.

### tcpdump + ash scanner ###
If you are on a more constrained device, then using OpenWrt binaries + some shell scripts might be most appropriate. In my case WR703n router
was not powerful enough to run the scripts in python3. Only dependencies here are libubox (preinstalled), tcpdump and curl

* Install curl + tcpdump using `opkg update && opkg install tcpdump curl` on the device.
* Copy the `find3_1_all.ipk` file in the (release)[https://github.com/jekkos/find3-openwrt-scanner/releases/tag/v1] section to the device using `scp find3_1_all.ipk root@<ip>:/tmp
* Open an SSH session to the device and install using `opkg install /tmp/find3_1_all.ipk'
* Adapt the `URL` and `FAMILY` variables in `/etc/config/tcpdumpscan`.
* Hit `/etc/init.d/tcpdumpscan restart` to start scanning.
* Finally type `/etc/init.d/tcpdumpscan enable` to enable scanning on startup.

### tcpdump + python scanner ###
You need to setup tcpdump and the needed python packages so you can submit fingerprints to the find3 server. Currently I have not foreseen an .ipk for this version.

* Enter following commnad `opkg install tcpdump python3-codecs python3-light python3-email python3-openssl`
* Adapt the `URL` and `FAMILY` variables and Copy the `tcpdumpscan` procd init script to `/etc/init.d` using scp.
* Copy the tcpdumpscan.py using scp to `/root` directory
* type `/etc/init.d/tcpdumpscan start` to start scanning
* Finally type `/etc/init.d/tcpdumpscan enable` to enable both on startup.

Log output can be monitored using `logread` in the router's SSH session.

### airodump-ng + python scanner ###
This setup might give you more control on how the wifi driver behaves in monitor mode by using specific airodump-ng parameters. I stepped away from it as changing the wifi
channels didn't seem to play nicely with the rtl8192cu (it often freezed the whole device).

* First install aircrack suite `opkg install aircrack-ng python3-codecs python3-light python3-email python3-openssl`
* Adapt the `URL` and `FAMILY` variables and Copy the `airodump` and `airodumpscan` procd init scripts to `/etc/init.d` using scp.
* Finally type `/etc/init.d/airodump enable` and `/etc/init.d/airodumpscan enable` to enable both on startup.

## OpenWrt build instructions ##

If you want to include the tcpdumpscan scripts in your custom OpenWrt 18.06 build, you should do the following

* Open `feed.conf.default` the Openwrt repository folder and add `src-git find3 https://github.com/jekkos/find3-openwrt-scanner.git` to the bottom of the file. 
* Then type `./scripts/feeds update find3 && ./scripts/feeds install`
* When this command is completed, you should see a new entry under the `Utilities` section after starting `make menuconfig`. Then choose to include in the base image or to build as a package only.

### collectd ###
Not needed for find3 but nice as an addon to use with grafana and influxdb

```
opkg install collectd-mod-network collectd-mod-uptime collectd-mod-interface collectd-mod-memory collectd-mod-cpu collectd-mod-load collectd-mod-iwinfo
/etc/init.d/collectd enable
```
A cool dashboard can be found (here)[https://grafana.com/grafana/dashboards/3484]

## OpenWrt b-1300 & wr703n 8Mb build config ##
Upgrading vanilla OpenWrt snapshots on a router is quite time intensive. After you install a new snapshot, you need to add the python and other packages again manually.  Also this setup is using mesh functionality from `wpad-mesh` which is not in a default OpenWrt build. This meant that after every upgade the router lost internet connection.  In this case it's easier to include all package upfront in the root filesystem. The config file in `diffconfig` version which can be easily used to build newer versions of OpenWrt with the same additional packages. The config contains all required python and collectd packages, as well as the rtl8192cu wifi kernel driver.

Just copy the `b1300defconfig` or `wr703ndeconfig` file to your OpenWrt root folder. Mind that the latter requires a 8Mb flash.

* In case you want to build for wr703n apply the patch first using `git apply wr703n-8Mb.patch`
* Type `cat b1300defconfig >> .config` or `cat wr703ndefconfig >> .config` depending on your router model
* Next hit `make defconfig` to create a full build config with this diff applied
* Type `make V=j` to build the image 
* scp `openwrt-ipq40xx-glinet_gl-b1300-squashfs-sysupgrade.bin` to `/tmp` on the router
* Open a shell to the router and hit `sysupgrade /tmp/openwrt-ipq40xx-glinet_gl-b1300-squashfs-sysupgrade.bin`

