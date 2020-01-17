include $(TOPDIR)/rules.mk

PKG_NAME:=find3
PKG_RELEASE:=1

PKG_MAINTAINER:=Jeroen Peelaerts <jpeelaer@jpeelaer.net>

include $(INCLUDE_DIR)/package.mk

define Package/find3-openwrt-scanner
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=Find3 CLI scanner
  URL:=http://www.internalpositioning.com/
  PKGARCH:=all
  DEPENDS:=+tcpdump +curl
endef

define Package/find3-openwrt-scanner/description
  FIND attempts to simplify internal positioning. 
  Internal positioning, simplified Using FIND, 
  and only your smartphone or laptop, you will be able to pinpoint your position in your home or office.
endef

define Build/Prepare
endef

define Build/Compile
endef

define Package/find3-openwrt-scanner/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(INSTALL_BIN) ./files/tcpdumpscan.sh $(1)/usr/lib
	$(INSTALL_DIR) $(1)/etc/init.d 
	$(INSTALL_BIN) ./files/tcpdumpscan.init $(1)/etc/init.d/tcpdumpscan
	$(INSTALL_DIR) $(1)/etc/config
	$(INSTALL_CONF) ./files/tcpdumpscan.config $(1)/etc/config/tcpdumpscan
endef 

define Package/find3-openwrt-scanner/conffiles
/etc/config/tcpdumpscan
endef

$(eval $(call BuildPackage,find3))
