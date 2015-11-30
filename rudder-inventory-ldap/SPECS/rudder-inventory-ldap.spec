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

%if 0%{?sles_version} 
%define syslogservicename syslog
%endif

%if 0%{?rhel} == 5 || 0%{?el5}
%define syslogservicename syslog
%endif

%if 0%{?rhel} && 0%{?rhel} > 5
%define syslogservicename rsyslog
%endif

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - OpenLDAP
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 0
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
# This file will contain path of /opt/rudder/lib for ld which will
# find there all necessary libraries for BerkeleyDB.
Source9: rudder-inventory-ldap.conf
Source10: rudder-slapd.conf

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#Generic requirements

BuildRequires: gcc
Requires: rsyslog openssl

#Specific requirements

%if 0%{?sles_version} && 0%{?sles_version} == 10
BuildRequires: openssl-devel
%endif

%if 0%{?sles_version} && 0%{?sles_version} == 11
BuildRequires: libopenssl-devel
%endif

%if 0%{?rhel} && 0%{?rhel} < 7
BuildRequires: openssl-devel libtool-ltdl-devel
%endif

%if 0%{?rhel} && 0%{?rhel} >= 7
BuildRequires: openssl-devel libtool-ltdl-devel
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

cp -rf %{_sourcedir}/berkeleydb-source %{_builddir}
cp -rf %{_sourcedir}/openldap-source %{_builddir}

#=================================================
# Building
#=================================================
%build

# Ensure an appropriate environment for the compiler
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"

# 1 - BerkeleyDB
cd berkeleydb-source/build_unix/
../dist/configure --build=%{_target} --prefix=%{rudderdir}

make %{?_smp_mflags}
make install

cd ../..

# 2 - OpenLDAP
cd openldap-source

export LD_LIBRARY_PATH="/opt/rudder/lib"
export CPPFLAGS="-I/opt/rudder/include"
export LDFLAGS="-L/opt/rudder/lib"

./configure --build=%{_target} --prefix=%{rudderdir} --libdir=%{rudderdir}/lib/ldap --enable-dynamic --enable-debug --enable-modules --enable-hdb=mod --enable-monitor=mod --enable-dynlist=mod

make %{?_smp_mflags} depend
make %{?_smp_mflags}

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/etc/ld.so.conf.d
mkdir -p %{buildroot}/opt/rudder/
mkdir -p %{buildroot}/etc/ld.so.conf.d
mkdir -p %{buildroot}/opt/rudder/etc/server-roles.d/
mkdir -p %{buildroot}%{rudderlogdir}/ldap
mkdir -p %{buildroot}/var/rudder/ldap/openldap-data
mkdir -p %{buildroot}/var/rudder/run

# Now, we install BerkeleyDB in %{buildroot} to package it
cd berkeleydb-source/build_unix && make install DESTDIR=%{buildroot}

cd ../../openldap-source && make install DESTDIR=%{buildroot}

# Remove useless BerkeleyDB documentation
rm -rf %{buildroot}/opt/rudder/docs

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

# Install /etc/ld.so.conf.d/rudder.conf in order to use libraries
# contained in /opt/rudder/lib like BerkeleyDB
install -m 644 %{SOURCE9} %{buildroot}/etc/ld.so.conf.d/rudder-inventory-ldap.conf

# Syslog configuration
mkdir -p %{buildroot}/etc/rsyslog.d
cp %{_sourcedir}/rsyslog/rudder-slapd.conf %{buildroot}/etc/rsyslog.d/rudder-slapd.conf


%pre -n rudder-inventory-ldap
#=================================================
# Pre Installation
#=================================================

# Only do this on package upgrade
if [ $1 -gt 1 ]
then

	# When upgrading OpenLDAP, we may need to dump the database
	# so that it can be restored from LDIF in case the new
	# package uses a different version of BerkeleyDB (libdb)
	TIMESTAMP=`date +%%Y%%m%%d%%H%%M%%S`
	# Ensure backup folder exist
	mkdir -p /var/rudder/ldap/backup/

	/opt/rudder/sbin/slapcat -b "cn=rudder-configuration" -l /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.ldif

	# Store version of libdb used to make this backup
	echo $(ldd /opt/rudder/sbin/slapcat | grep libdb | cut -d"=" -f1) > /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.libdb-version

fi

