include $(TOPDIR)/rules.mk

PKG_NAME:=find3
PKG_VERSION:=1.0
PKG_RELEASE:=1
PKG_SOURCE_PROTO:=git 
PKG_SOURCE_URL:=https://github.com/jekkos/find3-openwrt-scanner
PKG_SOURCE_VERSION:=3438d347246c8e5d46bfa2aee912804ffdac5b0c
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_SOURCE_VERSION)
PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_SOURCE_SUBDIR)
PKG_MAINTAINER:=Jeroen Peelaerts <jpeelaer@jpeelaer.net>

include $(INCLUDE_DIR)/package.mk

define Package/find3
  SECTION:=utils
  CATEGORY:=Utilities
  TITLE:=Find3 CLI scanner
  URL:=http://www.internalpositioning.com/
  DEPENDS:=+tcpdump +curl
endef

define Package/find3/description
  FIND attempts to simplify internal positioning. Internal positioning, simplified Using FIND, and only your smartphone or laptop, you will be able to pinpoint your position in your home or office
endef

# Nothing just to be sure
#define Build/Configure
#endef

define Package/find3/install
	$(INSTALL_DIR) $(1)/usr/sbin $(1)/etc/init.d $(1)/etc/config
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/tcpdumpscan.sh $(1)/usr/lib/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/tcpdumpscan.init $(1)/etc/init.d/tcpdumpscan
	$(INSTALL_CONF) $(PKG_BUILD_DIR)/tcpdumpscan.config $(1)/etc/config/tcpdumpscan
endef 
$(eval $(call BuildPackage,find3))
