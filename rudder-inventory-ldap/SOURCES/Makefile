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

OPENLDAP_RELEASE = 2.4.46
OPENLDAP_SHA256 = 9a90dcb86b99ae790ccab93b7585a31fbcbeec8c94bf0f7ab0ca0a87ea0c4b2d

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>

PATCH := /usr/bin/patch
FIND := /usr/bin/find

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
CURL = curl -s --http1.1 -L -o
ifneq (,$(wildcard /usr/bin/curl))
_GET = $(PROXY_ENV) $(CURL)
else
_GET = $(PROXY_ENV) $(WGET)
endif
# Pass an empty string to skip hash check
GET=get() { $(_GET) "$$1.part" "$$2" && { openssl dgst -sha256 "$$1.part" | grep -q "$$3" || { echo "Wrong checksum, aborting"; exit 1; }; } && mv "$$1.part" "$$1"; }; get

localdepends: ./openldap-source ./rudder.schema ./inventory.schema ../debian/rudder-slapd.init ../debian/rudder-slapd.default
	rm -rf ./openldap.tgz

./openldap-source: /usr/bin/wget
	# Original URL: ftp://ftp.openldap.org/pub/OpenLDAP/openldap-release/openldap-$(OPENLDAP_RELEASE).tgz
	$(GET) ./openldap.tgz https://repository.rudder.io/build-dependencies/openldap/openldap-$(OPENLDAP_RELEASE).tgz $(OPENLDAP_SHA256)
	tar xzf ./openldap.tgz -C .
	mv ./openldap-$(OPENLDAP_RELEASE) ./openldap-source
	
	# Apply patches
	for PATCHNAME in patches/openldap/*.patch; do echo "Applying $$PATCHNAME..."; $(PATCH) -d ./openldap-source -p1 < $$PATCHNAME; done
	# Make sure there were no rejects
	test `$(FIND) ./openldap-source -name \*.rej | wc -l` = 0

./rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2 https://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2 ""

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
	rm -rf ./openldap-source
	rm -rf ./rudder.schema
	rm -rf ./inventory.schema

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: localclean localdepends veryclean
