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

RUDDER_VERSION_TO_PACKAGE =

# Autodetect presence of gnu tools
TAR := $(shell type gtar >/dev/null 2>&1 && echo gtar || echo tar)
PATCH := $(shell type gpatch >/dev/null 2>&1 && echo gpatch || echo patch)
SED := $(shell type gsed >/dev/null 2>&1 && echo gsed || echo sed)
INSTALL := $(shell type ginstall >/dev/null 2>&1 && echo ginstall || echo install)
CP_A := cp -rp
FIND := find

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

# Defauth PATHs
RUDDER_DIR = /opt/rudder
DESTDIR = $(CURDIR)/target
INSTALL_DIR = $(DESTDIR)$(RUDDER_DIR)

localdepends: ./rudder-sources

rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2 https://www.rudder-project.org/archives/rudder-sources-$(RUDDER_VERSION_TO_PACKAGE).tar.bz2 ""

rudder-sources: rudder-sources.tar.bz2
	bunzip2 < rudder-sources.tar.bz2 | $(TAR) xf -
	mv rudder-sources-$(RUDDER_VERSION_TO_PACKAGE)*/ rudder-sources/ # the '*' is needed for nightly release
	touch rudder-sources # to make it younger than the bzip source file

build:
	true

install:
	# Init files
ifneq (true,$(NO_INIT)) # By default install init script
	mkdir -p $(DESTDIR)/etc/init.d/
	$(INSTALL) -m 755 rudder-server.init $(DESTDIR)/etc/init.d/rudder-server
endif

	# Directories
	mkdir -p $(INSTALL_DIR)/etc/server-roles.d/

	$(INSTALL) -m 644 rudder-server-root $(INSTALL_DIR)/etc/server-roles.d/

	# Add postinst script
	mkdir -p $(INSTALL_DIR)/share/package-scripts/
	$(INSTALL) -m 755 rudder-server-root-postinst $(INSTALL_DIR)/share/package-scripts/


clean: localclean
localclean:
	rm -rf ./rudder-sources

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: clean localclean localdepends veryclean
