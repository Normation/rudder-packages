#####################################################################################
# Copyright 2014 Normation SAS
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
# Specification file for ncf-api-virtualenv
#
# Install the ncf framework API Python virtual
# environment
#
# Copyright (C) 2014 Normation
#=================================================

#=================================================
# Variables
#=================================================

# What is the package name
%define real_name        ncf-api-virtualenv

# Where should the package contents be installed
%define installdir       /usr/share/%{real_name}

#=================================================
# Header
#=================================================

Summary: ncf API Virtualenv - ncf API Python virtual environment
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 0
License: GPLv3
URL: http://www.ncf.io

Group: Applications/System

Source1: ncf_api_flask_app.wsgi

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# Disable dependency auto-generation, to prevent Python requirements
# autodetection, which is not desired here.
AutoReq: 0
AutoProv: 0

# Add Requires here - order is important
Requires: python ncf

%description
ncf is a CFEngine framework aimed at helping newcomers on CFEngine
to be more quickly operationnal and old timers to spend less time
focusing on low level details and have more time for fun things.

This package provides a Python virtual environment to make the use
of the ncf API easier.

#=================================================
# Source preparation
#=================================================
%prep

#=================================================
# Building
#=================================================
%build

# Go into SOURCES
cd %{_sourcedir}

# Build Virtualenv
python virtualenv.py %{real_name}

# Get all requirements via pip
%{real_name}/bin/pip install -r %{_sourcedir}/rudder-sources/ncf/api/requirements.txt

# Clean up unwanted binaries
if [ "z%{real_name}" != "" ]; then
  for i in easy_install python pip; do
      rm -f %{real_name}/bin/${i}*
  done
else
  echo "WARNING: Skipping Virtualenv cleanup, as it"
  echo "WARNING: would operate on /bin ..."
  echo "WARNING: Please make sure the real_name macro"
  echo "WARNING: is defined"
fi

#=================================================
# Installation
#=================================================
%install

rm -rf %{buildroot}

# Directories

mkdir -p %{buildroot}%{installdir}/

# Files

cp -r %{real_name}/* %{buildroot}%{installdir}/

install -m 644 %{SOURCE1} %{buildroot}%{installdir}/

%pre -n ncf-api-virtualenv
#=================================================
# Pre Installation
#=================================================

%post -n ncf-api-virtualenv
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
%files -n ncf-api-virtualenv
%defattr(-, root, root, 0755)
%{installdir}/

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jun 16 2014 - Matthieu CERDA <matthieu.cerda@normation.com> 0.2014160600-1
- Initial release
