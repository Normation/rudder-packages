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

INSTALL := $(shell type ginstall >/dev/null 2>&1 && echo ginstall || echo install)

# Defauth PATHs
RUDDER_DIR = /opt/rudder
DESTDIR = $(CURDIR)/target
INSTALL_DIR = $(DESTDIR)$(RUDDER_DIR)

localdepends: ./rudder-sources

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

build:
	true

install:
	mkdir -p $(DESTDIR)/etc/init.d/

	# Init files
ifneq (true,$(NO_INIT))
	$(INSTALL) -m 755 rudder-server.init $(DESTDIR)/etc/init.d/rudder-server
endif

	# Directories
	mkdir -p $(INSTALL_DIR)/etc/
	mkdir -p $(INSTALL_DIR)/etc/server-roles.d/

	$(INSTALL) -m 644 rudder-server-root $(INSTALL_DIR)/etc/server-roles.d/

localclean:
	rm -rf ./rudder-sources

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: localclean localdepends veryclean
