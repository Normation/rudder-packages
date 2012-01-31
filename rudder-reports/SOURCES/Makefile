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

TMP_DIR := $(shell mktemp -dq)
GIT_BRANCH_RUDDER = <put branch or tag name here>
RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>

localdepends: ./config

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./config:
	mkdir -p ./config
	cd $(TMP_DIR) && git clone --depth 1 git://github.com/Normation/rudder.git
	cd $(TMP_DIR)/rudder && git checkout $(GIT_BRANCH_RUDDER) || rm -rf $(TMP_DIR)/rudder
	cp $(TMP_DIR)/rudder/rudder-core/src/main/resources/reportsSchema.sql ./config/
	rm -rf $(TMP_DIR)

/usr/bin/git:
	sudo aptitude --assume-yes install git-core

localclean:
	rm -rf ./config
	rm -rf ./rudder-sources

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: localclean localdepends veryclean
