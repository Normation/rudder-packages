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

RUDDER_VERSION_TO_PACKAGE =
RUDDER_MAJOR_VERSION := $(shell echo ${RUDDER_VERSION_TO_PACKAGE} | cut -d'.' -f 1-2)

PROXY_ENV = $(if $(PROXY), http_proxy=$(PROXY))
# Usage: $(GET) <destination_file> <url> <hash>
# Pass an empty string to skip hash check
# grep 'GET=' */SOURCES/Makefile to patch everywhere
GET=get() { $(PROXY_ENV) curl --silent --location --fail --output "$$1.part" "$$2" && { openssl dgst -sha256 "$$1.part" | grep -q "$$3" || { echo "Wrong checksum, aborting"; exit 1; }; } && mv "$$1.part" "$$1"; }; get

# Defauth PATHs
DESTDIR = $(CURDIR)/target

localdepends: rudder-sources

rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2 https://repository.rudder.io/sources/$(RUDDER_VERSION_TO_PACKAGE)/rudder-sources-$(RUDDER_VERSION_TO_PACKAGE).tar.bz2 ""

rudder-sources: rudder-sources.tar.bz2
	tar x --no-same-owner --no-same-permissions -f rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

build:

install: rudder-sources build
	mkdir -p $(DESTDIR)/opt/rudder/etc/postgresql/
	# must be a different name from the one in rudder-server
	install -m 644 -T rudder-sources/rudder/webapp/sources/rudder/rudder-core/src/main/resources/reportsSchema.sql $(DESTDIR)/opt/rudder/etc/postgresql/reportsSchema-ext.sql
	mkdir -p $(DESTDIR)/opt/rudder/share/package-scripts/
	install -m 755 rudder-external-db-postinst $(DESTDIR)/opt/rudder/share/package-scripts/

clean:

distclean: clean

# distclean should remove everything except rudder-sources.tar.bz2 since it can be brought by by external means
mrproper: distclean
	rm -f ./rudder-sources.tar.bz2

.PHONY: build install clean localdepends distclean mrproper
