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

GIT_BRANCH_RUDDER = remotes/origin/master

localdepends: ./policy-templates

./policy-templates:
	cd . && git clone --depth 1 ssh://git@git.normation.com:5190/policy-templates.git
	cd ./policy-templates && git checkout $(GIT_BRANCH_RUDDER) || rm -rf ./policy-templates

/usr/bin/git:
	sudo apt-get --assume-yes install git-core

localclean:

veryclean:
	rm -rf ./policy-templates

.PHONY: localclean localdepends  veryclean
