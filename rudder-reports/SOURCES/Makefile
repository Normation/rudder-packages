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

localdepends: ./rudder-sources ./rudder.conf

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./rudder.conf: ./rudder-sources
	cp rudder-sources/rudder-techniques/initial-promises/node-server/distributePolicy/rsyslog.conf/rudder.conf rudder.conf
	sed 's@\$${install_rsyslogd.rsyslog_port\[2\]}@514@' -i rudder.conf
	sed 's@\$${install_rsyslogd.rudder_postgres_server}@localhost@' -i rudder.conf
	sed 's@\$$(p.psql_password\[2\])@Normation@' -i rudder.conf

localclean:
	rm -rf ./rudder-sources
	rm -f ./rudder.conf

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: localclean localdepends veryclean
