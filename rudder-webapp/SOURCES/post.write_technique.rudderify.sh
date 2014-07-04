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
# That hook is designed to be run just after a technique wwas created or modified
# It generates techniques files usable by Rudder, commit them in Tehcniques folder and reload the technique library
#

# Variables

DESTINATION_PATH="${1}"
TECHNIQUE="${2}"
CATEGORY_PATH='ncf_techniques/category.xml'

# Main

## Set necessary umask to prevent permission issues (mode 770)
umask 007

## Rudderify the new Technique
/usr/share/ncf/tools/ncf_rudder.py rudderify_technique /var/rudder/configuration-repository/techniques/ncf_techniques "${TECHNIQUE}"

## Operate on configuration-repository's git tree, in the Techniques
cd /var/rudder/configuration-repository/techniques/

# If a non-zero file exists on the filesystem...
if [ -s "${CATEGORY_PATH}" ]; then

  #... and is not already added in git, add it
  HANDLED_BY_GIT=$(git ls-tree -r master --name-only | grep -c "${CATEGORY_PATH}")

  if [ "${HANDLED_BY_GIT}" -eq 0 ];then
    git add ncf_techniques/category.xml
  fi

fi

## Commit the new Technique
git add "ncf_techniques/${TECHNIQUE}"
git commit -q -m "Commit meta Technique ${TECHNIQUE}"

# Reload technique library, bypass the ssl verification since we are on localhost
curl -s -f -k "https://localhost/rudder/api/techniqueLibrary/reload"

if [ "$?" -eq 22 ]; then
  echo "ERROR: Unable to reload the Techniques using Rudder API. Please reload them manually using Rudder web interface."
fi
