#!/bin/bash
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

set -e

STEP="Script start"
anomaly_handler() {
  echo ""
  echo "ERROR: An error happened in $0 during the step: ${STEP}"
}

trap anomaly_handler ERR INT TERM


#
# That hook is designed to be run just after a technique wwas created or modified
# It generates techniques files usable by Rudder, commit them in Tehcniques folder and reload the technique library
#

# Variables

DESTINATION_PATH="${1}"
TECHNIQUE="${2}"

# Main

## Set necessary umask to prevent permission issues (mode 770)
umask 007

# Reload technique library, bypass the ssl verification since we are on localhost
STEP="Reloading the Techniques using Rudder API. Please reload them manually using Rudder web interface."
curl --proxy '' -s -f "http://localhost:8080/rudder/api/techniqueLibrary/reload"

