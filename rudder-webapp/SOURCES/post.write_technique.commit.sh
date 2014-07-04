#!/bin/sh
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

#
# That hook is designed to be run just after a technique was created or modified.
# Its goal is to commit the newly created technique with ncf-api to configuration-repository
#

# Variables

DESTINATION_PATH=${1}
TECHNIQUE=${2}

# Main

## Set necessary umask to prevent permission issues (mode 770)
umask 007

## Operate on configuration-repository's git tree
cd /var/rudder/configuration-repository

## Commit the new Technique
git add "ncf/50_techniques/${TECHNIQUE}"
git commit -q -m "Commit ncf Technique \"${TECHNIQUE}\" in Rudder"
