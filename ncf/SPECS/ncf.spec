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
# Specification file for ncf
#
# Install the ncf framework
#
# Copyright (C) 2013 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        ncf
%define installdir       /usr/share
%define bindir           /usr/bin

#=================================================
# Header
#=================================================
Summary: ncf - CFEngine framework
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 0
License: GPLv3
URL: http://www.ncf.io

Group: Applications/System

Source1: rudder-sources

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

#BuildRequires: gcc

# Add Requires here - order is important

%description
ncf is a CFEngine framework aimed at helping newcomers on CFEngine
to be more quickly operationnal and old timers to spend less time
focusing on low level details and have more time for fun things.

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
mkdir -p %{buildroot}%{installdir}/
mkdir -p %{buildroot}%{bindir}/

cp -r %{SOURCE1}/ncf/ %{buildroot}%{installdir}/

# Create a symlink to make ncf available as part of the
# default PATH
ln -sf %{installdir}/ncf/ncf %{buildroot}%{bindir}/ncf

%pre -n ncf
#=================================================
# Pre Installation
#=================================================


%post -n ncf
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
%files -n ncf
%defattr(-, root, root, 0755)
%{installdir}/ncf/
%config(noreplace) %{installdir}/ncf/tree/ncf.conf
%{bindir}/ncf

#=================================================
# Changelog
#=================================================
%changelog
* Thu Dec 05 2013 - Matthieu CERDA <matthieu.cerda@normation.com> 0.2013120500-1
- Initial release
