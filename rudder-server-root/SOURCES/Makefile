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

# Defauth PATHs
DESTDIR = $(CURDIR)/target
INSTALL_DIR = $(DESTDIR)/opt/rudder

localdepends: 

build:

install: build
	mkdir -p $(DESTDIR)/usr/lib/systemd/system
	mkdir -p $(INSTALL_DIR)/etc/server-roles.d/
	mkdir -p $(INSTALL_DIR)/share/package-scripts/
	$(INSTALL) -m 644 rudder-server.service $(DESTDIR)/usr/lib/systemd/system/
	$(INSTALL) -m 644 rudder-server-root $(INSTALL_DIR)/etc/server-roles.d/
	$(INSTALL) -m 755 rudder-server-root-postinst $(INSTALL_DIR)/share/package-scripts/

clean: localclean
localclean:

distclean: veryclean
veryclean: clean

.PHONY: clean localclean localdepends verycleana
