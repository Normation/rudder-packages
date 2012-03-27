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

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>

localdepends: ./rudder-sources ../debian/rudder-server-root.logrotate ../debian/rudder-server-root.init

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

# Get the logrotate file. We need it both in the SOURCES/ dir, and in debian/ dir,
# because RPM packages take it straight from SOURCES/
./rudder.logrotate: ./rudder-sources
	cp -a ./rudder-sources/rudder-techniques/techniques/system/distributePolicy/1.0/logrotate.st ./rudder.logrotate

../debian/rudder-server-root.logrotate:
	cp rudder.logrotate.debian ../debian/rudder-server-root.logrotate

../debian/rudder-server-root.init:
	cp rudder-server-root.init ../debian/

localclean:
	rm -rf ./rudder-sources
	rm -f ../debian/rudder-server-root.logrotate
	rm -f ../debian/rudder-server-root.init
	rm -f ./rudder.logrotate

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: localclean localdepends veryclean
