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
%define real_epoch       0

%define rudderdir        /opt/rudder

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - techniques
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

#BuildRequires: gcc

# Add Requires here - order is important
Requires: ncf >= 1398866025:1.2.0.201709201540

# The following lines allow this package (rudder-techniques) to 
# replace the older rudder-policy-templates package.
# See http://wiki.mandriva.com/en/Development/Howto/RPM_Advanced#Renaming_a_package
Provides: rudder-policy-templates
Obsoletes: rudder-policy-templates

# Use our own dependency generator
%global _use_internal_dependency_generator 0
%global __find_requires_orig %{__find_requires}
%define __find_requires %{_sourcedir}/filter-reqs.pl true %{__find_requires_orig}
%global __find_provides_orig %{__find_provides}
%define __find_provides %{_sourcedir}/filter-reqs.pl true %{__find_provides_orig}

%description
Rudder is an open source configuration management and audit solution.

This package contains Techniques, which are configuration models,
adapted to a function or a particular service. By providing parameters to these
templates, you can create rules to manage nodes using Rudder
(nodes are machines using the rudder-agent package).

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

cp -r %{SOURCE1}/rudder-techniques/techniques/ %{buildroot}%{rudderdir}/share/
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
