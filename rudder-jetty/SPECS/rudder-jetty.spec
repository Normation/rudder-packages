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

%if 0%{?sles_version}
%define jetty_init_script jetty-sles.sh
%else
%define jetty_init_script jetty-rpm.sh
%endif

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - Jetty application server
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 0
License: APLv2.0
URL: http://www.rudder-project.org

Group: Applications/System

#Source1: jetty7/bin/jetty.sh
Source2: rudder-jetty.default
Source3: rudder-jetty.conf
Source4: rudder-jetty

# Prevent rpmbuild to use 64 bits libraries just because of the presence
# of one 64 bits binary in the jetty archive.
AutoReq: 0
AutoProv: 0

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# Dependencies for RHEL/CentOS / OpenJDK7 are a bit specific: on EL6.5, the
# jre7 virtual package was removed. Consistency on EL6 jre/jre7 package is
# not assured and RPM does not provide something like
# "Requires: package | package2" so I am forced to fallback to a hardcoded
# package name.
#
# Also, I would like to have something like %elif here, but not implemented
# in RPM yet...

%if 0%{?rhel} && 0%{?rhel} > 6
Requires: jre >= 1.7
%endif

%if 0%{?rhel} && 0%{?rhel} == 6
Requires: java-1.7.0-openjdk
%endif

%if 0%{!?rhel}
Requires: jre >= 1.6
%endif

# We are providing Jetty, but the name of the provided element depends of the
# OS flavour.


%if 0%{?rhel} || 0%{?fedora}
Provides: jetty-eclipse jetty-server
%endif

# No Jetty provided by SLES...

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
mkdir -p %{buildroot}/opt/rudder/etc/
mkdir -p %{buildroot}/opt/rudder/etc/server-roles.d/
mkdir -p %{buildroot}%{rudderlogdir}/webapp
mkdir -p %{buildroot}/var/rudder/run

cd %{_topdir}/SOURCES

cp -a jetty7 %{buildroot}/opt/rudder

# Init script
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
install -m 755 jetty7/bin/%{jetty_init_script} %{buildroot}/etc/init.d/rudder-jetty
install -m 644 %{SOURCE2} %{buildroot}/etc/default/rudder-jetty
install -m 644 %{SOURCE3} %{buildroot}/opt/rudder/etc/rudder-jetty.conf

install -m 644 %{SOURCE4} %{buildroot}/opt/rudder/etc/server-roles.d/

%pre -n rudder-jetty
#=================================================
# Pre Installation
#=================================================

# Prepare the migration of /etc/default/rudder-jetty
if [ -e /opt/rudder/etc/rudder-jetty.conf ]
then
    if [ $(grep -c '# WARNING #' /opt/rudder/etc/rudder-jetty.conf) -eq 0 ]
    then
        cp /opt/rudder/etc/rudder-jetty.conf /opt/rudder/etc/rudder-jetty.conf.migrate
    fi
fi

if [ -x /opt/jetty7 ]
then
        TMP_BACKUP=`mktemp -d -t jetty.backup.XXXXXXXXXX -q`
        mv /opt/jetty7 $TMP_BACKUP/
fi

%post -n rudder-jetty
#=================================================
# Post Installation
#=================================================

# Migrate old /opt/rudder/etc/rudder-jetty.conf entries
if [ -e /opt/rudder/etc/rudder-jetty.conf.migrate ]
then
    JAVA_XMX_MIGRATE=$(grep '^JAVA_XMX=' /opt/rudder/etc/rudder-jetty.conf.migrate|cut -d = -f 2-)
    JAVA_MAXPERMSIZE_MIGRATE=$(grep '^JAVA_MAXPERMSIZE=' /opt/rudder/etc/rudder-jetty.conf.migrate|cut -d = -f 2-)

    cat > /etc/default/rudder-jetty << EOF
#
# Jetty server configuration
#

# Memory settings
#
# The defaults should be enough for up to ~100 nodes
#
JAVA_XMX=${JAVA_XMX_MIGRATE}
JAVA_MAXPERMSIZE=${JAVA_MAXPERMSIZE_MIGRATE}

# Java VM arguments
#
#JAVA_OPTIONS=""

# Java VM location
#
#JAVA_HOME=/usr/lib/jvm/java-7-openjdk-amd64
#JAVA=java

# Source variables from /opt/rudder/etc/rudder-jetty.conf
# Warning: removing this is likely to prevent Jetty from
# starting correctly
[ -f /opt/rudder/etc/rudder-jetty.conf ] && . /opt/rudder/etc/rudder-jetty.conf
EOF

    rm -f /opt/rudder/etc/rudder-jetty.conf.migrate

fi

# Do this at first install
if [ $1 -eq 1 ]
then
	# Set rudder-agent as service
	chkconfig --del rudder-jetty
	%if 0%{?rhel} && 0%{?rhel} >= 6
	chkconfig rudder-jetty off
	%endif
fi

%preun -n rudder-jetty
#=================================================
# Pre Un-installation
#=================================================

if [[ $1 -eq 0 ]]
then
  service rudder-jetty stop
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
/opt/rudder/etc
%{rudderlogdir}/webapp
/var/rudder/run
/etc/init.d/rudder-jetty
%config(noreplace) /etc/default/rudder-jetty
/opt/rudder/etc/rudder-jetty.conf

#=================================================
# Changelog
#=================================================
%changelog
* Wed Aug 31 2011 - Nicolas PERRON <nicolas.perron@normation.com> 2.3-beta-1
- Remove service start from postinst
* Wed Jul 27 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
