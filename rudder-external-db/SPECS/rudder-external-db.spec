#####################################################################################
# Copyright 2011-2019 Normation SAS
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

# Disable totally debug info package
%define debug_package %{nil}

%define real_name               rudder-external-db

# avoid error during byte compilation of pyc since they are removed anyway
%define _python_bytecompile_errors_terminate_build 0

#=================================================
# Header
#=================================================

Summary: Configuration management and audit tool - Rudder external DB
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 0
License: GPLv3
URL: https://www.rudder.io
Source: rudder-sources.tar.bz2

Group: Applications/System

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# Requirements

AutoReq: 0
AutoProv: 0

## General

%description
Rudder is an open source configuration management and audit solution.

This package prevents rudder from installing and configuring a local postgresql database.

#=================================================
# Installation
#=================================================
%install

cd %{_sourcedir}
make --debug install DESTDIR=%{buildroot}

#=================================================
# Post Installation
#=================================================
%post

set -e

/opt/rudder/share/package-scripts/rudder-external-db-postinst

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-external-db
%defattr(-, root, root, 0755)
/opt/rudder/etc/postgresql/reportsSchema-ext.sql
/opt/rudder/share/package-scripts/rudder-external-db-postinst

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <dev@rudder.io> %{version}
- See https://docs.rudder.io/changelogs/current/index.html for changelogs
