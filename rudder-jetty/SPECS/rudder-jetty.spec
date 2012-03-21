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
# Specification file for rudder-jetty
#
# Installs Jetty7
#
# Copyright (C) 2011 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-jetty

%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder

%define jetty_release    7.2.2
%define date_release     20101205

%define _binaries_in_noarch_packages_terminate_build   0

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - Jetty application server
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 1299256513
License: APLv2.0
URL: http://www.rudder-project.org

Group: Applications/System

#Source1: jetty7/bin/jetty.sh
Source2: rudder-jetty.default

Patch1: jetty-init-sles.patch
Patch2: jetty-default-sles.patch
Patch3: jetty-init-rudder.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# BuildRequires:
Requires: jre >= 1.6

%description
Rudder is an open source configuration management and audit solution.

Jetty is an Open Source HTTP Servlet Server written in 100% Java. It is designed
to be light weight, high performance, embeddable, extensible and flexible, thus
making it an ideal platform for serving dynamic HTTP requests from any Java
application. See http://jetty.codehaus.org for more details.

This package bundles a version of the Jetty application server to simplify
installing Rudder. It is required by the rudder-webapp and
rudder-inventory-endpoint packages.


#=================================================
# Source preparation
#=================================================
%prep

cd %{_topdir}/SOURCES
%patch1
%patch2

#=================================================
# Building
#=================================================
%build

echo "No build"

#=================================================
# Installation
#=================================================
%install

rm -rf %{buildroot}

mkdir -p %{buildroot}/opt/rudder
mkdir -p %{buildroot}%{rudderlogdir}/webapp
mkdir -p %{buildroot}/var/rudder/run

cd %{_topdir}/SOURCES

cp -a jetty7 %{buildroot}/opt/rudder
# tar zvxf jetty7.tgz -C %{buildroot}/opt/rudder

# Init script
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
install -m 755 jetty7/bin/jetty-sles.sh %{buildroot}/etc/init.d/jetty
install -m 644 %{SOURCE2} %{buildroot}/etc/default/jetty

%pre -n rudder-jetty
#=================================================
# Pre Installation
#=================================================

if [ -x /opt/jetty7 ]
then
        TMP_BACKUP=`mktemp -d -t jetty.backup.XXXXXXXXXX -q`
        mv /opt/jetty7 $TMP_BACKUP/
fi

%post -n rudder-jetty
#=================================================
# Post Installation
#=================================================

# Do this at first install
if [ $1 -eq 1 ]
then
	# Set rudder-agent as service
	/sbin/chkconfig --add jetty
fi

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-jetty
%defattr(-, root, root, 0755)
/opt/rudder/jetty7
%{rudderlogdir}/webapp
/var/rudder/run
/etc/init.d/jetty
/etc/default/jetty

#=================================================
# Changelog
#=================================================
%changelog
* Wed Aug 31 2011 - Nicolas PERRON <nicolas.perron@normation.com> 2.3-beta-1
- Remove service start from postinst
* Wed Jul 27 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
