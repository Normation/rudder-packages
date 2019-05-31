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
# Specification file for rudder-reports
#
# Configure PostgreSQL for Rudder
#
# Copyright (C) 2011- Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name          rudder-reports
%define real_epoch         1398866025

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - reports database
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

Requires: postgresql-server >= 9.2
Requires: rsyslog >= 4

%if 0%{?suse_version}
Requires: rsyslog-module-pgsql >= 4
%endif

%if 0%{?rhel}
Requires: rsyslog-pgsql >= 4
%endif

%description
Rudder is an open source configuration management and audit solution.

This packages creates and initializes a PostgreSQL database to receive reports
sent from nodes managed with Rudder. These reports are used by rudder-webapp to
calculate compliance to given configuration rules.


#=================================================
# Building
#=================================================
%build

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}

cd %{_sourcedir}
make install DESTDIR=%{buildroot}


#=================================================
# Post Installation
#=================================================
%post -n rudder-reports

%if 0%{?rhel}
  /opt/rudder/share/package-scripts/rudder-reports-postinst true
%else
  /opt/rudder/share/package-scripts/rudder-reports-postinst
%endif

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-reports
%defattr(-, root, root, 0755)
/opt/rudder/etc/postgresql/reportsSchema.sql
/opt/rudder/etc/server-roles.d/
/opt/rudder/share/package-scripts/

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <dev@rudder.io> %{version}
- See https://docs.rudder.io/changelogs/current/index.html for changelogs

