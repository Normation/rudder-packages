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

PROXY_ENV = $(if $(PROXY), http_proxy=$(PROXY))
# Usage: $(GET) <destination_file> <url> <hash>
# Pass an empty string to skip hash check
# grep 'GET=' */SOURCES/Makefile to patch everywhere
GET=get() { $(PROXY_ENV) curl --silent --location --fail --output "$$1.part" "$$2" && { openssl dgst -sha256 "$$1.part" | grep -q "$$3" || { echo "Wrong checksum, aborting"; exit 1; }; } && mv "$$1.part" "$$1"; }; get

# Defauth PATHs
DESTDIR = $(CURDIR)/target

localdepends: 

build:

rudder-server-root-version:
	[ -f rudder-sources/versions ] && cp ./rudder-sources/versions $@
	[ -f $@ ] || echo "main_version=unknown" > $@
	[ -f rudder-sources/commits ] && awk '{print $1"_commit="$2}' commits >> $@

install: build rudder-server-root-version
	mkdir -p $(DESTDIR)/usr/lib/systemd/system
	mkdir -p $(DESTDIR)/opt/rudder/etc/server-roles.d/
	mkdir -p $(DESTDIR)/opt/rudder/share/package-scripts/
	mkdir -p $(DESTDIR)/opt/rudder/share/versions/
	install -m 644 rudder-server.service $(DESTDIR)/usr/lib/systemd/system/
	install -m 644 rudder-server-root $(DESTDIR)/opt/rudder/etc/server-roles.d/
	install -m 755 rudder-server-root-postinst $(DESTDIR)/opt/rudder/share/package-scripts/
	install -m 644 rudder-server-root-version $(DESTDIR)/opt/rudder/share/versions/

clean:

# distclean should remove everything except rudder-sources.tar.bz2 since it can be brought by by external means
distclean: clean

.PHONY: clean localdepends distclean
