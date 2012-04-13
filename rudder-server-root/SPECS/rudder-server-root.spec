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
# Install initial promises, rudder-init and uuid
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
%define init_promises	 /initial-promises

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

Source1: rudder-policy-templates
Source2: rudder-init.sh
Source3: uuid.hive
Source4: rudder.logrotate.suse
Source5: rudder-server-root.init

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

Requires: rudder-cfengine-community, rudder-webapp, curl

%description
Rudder is an open source configuration management and audit solution.

This package is essentially a meta-package to install all components required to
run a Rudder root server on one machine. It also installs some required files
(initial promises).


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
mkdir -p %{buildroot}%{rudderdir}/share/initial-promises/
mkdir -p %{buildroot}%{ruddervardir}/cfengine-community/
mkdir -p %{buildroot}/etc/logrotate.d/
mkdir -p %{buildroot}/etc/init.d

# Initial Promises (root)
cp -r %{SOURCE1}/%{init_promises}/rootServerInitialPromises/cfengine-nova %{buildroot}%{rudderdir}/share/initial-promises/
cp -r %{SOURCE1}/%{init_promises}/rootServerInitialPromises/cfengine-community %{buildroot}%{rudderdir}/share/initial-promises/
# Initial Promises (node)
cp -r %{SOURCE1}%{init_promises}/nodeInitialPromises %{buildroot}/var/cfengine/masterfiles
cp -r %{SOURCE1}%{init_promises}/nodeInitialPromises %{buildroot}%{ruddervardir}/cfengine-community/masterfiles
# Others
cp %{SOURCE2} %{buildroot}%{rudderdir}/bin/
cp %{SOURCE3} %{buildroot}%{rudderdir}/etc/
cp %{SOURCE4} %{buildroot}/etc/logrotate.d/rudder
cp %{SOURCE5} %{buildroot}/etc/init.d/rudder-server-root


%pre -n rudder-server-root
#=================================================
# Pre Installation
#=================================================

%post -n rudder-server-root
#=================================================
# Post Installation
#=================================================
# Is this the first installation?
LDAPCHK=`/opt/rudder/sbin/slapcat  | grep "^dn: " | wc -l`
if [ $LDAPCHK -eq 0 ]; then
  echo "************************************************************"
  echo "Rudder is now installed but not configured."
  echo "Please run /opt/rudder/bin/rudder-init.sh"
  echo "************************************************************"
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
%{rudderdir}/share/initial-promises/
%config %{rudderdir}/etc/uuid.hive
%config(noreplace,missingok) %{_sysconfdir}/logrotate.d/rudder
%{rudderdir}/bin/rudder-init.sh
%{ruddervardir}/cfengine-community/masterfiles
/var/cfengine/masterfiles
/var/cfengine/inputs
%attr(0755, root, root) /etc/init.d/rudder-server-root

#=================================================
# Changelog
#=================================================
%changelog
* Wed Aug 31 2011 - Nicolas Perron <nicolas.perron@normation.com> 2.3-beta1-1
- Add inputs folder for cfengine nova
* Tue Aug 02 2011 - Nicolas Perron <nicolas.perron@normation.com> 2.3-alpha4-1
- Initial package
