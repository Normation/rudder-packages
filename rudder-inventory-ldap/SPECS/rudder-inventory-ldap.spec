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

%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder

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

Source1: rudder-inventory-ldap.init
Source2: rudder-inventory-ldap.default
Source3: slapd.conf
Source4: inventory.schema
Source5: rudder.schema
Source6: DB_CONFIG
Source7: rudder-inventory-ldap
Source8: rudder-ldap
Source10: rudder-slapd.conf
Source11: rudder-slapd-configure

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

%if 0%{?sle_version} && 0%{?sle_version} >= 150000
Requires: insserv-compat
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
# Source preparation
#=================================================
%prep

cp -rf %{_sourcedir}/openldap-source %{_builddir}

#=================================================
# Building
#=================================================
%build

# Ensure an appropriate environment for the compiler
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"

# OpenLDAP
cd openldap-source

export LD_LIBRARY_PATH="/opt/rudder/lib"
export CPPFLAGS="-I/opt/rudder/include"
export LDFLAGS="-L/opt/rudder/lib"

./configure --build=%{_target} --prefix=%{rudderdir} --libdir=%{rudderdir}/lib/ldap --enable-dynamic --enable-debug --enable-modules --enable-monitor=mod --enable-dynlist=mod --enable-mdb=yes --enable-hdb=no --enable-bdb=no

make %{?_smp_mflags} depend
make %{?_smp_mflags}

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/opt/rudder/
mkdir -p %{buildroot}/opt/rudder/etc/server-roles.d/
mkdir -p %{buildroot}%{rudderlogdir}/ldap
mkdir -p %{buildroot}/var/rudder/ldap/openldap-data
mkdir -p %{buildroot}/var/rudder/run

cd openldap-source && make install DESTDIR=%{buildroot}

# Init script
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
install -m 755 %{SOURCE1} %{buildroot}/etc/init.d/rudder-slapd
install -m 644 %{SOURCE2} %{buildroot}/etc/default/rudder-slapd
install -m 644 %{SOURCE10} %{buildroot}/opt/rudder/etc/rudder-slapd.conf

install -m 644 %{SOURCE3} %{buildroot}/opt/rudder/etc/openldap/slapd.conf
install -m 644 %{SOURCE4} %{buildroot}/opt/rudder/etc/openldap/schema/
install -m 644 %{SOURCE5} %{buildroot}/opt/rudder/etc/openldap/schema/
install -m 644 %{SOURCE6} %{buildroot}/var/rudder/ldap/openldap-data/

install -m 644 %{SOURCE7} %{buildroot}/opt/rudder/etc/server-roles.d/
install -m 644 %{SOURCE8} %{buildroot}/opt/rudder/etc/server-roles.d/

# Install mdb configuration file
install -m 755 %{SOURCE11} %{buildroot}/opt/rudder/bin/rudder-slapd-configure

# Syslog configuration
mkdir -p %{buildroot}/etc/rsyslog.d
cp %{_sourcedir}/rsyslog/rudder-slapd.conf %{buildroot}/etc/rsyslog.d/rudder-slapd.conf


%pre -n rudder-inventory-ldap
#=================================================
# Pre Installation
#=================================================

# Only do this on package upgrade
if [ $1 -ne 1 ]
then
        # We need it to be able to open big mdb memory-mapped databases
        ulimit -v unlimited

	# When upgrading OpenLDAP, we may need to dump the database
	# so that it can be restored from LDIF
	TIMESTAMP=`date +%%Y%%m%%d%%H%%M%%S`
	# Ensure backup folder exist
	mkdir -p /var/rudder/ldap/backup/

        # We need it to be able to open big mdb memory-mapped databases
        ulimit -v unlimited

	/opt/rudder/sbin/slapcat -b "cn=rudder-configuration" -l /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.ldif
fi

%post -n rudder-inventory-ldap
#=================================================
# Post Installation
#=================================================

# ldconfig only necessary when upgrading from 4.1 to >4.2
if [[ $1 -gt 1 ]]; then 
  ldconfig
fi

echo -n "INFO: Setting rudder-slapd as a boot service..."
chkconfig --add rudder-slapd >/dev/null 2>&1

# mandatory with systemd wrapper for old init
systemctl daemon-reload

systemctl enable rudder-slapd
echo " Done"

# Need to restart to take schema changes into account
echo -n "INFO: Restarting rudder-slapd..."
# during upgrade, service may not have been started with systemctl
# detect first if rudder-slapd is seen running ?
RUDDER_SLAPD_RUNNING_SERVICE=0
RUDDER_SLAPD_RUNNING_SYSTEMCTL=0
if service rudder-slapd status > /dev/null; then 
  RUDDER_SLAPD_RUNNING_SERVICE=1
fi
if systemctl is-active rudder-slapd > /dev/null; then 
  RUDDER_SLAPD_RUNNING_SYSTEMCTL=1
fi

if [ $RUDDER_SLAPD_RUNNING_SERVICE -eq 1 ] && [ $RUDDER_SLAPD_RUNNING_SYSTEMCTL -eq 0 ]
then
  # systemctl doesn't know the service is started, we stop it with service first
  service rudder-slapd stop > /dev/null
fi

systemctl restart rudder-slapd >/dev/null
echo " Done"

%preun -n rudder-inventory-ldap
#=================================================
# Pre Un-installation
#=================================================

if [[ $1 -eq 0 ]]
then
systemctl stop rudder-slapd
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
%{rudderlogdir}/ldap
%config(noreplace) /etc/rsyslog.d/rudder-slapd.conf
%config(noreplace) /var/rudder/ldap/openldap-data/DB_CONFIG
/var/rudder/run
/opt/rudder/etc
/opt/rudder/bin
/opt/rudder/sbin
/opt/rudder/share
/opt/rudder/include
/opt/rudder/lib
/opt/rudder/var
/opt/rudder/libexec
/etc/init.d/rudder-slapd
%config(noreplace) /etc/default/rudder-slapd
/opt/rudder/etc/rudder-slapd.conf
%config(noreplace) /opt/rudder/etc/openldap/slapd.conf

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <rudder-dev@rudder-project.org> %{version}
- See https://www.rudder-project.org/site/documentation/user-manual/ for changelogs
