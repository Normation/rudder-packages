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

.DEFAULT_GOAL := localdepends

OPENLDAP_RELEASE = 2.4.23
RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>
TMP_DIR := $(shell mktemp -dq)
WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget

localdepends: ./openldap-source ./DB_CONFIG ./rudder.schema ./inventory.schema ./slapd.conf ../debian/rudder-agent.init ../debian/rudder-agent.default
	rm -rf ./openldap.tgz

./openldap-source: /usr/bin/wget
	# Original URL: ftp://ftp.openldap.org/pub/OpenLDAP/openldap-release/openldap-$(OPENLDAP_RELEASE).tgz
	$(WGET) -O ./openldap.tgz http://www.normation.com/tarball/openldap-$(OPENLDAP_RELEASE).tgz
	tar xvzf ./openldap.tgz -C .
	mv ./openldap-$(OPENLDAP_RELEASE) ./openldap-source

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./slapd.conf: ./config/ldap-inventory
	cp ./rudder-sources/ldap-inventory/inventory-repository/src/main/resources/ldap/slapd.conf ./slapd.conf

./inventory.schema: ./config/ldap-inventory
	cp ./rudder-sources/ldap-inventory/inventory-repository/src/main/resources/ldap/inventory.schema ./inventory.schema

./DB_CONFIG: ./config/ldap-inventory
	cp ./rudder-sources/ldap-inventory/inventory-repository/src/main/resources/ldap/DB_CONFIG ./DB_CONFIG

./rudder.schema: ./config/rudder
	cp ./rudder-sources/rudder/rudder-core/src/main/resources/ldap/rudder.schema ./rudder.schema

../debian/rudder-agent.init:
	cp ./rudder-inventory-ldap.init ../debian/slapd.init

../debian/rudder-agent.default:
	cp ./rudder-inventory-ldap.default ../debian/slapd.default

/usr/bin/wget:
	sudo apt-get --assume-yes install wget

localclean:
	rm -rf ./openldap-source
	rm -rf ./slapd.conf
	rm -rf ../debian/slapd.init
	rm -rf ../debian/slapd.default
	rm -rf ./rudder.schema
	rm -rf ./inventory.schema
	rm -rf ./DB_CONFIG
	rm -rf ./rudder-sources

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: localclean localdepends veryclean
