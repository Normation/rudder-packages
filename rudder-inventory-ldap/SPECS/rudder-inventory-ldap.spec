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

%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder

%define openldap_release 2.4.23

%if 0%{?sles_version} 
%define sysloginitscript /etc/init.d/syslog
%endif
%if 0%{?el6} 
%define sysloginitscript /etc/init.d/rsyslog
%endif

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - OpenLDAP
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 1299256513
License: OpenLDAP public license
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-inventory-ldap.init
Source2: rudder-inventory-ldap.default
Source3: slapd.conf
Source4: inventory.schema
Source5: rudder.schema
Source6: DB_CONFIG

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#Generic requirement
BuildRequires: gcc cyrus-sasl-devel
Requires: rsyslog cyrus-sasl openssl
#Specific requirement
%if 0%{?sles_version} == 11
BuildRequires: libdb-4_5-devel libopenssl-devel
Requires: libdb-4_5
%endif
%if 0%{?sles_version} == 10
BuildRequires: db42-devel openssl-devel
Requires: db42
%endif

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

# rm -rf source rudder inputs
# wget -O openldap.tar.gz ftp://ftp.openldap.org/pub/OpenLDAP/openldap-release/openldap-%{openldap_release}.tgz
# gzip -dc openldap.tar.gz | tar -xvvf -
# mv openldap-%{openldap_release} source
# git clone --depth 1 ssh://git@git.normation.com:5190/rudder.git
# cd rudder && git checkout %{GIT_BRANCH_RUDDER}

cp -rf %{_sourcedir}/openldap-source %{_builddir}

#=================================================
# Building
#=================================================
%build
cd openldap-source

# Ensure an appropriate environment for the compiler
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"

./configure --build=%_target --prefix=%{rudderdir} --enable-dynamic --enable-debug --enable-modules --enable-hdb=mod --enable-monitor=mod --enable-dynlist=mod --with-cyrus-sasl

make %{?_smp_mflags} depend
make %{?_smp_mflags}
#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/opt/rudder
mkdir -p %{buildroot}%{rudderlogdir}/ldap
mkdir -p %{buildroot}/var/rudder/ldap/openldap-data
mkdir -p %{buildroot}/var/rudder/run

cd openldap-source && make install DESTDIR=%{buildroot}

# Init script
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
install -m 755 %{SOURCE1} %{buildroot}/etc/init.d/slapd
install -m 644 %{SOURCE2} %{buildroot}/etc/default/slapd
install -m 644 %{SOURCE3} %{buildroot}/opt/rudder/etc/openldap/slapd.conf
install -m 644 %{SOURCE4} %{buildroot}/opt/rudder/etc/openldap/schema/
install -m 644 %{SOURCE5} %{buildroot}/opt/rudder/etc/openldap/schema/
install -m 644 %{SOURCE6} %{buildroot}/var/rudder/ldap/openldap-data/

mkdir -p %{buildroot}/etc/rsyslog.d
cp %{_sourcedir}/rsyslog/slapd.conf %{buildroot}/etc/rsyslog.d/slapd.conf

%pre -n rudder-inventory-ldap
#=================================================
# Pre Installation
#=================================================

%post -n rudder-inventory-ldap
#=================================================
# Post Installation
#=================================================

echo "Setting slapd as a boot service"
/sbin/chkconfig --add slapd

echo "Reloading syslogd ..."
%{sysloginitscript} restart

echo "All done. Starting slapd..."
/etc/init.d/slapd start

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
%config(noreplace) /etc/rsyslog.d/slapd.conf
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
/etc/init.d/slapd
%config(noreplace) /etc/default/slapd
%config(noreplace) /opt/rudder/etc/openldap/slapd.conf

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 28 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
