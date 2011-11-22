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
# Specification file for rudder-policy-templates
#
# Install Rudder Policy Templates
#
# Copyright (C) 2011 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-policy-templates
%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool -  policy templates
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 1299256513
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-policy-templates

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

#BuildRequires: gcc

%description
Rudder is an open source configuration management and audit solution.

This package contains policy templates, which are configuration models, adapted
to a function or a particular service. By providing parameters to these
templates, you can create configuration rules to manage nodes using Rudder
(nodes are machines with the rudder-agent package installed).


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
mkdir -p %{buildroot}%{rudderdir}/share/

# Policy Templates
cp -r %{SOURCE1}/policies %{buildroot}%{rudderdir}/share/policy-templates
cp -r %{SOURCE1}/tools/ %{buildroot}%{rudderdir}/share/

%pre -n rudder-policy-templates
#=================================================
# Pre Installation
#=================================================


%post -n rudder-policy-templates
#=================================================
# Post Installation
#=================================================


#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-policy-templates
%defattr(-, root, root, 0755)
%{rudderdir}/share/policy-templates/
%{rudderdir}/share/tools/

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 28 2011 - Nicolas Perron <nicolas.perron@normation.com> 2.3-alpha4-1
- Initial package
