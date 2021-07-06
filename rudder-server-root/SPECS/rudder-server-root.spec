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
%define real_epoch       1398866025

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - root server base package
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: %{real_epoch}
License: GPLv3
URL: https://www.rudder.io/

Group: Applications/System

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

AutoReq: 0
AutoProv: 0

Requires: %(../format-dependencies rpm %{real_epoch}:%{real_version} rudder-webapp rudder-reports rudder-agent)

%description
Rudder is an open source configuration management and audit solution.

This package is essentially a meta-package to install all components required to
run a Rudder root server on a machine.

#=================================================
# Building
#=================================================
%build

#=================================================
# Installation
#=================================================
%install

cd %{_sourcedir}

cd %{_sourcedir}
make --debug install DESTDIR=%{buildroot}

#=================================================
# pretrans is run before all preinst when installing more than one package
#=================================================
%pretrans

set -e

# We need to be sure that uuid.hive is set to root at beginning
mkdir -p /opt/rudder/etc
echo 'root' > /opt/rudder/etc/uuid.hive

mkdir -p /var/rudder/cfengine-community/
echo "127.0.0.1" > /var/rudder/cfengine-community/policy_server.dat

%pre
#=================================================
# Pre Installation
#=================================================

set -e

CFRUDDER_FIRST_INSTALL=$1
LOG_FILE="/var/log/rudder/install/%{name}.log"

echo "`date` - Starting %{name} pre installation script" >> ${LOG_FILE}

%post
#=================================================
# Post Installation
#=================================================

set -e

CFRUDDER_FIRST_INSTALL=$1

/opt/rudder/share/package-scripts/rudder-server-root-postinst "${CFRUDDER_FIRST_INSTALL}"

%postun
#=================================================
# Post Uninstallation
#=================================================

set -e

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
/opt/rudder/etc/
/opt/rudder/share/package-scripts/rudder-server-root-postinst
/usr/lib/systemd/system/rudder-server.service
/opt/rudder/share/versions/rudder-server-root-version

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <dev@rudder.io> %{version}
- See https://docs.rudder.io/changelogs/current/index.html for changelogs

