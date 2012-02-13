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

GIT_BRANCH_RUDDER = <put branch or tag name here>

localdepends: ./rudder-policy-templates ../debian/rudder-server-root.logrotate ../debian/rudder-server-root.init

./rudder-policy-templates:
	cd . && git clone --depth 1 git://github.com/Normation/rudder-policy-templates.git
	cd ./rudder-policy-templates && git checkout $(GIT_BRANCH_RUDDER) || rm -rf ./rudder-policy-templates

../debian/rudder-server-root.logrotate:
	cp rudder.logrotate ../debian/rudder-server-root.logrotate

../debian/rudder-server-root.init:
	cp rudder-server-root.init ../debian/

/usr/bin/git:
	sudo apt-get --assume-yes install git-core

localclean:
	rm -f ../debian/rudder-server-root.logrotate
	rm -f ../debian/rudder-server-root.init

veryclean:
	rm -rf ./rudder-policy-templates

.PHONY: localclean localdepends veryclean