%post -n rudder-inventory-ldap
#=================================================
# Post Installation
#=================================================

# Reload the linker cache (to acknowledge BerkeleyDB's presence if needed)
if [ -f /etc/ld.so.conf.d/rudder-inventory-ldap.conf ]; then
        ldconfig
fi

echo -n "INFO: Setting rudder-slapd as a boot service..."
chkconfig --add rudder-slapd >/dev/null 2>&1

%if 0%{?rhel} && 0%{?rhel} >= 6
chkconfig rudder-slapd on
%endif
echo " Done"

echo -n "INFO: Reloading syslogd... "
service %{syslogservicename} restart >/dev/null 2>&1
echo " Done"

RUDDER_SHARE=/opt/rudder/share
RUDDER_UPGRADE_TOOLS=${RUDDER_SHARE}/upgrade-tools
BACKUP_LDIF_PATH=/var/rudder/ldap/backup/
BACKUP_LDIF_REGEX="^/var/rudder/ldap/backup/openldap-data-pre-upgrade-\([0-9]\{14\}\)\.ldif$"

# Do we have a backup file from a previous upgrade?
BACKUP_LDIF=$(find ${BACKUP_LDIF_PATH} -regextype sed -regex "${BACKUP_LDIF_REGEX}" 2>&1 | sort -nr | head -n1)
if [ -n "${BACKUP_LDIF}" ]; then
	TIMESTAMP=$(echo ${BACKUP_LDIF} | sed "s%${BACKUP_LDIF_REGEX}%\1%")

	# If this is an upgrade from an older version of rudder-inventory-ldap
   	# we may need to drop and reimport the database if the underlying version
	# of libdb has changed.
	if [ -f "/var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.libdb-version" ]; then
		# Did the underlying version of libdb change?
		current_libdb_version=$(ldd /opt/rudder/sbin/slapcat | grep libdb | cut -d"=" -f1)
		previous_libdb_version=$(cat /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.libdb-version)
		if [ "${current_libdb_version}" != "${previous_libdb_version}" ]; then
			# OK, we need to remove the old DB and import the backup
			REINIT_DB="yes"
		fi
	fi

	if [ "${REINIT_DB}" = "yes" ]; then

		# Do we have a database backup to restore from?
		if [ ! -f ${BACKUP_LDIF} ]; then
			echo >&2 "ERROR: No database backup for old version. Can't upgrade rudder-inventory-ldap database..."
			exit 1
		fi

		# Stop OpenLDAP - use forcestop to avoid the init script failing
		# when trying to do the backup with bad libdb versions
		echo -n "INFO: Stopping rudder-slapd..."
		service rudder-slapd forcestop >/dev/null 2>&1
		echo " Done"

		# Backup the old database
		LDAP_BACKUP_DIR="/var/rudder/ldap/openldap-data-backup-upgrade-on-${TIMESTAMP}/"
		mkdir -p "${LDAP_BACKUP_DIR}"
		find /var/rudder/ldap/openldap-data -maxdepth 1 -mindepth 1 -not -name "DB_CONFIG" -exec mv {} ${LDAP_BACKUP_DIR} \;

		# Import the backed up database
		/opt/rudder/sbin/slapadd -q -l ${BACKUP_LDIF}

		# Start OpenLDAP
		echo -n "INFO: Starting rudder-slapd..."
		service rudder-slapd start >/dev/null 2>&1
		echo " Done"

		echo "INFO: OpenLDAP database was successfully upgraded to new format"

		if [ -x /opt/rudder/bin/rudder-upgrade ]
		then
			echo "INFO: Running the Rudder upgrade script to replay LDAP migrations on the old database content..."
			/opt/rudder/bin/rudder-upgrade
		fi

		echo "INFO: You can safely remove the backups in ${LDAP_BACKUP_DIR}"
		echo "INFO: and ${BACKUP_LDIF}"
	fi
fi

# Need to restart to take schema changes into account
echo -n "INFO: Restarting rudder-slapd..."
service rudder-slapd force-reload >/dev/null 2>&1
echo " Done"

%preun -n rudder-inventory-ldap
#=================================================
# Pre Un-installation
#=================================================

if [[ $1 -eq 0 ]]
then
  service rudder-slapd forcestop
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
%config(noreplace) /etc/ld.so.conf.d/rudder-inventory-ldap.conf

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 28 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
