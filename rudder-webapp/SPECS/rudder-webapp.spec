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
# Specification file for rudder-webapp
#
# Copyright (C) 2011- Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-webapp
%define real_epoch       1398866025

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - transitional package
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: %{real_epoch}
License: GPLv3
URL: https://www.rudder.io/

Group: Applications/System

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-webapp-%(%{__id_u} -n)
BuildArch: noarch

AutoReq: 0
AutoProv: 0

%description
Rudder is an open source configuration management and audit solution.

This is a transitional package.
It can be safely removed.

#=================================================
# Building
#=================================================
%build

#=================================================
# Installation
#=================================================
%install

%pre
#=================================================
# Pre Installation
#=================================================

%post
#=================================================
# Post Installation
#=================================================

%postun
#=================================================
# Post Uninstallation
#=================================================


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

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <dev@rudder.io> %{version}
- See https://docs.rudder.io/changelogs/current/index.html for changelogs

