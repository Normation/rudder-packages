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

%if 0%{?rhel}
%define logrotatefile    rudder.logrotate.rhel
%else
%define logrotatefile    rudder.logrotate.suse
%endif

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
Source3: rudder-node-to-relay
Source4: %{logrotatefile}
Source5: rudder-server-root.init
Source6: rudder-passwords.conf

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

Requires: rudder-agent, rudder-webapp, curl

%description
Rudder is an open source configuration management and audit solution.

This package is essentially a meta-package to install all components required to
run a Rudder root server on one machine. It also installs some required files
(rudder-init.sh, rudder-node-to-relay and uuid to root).


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
cp %{SOURCE3} %{buildroot}%{rudderdir}/bin/
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
# This package is only installed by the root server
# then we can set UUID to 'root' serenly
echo 'root' > %{rudderdir}/etc/uuid.hive

# Check if Rudder LDAP has already been initialize previously
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
%config(noreplace,missingok) %{_sysconfdir}/logrotate.d/rudder
%{rudderdir}/bin/rudder-node-to-relay
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
