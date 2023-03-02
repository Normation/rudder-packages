#####################################################################################
# Copyright 2019 Normation SAS
#####################################################################################
# This program is free software: you can redistribute it and/or modify
# Licensed under the Apache License, Version 2.0 (the "License");
# it under the terms of the GNU General Public License as published by
# you may not use this file except in compliance with the License.
# the Free Software Foundation, Version 3.
# You may obtain a copy of the License at
#
# This program is distributed in the hope that it will be useful,
#     http://www.apache.org/licenses/LICENSE-2.0
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# Unless required by applicable law or agreed to in writing, software
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
######################################################################################

#=================================================
# Variables
#=================================================
%define real_name               rudder-api-client
%define real_epoch              0

# avoid error during byte compilation of pyc since they are removed anyway
%define _python_bytecompile_errors_terminate_build 0

#=================================================
# Header
#=================================================
Summary: Command line tools and python libraries to call Rudder
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: %{real_epoch}
License: Apache-2.0
URL: https://www.rudder.io/
Source: rudder-sources.tar.bz2

Group: Applications/System

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

AutoReq: 0
AutoProv: 0

## Python 2
%if 0%{?rhel} == 7 || ( 0%{?suse_version} && 0%{?suse_version} < 1500 )
BuildRequires: python, python-requests
Requires: python, python-requests, python-urllib3
%else
## Python 3, rhel8
%if 0%{?rhel} >= 8
BuildRequires: python3, python3-requests
Requires: python3, python3-requests, python3-urllib3
%else
## sles 15
BuildRequires: python3, python3-requests
Requires: python3, python3-requests, python3-docopt, python3-urllib3
%endif
%endif

%description
Command line tools and python libraries to call Rudder.

#=================================================
# Source preparation
#=================================================
%prep
%setup -c

#=================================================
# Installation
#=================================================
%install
cd rudder-sources-*/rudder-api-client/

make --debug install DESTDIR=%{buildroot}

# rhel7 does not have python3 so we force python2 instead
%if 0%{?rhel} == 7 || ( 0%{?suse_version} && 0%{?suse_version} < 1500 )
find %{buildroot} -type f | xargs sed -i '1,1s|#!/usr/bin/python3|#!/usr/bin/python2|'
%endif

#=================================================
# Cleaning
#=================================================
%clean
cd rudder-sources-*/rudder-api-client/
make clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-api-client
%defattr(-, root, root, 0755)
/usr/share/rudder-api-client/rudder.py
/usr/bin/rudder-cli
%exclude /usr/share/rudder-api-client/rudder.pyc
%exclude /usr/share/rudder-api-client/rudder.pyo

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <dev@rudder.io> %{version}
- See https://docs.rudder.io/changelogs/current/index.html for changelogs

