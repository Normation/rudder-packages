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

#=================================================
# Specification file for rudder-server-root
#
# Install rudder-init and force uuid to be root
#
# Copyright (C) 2011 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-server-root
%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - root server base package
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 1299256513
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-sources
Source2: rudder-init.sh
Source4: rudder.logrotate.suse
Source5: rudder-server-root.init
Source6: rudder-passwords.conf

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

Requires: rudder-agent, rudder-webapp, curl

%description
Rudder is an open source configuration management and audit solution.

This package is essentially a meta-package to install all components required to
run a Rudder root server on one machine. It also installs some required files
(rudder-init.sh and uuid to root).


#=================================================
# Source preparation
#=================================================
%prep

#=================================================
# Building
#=================================================
%build

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}
# Directories
mkdir -p %{buildroot}/var/cfengine/
mkdir -p %{buildroot}/var/cfengine/inputs
mkdir -p %{buildroot}%{rudderdir}/bin/
mkdir -p %{buildroot}%{rudderdir}/etc/
mkdir -p %{buildroot}%{ruddervardir}/cfengine-community/
mkdir -p %{buildroot}/etc/logrotate.d/
mkdir -p %{buildroot}/etc/init.d

# Others
cp %{SOURCE2} %{buildroot}%{rudderdir}/bin/
cp %{SOURCE4} %{buildroot}/etc/logrotate.d/rudder
cp %{SOURCE5} %{buildroot}/etc/init.d/rudder-server-root
cp %{SOURCE6} %{buildroot}%{rudderdir}/etc/


%pre -n rudder-server-root
#=================================================
# Pre Installation
#=================================================

%post -n rudder-server-root
#=================================================
# Post Installation
#=================================================
echo 'root' > %{rudderdir}/etc/uuid.hive
# Is this the first installation?
LDAPCHK=`/opt/rudder/sbin/slapcat  | grep "^dn: " | wc -l`
## If this is the first installation, need to initialize
if [ $LDAPCHK -eq 0 ]; then
  echo "************************************************************"
  echo "Rudder is now installed but not configured."
  echo "Please run /opt/rudder/bin/rudder-init.sh"
  echo "************************************************************"
else
  # If it is an upgrade try to send inventory
  ## Check that the inventory has not been sent for 24 hours
  SERVER_INVENTORY_DATE=`/opt/rudder/sbin/slapcat | perl -p0e 's/\n //g' | perl -p0e 's/\n([^\n])/%%%%\1/g' |\
  grep -i "^%%%%dn: nodeId=root,ou=Nodes,ou=Accepted Inventories,ou=Inventories,cn=rudder-configuration" |\
  grep -iE --color "%%%%(inventoryDate)::? " | sed 's/.*inventoryDate: \([0-9]*\).*/\1/g'`
  DATE_CHECK=`perl -e 'use Time::Piece; my $date = shift; my $time = Time::Piece->strptime($date, "%Y%m%d%H%M%%S"); $time += $time->localtime->tzoffset; print $time->strftime("%s");' ${SERVER_INVENTORY_DATE}`
  DATE_REF=`date -d '24 hours ago' +%s`
  if [ ${DATE_CHECK} -lt ${DATE_REF} ]; then
    ## If the inventory of the root server is older than 24 hours
    ## create invtenroy of the machine
    echo "A new inventory will be created..."
    UUID=`/bin/cat /opt/rudder/etc/uuid.hive`
    RUDDERUUID=`/usr/sbin/dmidecode -s system-uuid`
    USER=`/usr/bin/whoami`
    CFKEY=`/bin/cat /var/rudder/cfengine-community/ppkeys/localhost.pub`
    HOST_INV=`grep "^base.url\s*=" /opt/rudder/etc/rudder-web.properties | sed 's%^base.url\s*=\s*https\?://\([^:]*\)[:[0-9]*]*/.*$%\1%'`
    ## We assume that root server is sending inventory to itself
    POLSRVUUID=${UUID}
    ## Make sure that the folder to make inventory exists
    mkdir -p /var/rudder/tmp/inventory/
    /opt/rudder/bin/run-inventory --local=/var/rudder/tmp/inventory --scan-homedirs
    echo "...adding extra informations..."
    FILE_TMP=`mktemp`
    FILE_SRC=`find /var/rudder/tmp/inventory/ -name "*.ocs"`
	echo "Transitional files: ${FILE_TMP} and ${FILE_SRC}"
     ## Cut file in two in order to add extra mandatory information 2 lines before the end
    head -n-2 ${FILE_SRC} > ${FILE_TMP}
    echo -e "\n<UUID>${UUID}</UUID>\n<USER>${USER}</USER>\n<AGENTSNAME><AGENTNAME>Community</AGENTNAME>\n</AGENTSNAME>\n<MACHINEID>${RUDDERUUID}</MACHINEID>\n<CFKEY>${CFKEY}</CFKEY>\n<HOSTNAME>${HOST_INV}</HOSTNAME>\n<POLICY_SERVER>${POLSRVUUID}</POLICY_SERVER>\n<QUERY>INVENTORY</QUERY>\n</REQUEST>" >> ${FILE_TMP}
    cp -f ${FILE_TMP} ${FILE_SRC}
    ## And move the inventory in the foler which will process it
    ## when the application will be available
    mv /var/rudder/tmp/inventory/*.ocs /var/rudder/inventories/incoming/
    ## Remove temporary folder and files generated
    rm -rf /var/rudder/tmp/inventory/
    echo "Done."
  fi
fi

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-server-root
%defattr(-, root, root, 0755)
%config(noreplace,missingok) %{_sysconfdir}/logrotate.d/rudder
%{rudderdir}/bin/rudder-init.sh
/var/cfengine/inputs
%attr(0755, root, root) /etc/init.d/rudder-server-root
%config(noreplace) %{rudderdir}/etc/rudder-passwords.conf
%attr(0600, root, root) %{rudderdir}/etc/rudder-passwords.conf

#=================================================
# Changelog
#=================================================
%changelog
* Wed Aug 31 2011 - Nicolas Perron <nicolas.perron@normation.com> 2.3-beta1-1
- Add inputs folder for cfengine nova
* Tue Aug 02 2011 - Nicolas Perron <nicolas.perron@normation.com> 2.3-alpha4-1
- Initial package
