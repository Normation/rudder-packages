#####################################################################################
# Copyright 2014 Normation SAS
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

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>

MAKE  := /usr/bin/make
PATCH := /usr/bin/patch

localdepends: ./rudder-agent.make build-sources

# We need to copy rudder-agent's Makefile to make the build the most self-contained possible
rudder-agent.make: ../../rudder-agent/SOURCES/Makefile
	cp -f ../../rudder-agent/SOURCES/Makefile ./rudder-agent.make

fetch-sources: fetch-sources-stamp
fetch-sources-stamp:
	# Clean up rudder-agent sources first
	cd ../../rudder-agent/SOURCES && make localclean
	# Make sure the debian/changelog is pristine
	cd ../../rudder-agent/debian && git checkout changelog
	# Get everything from rudder-agent, excluding perl thingies and Makefile
	# We also exclude OpenSSL-specific patches from OS-dependent patches
	# to prevent them from reaching rudder-agent-thin.
	# See. http://www.rudder-project.org/redmine/issues/5147
	rsync --exclude=patches/DEBIAN_3/0001-use-bundled-openssl.patch --exclude=patches/DEBIAN_4/0001-use-bundled-openssl.patch --exclude=patches/UBUNTU_10_04/0001-use-bundled-openssl.patch --exclude=Makefile --exclude=filter-reqs.pl --exclude=perl-prepare.sh --exclude=rudder-perl --out-format='%n' -a ../../rudder-agent/ ../ | grep -v '^.*/$$' > rudder-agent.list
	touch fetch-sources-stamp

build-sources: build-sources-stamp
build-sources-stamp: fetch-sources-stamp rudder-agent.make
	# Bypass fusioninventory download
	touch files fusioninventory-agent

	$(MAKE) -f rudder-agent.make

	# Prepare rudder-agent-thin Debian-specific elements
	mv ../debian/rudder-agent.default ../debian/rudder-agent-thin.rudder-agent.default
	mv ../debian/rudder-agent.init ../debian/rudder-agent-thin.rudder-agent.init
	mv ../debian/rudder-agent.cron.d ../debian/rudder-agent-thin.rudder-agent.cron.d

	# Convert rudder-agent to rudder-agent-thin where needed
	$(PATCH) -d ../debian --forward -p1 < patches/rudder-agent-thin/0001-rudder-agent-to-rudder-agent-thin-debian.patch
	$(PATCH) -d ../SPECS --forward -p1 < patches/rudder-agent-thin/0002-rudder-agent-to-rudder-agent-thin-spec.patch

	# Make sure there were no rejects
	test `$(FIND) . -name \*.rej | wc -l` = 0

	touch build-sources-stamp

localclean: rudder-agent.make
	$(MAKE) -f rudder-agent.make localclean
	xargs -a rudder-agent.list -d'\n' -I file rm -f ../file || echo "No rudder-agent.list, skipping rsync'ed files cleanup."
	rm -rf ../SPECS ../debian
	rm -f rudder-agent.list
	rm -f fetch-sources-stamp
	rm -f build-sources-stamp
	rm -f rudder-agent.make

veryclean:
	# N/A

.PHONY: localdepends localclean veryclean fetch-sources build-sources
