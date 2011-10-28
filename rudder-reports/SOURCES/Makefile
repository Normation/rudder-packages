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
GIT_BRANCH_RUDDER ?= branches/rudder/2.3

localdepends: ./config

./config:
	mkdir -p ./config
	cd $(TMP_DIR) && git clone --depth 1 git@github.com:Normation/rudder.git
	cd $(TMP_DIR)/rudder && git checkout $(GIT_BRANCH_RUDDER) || rm -rf $(TMP_DIR)/rudder
	cp $(TMP_DIR)/rudder/rudder-core/src/main/resources/reportsSchema.sql ./config/
	cp $(TMP_DIR)/rudder/rudder-core/src/main/resources/reportsBootstrap.sql ./config/
	rm -rf $(TMP_DIR)

/usr/bin/git:
	sudo aptitude --assume-yes install git-core

localclean:

veryclean:
	rm -rf ./config

.PHONY: localclean localdepends veryclean
