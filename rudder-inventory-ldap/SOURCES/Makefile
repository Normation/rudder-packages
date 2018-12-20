#####################################################################################
# Copyright 2011 Normation SAS
#####################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, Version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#####################################################################################

.DEFAULT_GOAL := build

OPENLDAP_RELEASE = 2.4.46
OPENLDAP_SHA256 = 9a90dcb86b99ae790ccab93b7585a31fbcbeec8c94bf0f7ab0ca0a87ea0c4b2d

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>

# GENERIC_GET: do not remove this line
# This is a generic get code that is common to many of our Makefiles.
# The tag is here to find them. Rudder agent has an even more generic one.
# If you change this code, change all the places where you can find this tag too.
# It is duplicated because it is the code that is used to manage dependency
# to other repositories, hence allowing deduplication of other code.
# Autodetect wget, curl or fetch usage and proxy configuration
# Usage: $(GET) <destination_file> <url> <hash>
PROXY_ENV = $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY))
# No accept encoding to prevent the webserver form altering the distributed file
WGET = wget -q --header="accept-encoding:" -O
CURL = curl -s -L -o
ifneq (,$(wildcard /usr/bin/curl))
_GET = $(PROXY_ENV) $(CURL)
else
_GET = $(PROXY_ENV) $(WGET)
endif
# Pass an empty string to skip hash check
GET=get() { $(_GET) "$$1.part" "$$2" && { openssl dgst -sha256 "$$1.part" | grep -q "$$3" || { echo "Wrong checksum, aborting"; exit 1; }; } && mv "$$1.part" "$$1"; }; get

localdepends: openldap-source

openldap-source:
	# Original URL: ftp://ftp.openldap.org/pub/OpenLDAP/openldap-release/openldap-$(OPENLDAP_RELEASE).tgz
	$(GET) ./openldap.tgz https://repository.rudder.io/build-dependencies/openldap/openldap-$(OPENLDAP_RELEASE).tgz $(OPENLDAP_SHA256)
	tar xzf ./openldap.tgz -C .
	mv ./openldap-$(OPENLDAP_RELEASE) ./openldap-source
	
	# Apply patches
	for PATCHNAME in patches/openldap/*.patch; do echo "Applying $$PATCHNAME..."; patch -d ./openldap-source -p1 < $$PATCHNAME; done
	# Make sure there were no rejects
	test `find ./openldap-source -name \*.rej | wc -l` = 0
	rm -rf ./openldap.tgz

rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2 http://repository.rudder.io/sources/$(RUDDER_VERSION_TO_PACKAGE)/rudder-sources-$(RUDDER_VERSION_TO_PACKAGE).tar.bz2 ""

rudder-sources: rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

build: openldap-source rudder-sources
	cd openldap-source && ./configure --prefix=/opt/rudder --libdir=/opt/rudder/lib/ldap --enable-dynamic --enable-debug --enable-modules --enable-monitor=mod --enable-dynlist=mod --enable-mdb=yes --enable-hdb=no --enable-bdb=no
	cd openldap-source && make depend
	cd openldap-source && make
	touch $@

# Install into DESTDIR
install: build
	cd openldap-source && make install DESTDIR=$(DESTDIR)
	mkdir -p $(DESTDIR)/etc/init.d
	mkdir -p $(DESTDIR)/etc/default
	mkdir -p $(DESTDIR)/etc/rsyslog.d
	mkdir -p $(DESTDIR)/opt/rudder/etc/server-roles.d/
	mkdir -p $(DESTDIR)/var/log/rudder/ldap
	mkdir -p $(DESTDIR)/var/rudder/ldap/openldap-data
	mkdir -p $(DESTDIR)/var/rudder/run
	install -m 755 rudder-inventory-ldap.init $(DESTDIR)/etc/init.d/rudder-slapd
	install -m 644 rudder-inventory-ldap.default $(DESTDIR)/etc/default/rudder-slapd
	install -m 644 rudder-slapd.conf $(DESTDIR)/opt/rudder/etc/rudder-slapd.conf
	install -m 644 slapd.conf $(DESTDIR)/opt/rudder/etc/openldap/slapd.conf
	install -m 644 rudder-sources/ldap-inventory/inventory-repository/src/main/resources/ldap/inventory.schema $(DESTDIR)/opt/rudder/etc/openldap/schema/
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/ldap/rudder.schema $(DESTDIR)/opt/rudder/etc/openldap/schema/
	install -m 644 rudder-inventory-ldap $(DESTDIR)/opt/rudder/etc/server-roles.d/
	install -m 644 rudder-ldap $(DESTDIR)/opt/rudder/etc/server-roles.d/
	install -m 755 rudder-slapd-configure $(DESTDIR)/opt/rudder/bin/rudder-slapd-configure
	install -m 644 rsyslog/rudder-slapd.conf $(DESTDIR)/etc/rsyslog.d/rudder-slapd.conf

clean: localclean
localclean:
	rm -f build
	rm -rf rudder-sources
	rm -rf openldap-source

distclean: veryclean
veryclean: clean
	rm -f ./rudder-sources.tar.bz2

.PHONY: install clean localclean localdepends veryclean
