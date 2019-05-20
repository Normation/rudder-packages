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
SHELL = /bin/bash

OPENLDAP_RELEASE = 2.4.47
OPENLDAP_SHA256 = f54c5877865233d9ada77c60c0f69b3e0bfd8b1b55889504c650047cc305520b

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>

PROXY_ENV = $(if $(PROXY), http_proxy=$(PROXY))
# Usage: $(GET) <destination_file> <url> <hash>
# Pass an empty string to skip hash check
# grep 'GET=' */SOURCES/Makefile to patch everywhere
GET=get() { $(PROXY_ENV) curl -s -L -o "$$1.part" "$$2" && { openssl dgst -sha256 "$$1.part" | grep -q "$$3" || { echo "Wrong checksum, aborting"; exit 1; }; } && mv "$$1.part" "$$1"; }; get

DESTDIR = $(CURDIR)/target

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
	mkdir -p $(DESTDIR)/etc/rsyslog.d
	mkdir -p $(DESTDIR)/opt/rudder/etc/server-roles.d/
	mkdir -p $(DESTDIR)/var/log/rudder/ldap
	mkdir -p $(DESTDIR)/var/rudder/ldap/openldap-data
	mkdir -p $(DESTDIR)/var/rudder/run
	mkdir -p $(DESTDIR)/usr/lib/systemd/system
	mkdir -p $(DESTDIR)/opt/rudder/share/package-scripts/
	install -m 640 slapd.conf $(DESTDIR)/opt/rudder/etc/openldap/slapd.conf
	install -m 644 rudder-sources/ldap-inventory/inventory-repository/src/main/resources/ldap/inventory.schema $(DESTDIR)/opt/rudder/etc/openldap/schema/
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/ldap/rudder.schema $(DESTDIR)/opt/rudder/etc/openldap/schema/
	install -m 644 rudder-inventory-ldap $(DESTDIR)/opt/rudder/etc/server-roles.d/
	install -m 644 rudder-ldap $(DESTDIR)/opt/rudder/etc/server-roles.d/
	install -m 644 rsyslog/rudder-slapd.conf $(DESTDIR)/etc/rsyslog.d/rudder-slapd.conf
	install -m 644 rudder-slapd.service $(DESTDIR)/usr/lib/systemd/system/rudder-slapd.service
	install -m 755 rudder-ldap-postinst $(DESTDIR)/opt/rudder/share/package-scripts/

clean:
	rm -f build
	rm -rf rudder-sources
	rm -rf openldap-source

# distclean should remove everything except rudder-sources.tar.bz2 since it can be brought by by external means
distclean: clean

mrproper: distclean
	rm -f ./rudder-sources.tar.bz2

.PHONY: install clean localdepends distclean mrproper
