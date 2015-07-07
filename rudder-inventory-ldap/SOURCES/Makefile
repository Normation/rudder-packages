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

OPENLDAP_RELEASE = 2.4.41
BERKELEYDB_RELEASE = 5.1.29

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>

WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget

localdepends: ./berkeleydb-source ./openldap-source ./rudder.schema ./inventory.schema ../debian/rudder-slapd.init ../debian/rudder-slapd.default
	rm -rf ./openldap.tgz
	rm -rf ./berkeleydb.tgz

./berkeleydb-source: /usr/bin/wget
	# Original URL: http://download.oracle.com/berkeley-db/db-$(BERKELEYDB_RELEASE).tar.gz
	$(WGET) -O ./berkeleydb.tgz http://www.normation.com/tarball/db-$(BERKELEYDB_RELEASE).tar.gz
	tar xzf ./berkeleydb.tgz -C .
	mv ./db-$(BERKELEYDB_RELEASE) ./berkeleydb-source

./openldap-source: /usr/bin/wget
	# Original URL: ftp://ftp.openldap.org/pub/OpenLDAP/openldap-release/openldap-$(OPENLDAP_RELEASE).tgz
	$(WGET) -O ./openldap.tgz http://www.normation.com/tarball/openldap/openldap-$(OPENLDAP_RELEASE).tgz
	tar xzf ./openldap.tgz -C .
	mv ./openldap-$(OPENLDAP_RELEASE) ./openldap-source

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./rudder.schema: ./rudder-sources
	cp ./rudder-sources/rudder/rudder-core/src/main/resources/ldap/rudder.schema ./rudder.schema

./inventory.schema: ./rudder-sources
	cp ./rudder-sources/ldap-inventory/inventory-repository/src/main/resources/ldap/inventory.schema ./inventory.schema

../debian/rudder-slapd.init:
	cp ./rudder-inventory-ldap.init ../debian/rudder-slapd.init

../debian/rudder-slapd.default:
	cp ./rudder-inventory-ldap.default ../debian/rudder-slapd.default

/usr/bin/wget:
	sudo apt-get --assume-yes install wget

localclean:
	rm -rf ../debian/rudder-slapd.init
	rm -rf ../debian/rudder-slapd.default
	rm -rf ./rudder-sources
	rm -rf ./berkeleydb-source
	rm -rf ./openldap-source
	rm -rf ./berkeleydb-source
	rm -rf ./rudder.schema
	rm -rf ./inventory.schema

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: localclean localdepends veryclean
