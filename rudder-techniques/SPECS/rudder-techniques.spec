#####################################################################################
# Copyright 2012 Normation SAS
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
# Specification file for rudder-techniques
#
# Install Rudder Techniques
#
# Copyright (C) 2012 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-techniques
%define rudderdir        /opt/rudder

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - techniques
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 1299256513
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-sources

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

#BuildRequires: gcc

# Add Requires here - order is important

# The following lines allow this package (rudder-techniques) to 
# replace the older rudder-policy-templates package.
# See http://wiki.mandriva.com/en/Development/Howto/RPM_Advanced#Renaming_a_package
Provides: rudder-policy-templates
Obsoletes: rudder-policy-templates

%description
Rudder is an open source configuration management and audit solution.

This package contains techniques, which are configuration models, adapted
to a function or a particular service. By providing parameters to these
techniques, you can create configuration rules to manage nodes using Rudder
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

cp -r %{SOURCE1}/rudder-techniques/policies %{buildroot}%{rudderdir}/share/techniques
cp -r %{SOURCE1}/rudder-techniques/tools/ %{buildroot}%{rudderdir}/share/

%pre -n rudder-techniques
#=================================================
# Pre Installation
#=================================================


%post -n rudder-techniques
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
%files -n rudder-techniques
%defattr(-, root, root, 0755)
%{rudderdir}/share/techniques/
%{rudderdir}/share/tools/

#=================================================
# Changelog
#=================================================
%changelog
* Wed Feb 22 2012 - Matthieu Cerda <matthieu.cerda@normation.com> 2.4.0-alpha6-1
- Initial package (this package used to be rudder-policy-templates)
