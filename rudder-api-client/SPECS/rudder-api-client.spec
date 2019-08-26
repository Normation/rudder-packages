#####################################################################################
# Copyright 2019 Normation SAS
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
# Variables
#=================================================
%define real_name               rudder-api-client
%define real_epoch              0
%define real_version            1

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
License: GPLv3
URL: https://www.rudder.io/

Group: Applications/System

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

AutoReq: 0
AutoProv: 0

## Python 3
%if 0%{?rhel} && 0%{?rhel} == 7
BuildRequires: python, python-requests
Requires: python, python-requests
%endif
%if 0%{?rhel} && 0%{?rhel} == 8
BuildRequires: python3, python3-requests
Requires: python3, python3-requests
%endif
# Doc for suse versioning https://en.opensuse.org/openSUSE:Packaging_for_Leap
%if 0%{?suse_version} && 0%{?suse_version} < 1500
BuildRequires: python, python-requests
Requires: python, python-request
%endif
%if 0%{?suse_version} && 0%{?suse_version} >= 1500
BuildRequires: python3, python3-requests
Requires: python3, python3-requests
%endif

%description
Command line tools and python libraries to call Rudder.

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}

cd %{_sourcedir}
# rhel7 and sles12 don't have mod wsgi python 3 so we force python2 instead
%if 0%{?rhel} == 7 || ( 0%{?suse_version} && 0%{?suse_version} < 1500 )
find . -type f | xargs sed -i '1,1s|#!/usr/bin/python3|#!/usr/bin/python2|'
%endif
make install DESTDIR=%{buildroot}

#=================================================
# Cleaning
#=================================================
%clean
cd %{_sourcedir} && make clean
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

