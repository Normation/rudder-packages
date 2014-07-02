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

DESTINATION_PATH=$1
TECHNIQUE=$2
CATEGORY_PATH=ncf_techniques/category.xml

# Main

/usr/share/ncf/tools/ncf_rudder.py rudderify_technique /var/rudder/configuration-repository/techniques/ncf_techniques $TECHNIQUE

cd /var/rudder/configuration-repository/techniques/

# If a non-zero file exists on the filesystem...
if [ -s "${CATEGORY_PATH}" ]; then
  #... and is not already added in git, add it
  HANDLED_BY_GIT=`git ls-tree -r master --name-only | grep "${CATEGORY_PATH}" | wc -l`
  if [ ${HANDLED_BY_GIT} -eq 0 ];then
    git add ncf_techniques/category.xml
  fi
fi


git add ncf_techniques/$TECHNIQUE

git commit -m "Commit meta techniques $TECHNIQUE"

curl -X GET "http://localhost/rudder/api/techniqueLibrary/reload" 
