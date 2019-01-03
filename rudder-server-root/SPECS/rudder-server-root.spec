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
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-sources

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

Requires: rudder-webapp = %{real_epoch}:%{real_version}, rudder-inventory-ldap = %{real_epoch}:%{real_version}, rudder-reports = %{real_epoch}:%{real_version}, rudder-agent = %{real_epoch}:%{real_version}, curl

%if 0%{?sle_version} && 0%{?sle_version} >= 150000
Requires: insserv-compat
%endif

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

cd %{_sourcedir}
make install DESTDIR=%{buildroot}

%pre
#=================================================
# Pre Installation
#=================================================

CFRUDDER_FIRST_INSTALL=$1
LOG_FILE="/var/log/rudder/install/%{name}.log"

echo "`date` - Starting %{name} pre installation script" >> ${LOG_FILE}

## WARNING: This script is a copy of a part of the rudder-agent preinst

if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 ]
then
  mkdir -p /var/rudder/tmp

  if [ -f /etc/init.d/rudder-server ]
  then
    # If old rudder service is here and enabled
    if type chkconfig > /dev/null
    then 
      if chkconfig --list rudder-server 2>&1 | grep -q -e 3:on -e B:on
      then
        touch /var/rudder/tmp/migration-rudder-service-enabled-server
      fi
    fi
  fi
fi

%post
#=================================================
# Post Installation
#=================================================

CFRUDDER_FIRST_INSTALL=$1

/opt/rudder/share/package-scripts/rudder-server-root-postinst "${CFRUDDER_FIRST_INSTALL}"

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
/opt/rudder/etc/
/opt/rudder/share/package-scripts/rudder-server-root-postinst
/etc/init.d/rudder-server

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <rudder-dev@rudder-project.org> %{version}
- See https://www.rudder-project.org/site/documentation/user-manual/ for changelogs
