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

rudder-agent.make:
	rsync --exclude=Makefile --exclude=filter-reqs.pl --exclude=perl-prepare.sh --exclude=rudder-perl --out-format='%n' -a ../../rudder-agent/ ../ | grep -v '^.*/$$' > rudder-agent.list
	cp -f ../../rudder-agent/SOURCES/Makefile ./rudder-agent.make

build-sources: rudder-agent.make
	$(MAKE) -f rudder-agent.make
	mv ../debian/rudder-agent.default ../debian/rudder-agent-thin.rudder-agent.default
	mv ../debian/rudder-agent.init ../debian/rudder-agent-thin.rudder-agent.init
	mv ../debian/rudder-agent.cron.d ../debian/rudder-agent-thin.rudder-agent.cron.d
	touch files fusioninventory-agent
	$(PATCH) -d ../debian --forward -p1 < patches/rudder-agent-thin/0001-rudder-agent-to-rudder-agent-thin-debian.patch
	$(PATCH) -d ../SPECS --forward -p1 < patches/rudder-agent-thin/0002-rudder-agent-to-rudder-agent-thin-spec.patch

clean: localclean veryclean

localclean: rudder-agent.make
	$(MAKE) -f rudder-agent.make localclean

veryclean: rudder-agent.make
	$(MAKE) -f rudder-agent.make veryclean
	rm -f rudder-agent.make
	xargs -a rudder-agent.list -d'\n' -I file rm -f ../file
	rm -f rudder-agent.list

.PHONY: localdepends clean localclean veryclean build-sources
