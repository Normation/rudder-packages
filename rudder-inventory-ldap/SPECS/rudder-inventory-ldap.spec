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
# Specification file for rudder-inventory-ldap
#
# Installs Rudder's OpenLDAP flavor and the
# related files
#
# Copyright (C) 2011 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-inventory-ldap
%define real_epoch       1398866025

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - OpenLDAP
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: %{real_epoch}
License: OpenLDAP public license
URL: http://www.rudder-project.org

Group: Applications/System

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#Generic requirements

BuildRequires: gcc
Requires: rsyslog openssl

#Specific requirements

# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version}
Requires: libltdl7
BuildRequires: libopenssl-devel
%endif

%if 0%{?rhel}
Requires: libtool-ltdl
BuildRequires: openssl-devel libtool-ltdl-devel
%endif

# rpm automatically adds requires and provides on libs and bins it finds.
# provides conflicts with system tools
# and requiring what you are providing is just nuts
%{?filter_provides_in .*\.so$}
%{?filter_requires_in .*\.so$}
%{?filter_setup}

%description
Rudder is an open source configuration management and audit solution.

OpenLDAP Software is an open source implementation of the Lightweight Directory
Access Protocol. See http://www.openldap.org/ for more details.

This package bundles a version of the OpenLDAP directory software to simplify
installing Rudder. It is required by the rudder-webapp and
rudder-inventory-endpoint packages. The LDAP directory is used as storage for
inventory information collected from the managed nodes (that have the
rudder-agent package installed) and for configuration rules and parameters.


#=================================================
# Building
#=================================================
%build

# Ensure an appropriate environment for the compiler
export CFLAGS="$RPM_OPT_FLAGS"

cd %{_sourcedir}
make build

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}

cd %{_sourcedir}
make install DESTDIR=%{buildroot}

#=================================================
# Pre Installation
#=================================================
%pre -n rudder-inventory-ldap

# Only do this on package upgrade
if [ $1 -ne 1 ]
  then
  # When upgrading OpenLDAP, we may need to dump the database
  # so that it can be restored from LDIF
  TIMESTAMP=`date +%%Y%%m%%d%%H%%M%%S`
  # Ensure backup folder exist
  mkdir -p /var/rudder/ldap/backup/
  
  # We need it to be able to open big mdb memory-mapped databases
  ulimit -v unlimited
  
  /opt/rudder/sbin/slapcat -b "cn=rudder-configuration" -l /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.ldif

  # Copy default file for migration
  [ -f /etc/default/rudder-slapd ] && mkdir -p /var/rudder/tmp/ && cp /etc/default/rudder-slapd /var/rudder/tmp/default-rudder-slapd
fi

#=================================================
# Post Installation
#=================================================
%post -n rudder-inventory-ldap

CFRUDDER_FIRST_INSTALL=$1

/opt/rudder/share/package-scripts/rudder-inventory-ldap-postinst "${CFRUDDER_FIRST_INSTALL}"

#=================================================
# Pre Un-installation
#=================================================
%preun -n rudder-inventory-ldap

if [[ $1 -eq 0 ]]
then
systemctl stop rudder-slapd
fi

#=================================================
# Post Uninstallation
#=================================================
%postun -n rudder-inventory-ldap

# Do it only during uninstallation
if [ $1 -eq 0 ]; then
  # Remove the package user
  if getent passwd rudder-slapd >/dev/null; then
    echo -n "INFO: Removing the rudder-slapd user..."
    userdel rudder-slapd >/dev/null 2>&1
    echo " Done"
  fi
fi

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-inventory-ldap
%defattr(-, root, root, 0755)
%attr(- , rudder-slapd,root, 0660) /opt/rudder/etc/openldap/slapd.conf
%config(noreplace) /opt/rudder/etc/openldap/slapd.conf
/usr/lib/systemd/system/rudder-slapd.service
/opt/rudder/etc
/opt/rudder/bin
/opt/rudder/sbin
/opt/rudder/share
/opt/rudder/include
/opt/rudder/lib
/opt/rudder/var
/opt/rudder/libexec
/opt/rudder/share/package-scripts/
/var/log/rudder/ldap
/var/rudder/run

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <rudder-dev@rudder-project.org> %{version}
- See https://www.rudder-project.org/site/documentation/user-manual/ for changelogs
