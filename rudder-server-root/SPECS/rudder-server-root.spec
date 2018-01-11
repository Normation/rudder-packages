#####################################################################################
# Copyright 2011- Normation SAS
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
# Installs a Rudder root server
#
# Copyright (C) 2011- Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-server-root
%define real_epoch       0
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
Epoch: %{real_epoch}
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-sources

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

Requires: rudder-jetty = %{real_epoch}:%{real_version}, rudder-webapp = %{real_epoch}:%{real_version}, rudder-inventory-endpoint = %{real_epoch}:%{real_version}, rudder-inventory-ldap = %{real_epoch}:%{real_version}, rudder-reports = %{real_epoch}:%{real_version}, rudder-agent = %{real_epoch}:%{real_version}, curl

%description
Rudder is an open source configuration management and audit solution.

This package is essentially a meta-package to install all components required to
run a Rudder root server on a machine.

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

cd %{_sourcedir}

make install DESTDIR=%{buildroot}

%pre
#=================================================
# Pre Installation
#=================================================

CFRUDDER_FIRST_INSTALL=0
if [ $1 -eq 1 ];then
then
  CFRUDDER_FIRST_INSTALL=1
fi

/opt/rudder/share/package-scripts/rudder-agent-preinst "${CFRUDDER_FIRST_INSTALL}"

%post
#=================================================
# Post Installation
#=================================================

CFRUDDER_FIRST_INSTALL=0
if [ $1 -eq 1 ];then
then
  CFRUDDER_FIRST_INSTALL=1
fi

/opt/rudder/share/package-scripts/rudder-agent-postinst "${CFRUDDER_FIRST_INSTALL}"

%postun
#=================================================
# Post Uninstallation
#=================================================

# Do it only during uninstallation
if [ $1 -eq 0 ]; then

  # Clean up all logrotate leftovers
  rm -rf %{_sysconfdir}/logrotate.d/rudder*

fi

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files
%defattr(-, root, root, 0755)
%{rudderdir}/etc/

#=================================================
# Changelog
#=================================================
%changelog
+* Wed Nov  22 2017 - Rudder Team <rudder-dev@rudder-project.org> %{version}
+- See https://www.rudder-project.org/site/documentation/user-manual/ for changelogs
