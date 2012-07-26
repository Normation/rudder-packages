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
%if 0%{?el5} 
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
%if 0%{?rhel}
BuildRequires: db4-devel openssl-devel libtool-ltdl-devel
Requires: db4
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

# Syslog configuration
mkdir -p %{buildroot}/etc/rsyslog.d
cp %{_sourcedir}/rsyslog/slapd.conf %{buildroot}/etc/rsyslog.d/slapd.conf

# Upgrade tools
mkdir -p %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-upgrade-LDAP-schema-2.3-2.4-PI-PT-CR-names-changed.pl %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-upgrade-LDAP-schema-2.3-2.4-PI-PT-CR-names-changed-attribute-map.csv %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-upgrade-LDAP-schema-2.3-2.4-PI-PT-CR-names-changed-objectclass-map.csv %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-upgrade-LDAP-schema-2.3-2.4-PI-PT-CR-names-changed-branches-map.csv %{buildroot}%{rudderdir}/share/upgrade-tools/

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
	/opt/rudder/sbin/slapcat -b "cn=rudder-configuration" -l /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.ldif

	# Store version of libdb used to make this backup
	echo $(ldd /opt/rudder/sbin/slapcat | grep libdb | cut -d"=" -f1) > /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.libdb-version

fi

%post -n rudder-inventory-ldap
#=================================================
# Post Installation
#=================================================

echo "Setting slapd as a boot service"
/sbin/chkconfig --add slapd

echo "Reloading syslogd ..."
%{sysloginitscript} restart

BACKUP_LDIF_PATH=/var/rudder/ldap/backup/
BACKUP_LDIF_REGEX="^/var/rudder/ldap/backup/openldap-data-pre-upgrade-\([0-9]\{14\}\)\.ldif$"

# Do we have a backup file from a previous upgrade?
BACKUP_LDIF=`find ${BACKUP_LDIF_PATH} -regextype sed -regex "${BACKUP_LDIF_REGEX}" | sort -nr | head -n1`
if [ "z${BACKUP_LDIF}" != "z" ]; then
	TIMESTAMP=`echo ${BACKUP_LDIF} | sed "s%${BACKUP_LDIF_REGEX}%\1%"`

	# If this is an upgrade from a Rudder 2.3 to 2.4, we need to
	# rename a whole load of objectClasses and attributes in the LDIF file
	OLD_LDAP_TEST=`grep -Ei "^policyInstanceId::? " ${BACKUP_LDIF} | wc -l`
	if [ ${OLD_LDAP_TEST} -ne 0 ]; then
		echo "The Rudder OpenLDAP schema is not up to date."
		echo "You will see some warnings about UNKNOWN attributeDescription."
		echo "Updating..."

		RUDDER_SHARE=/opt/rudder/share
		RUDDER_UPGRADE_TOOLS=${RUDDER_SHARE}/upgrade-tools

		cp ${BACKUP_LDIF} ${BACKUP_LDIF}.renamed
		BACKUP_LDIF=${BACKUP_LDIF}.renamed
		${RUDDER_UPGRADE_TOOLS}/rudder-upgrade-LDAP-schema-2.3-2.4-PI-PT-CR-names-changed.pl ${BACKUP_LDIF}
		echo "...done."

		REINIT_DB="yes"
	fi  

	# The format for the cpuSpeed attribute changed in 2.3.8, 2.4.0 and above
   	# Check if we still have any values in the old format
	LDAP_CPUSPEED_IS_NOT_INTEGER=`grep -E "^cpuSpeed: [0-9]+\.[0-9]+$" ${BACKUP_LDIF} | wc -l`
	if [ ${LDAP_CPUSPEED_IS_NOT_INTEGER} -ne 0 ]; then
		cp ${BACKUP_LDIF} ${BACKUP_LDIF}.cpuSpeedFixed
		BACKUP_LDIF=${BACKUP_LDIF}.cpuSpeedFixed
		sed -i "s%^cpuSpeed: \(.*\)\..*%cpuSpeed: \1%" ${BACKUP_LDIF}

		echo "Some cpuSpeed attributes were converted to integers in the LDAP database"

		REINIT_DB="yes"
    fi

	# If this is an upgrade from an older version of rudder-inventory-ldap
   	# we may need to drop and reimport the database if the underlying version
	# of libdb has changed.
	if [ -f /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.libdb-version ]; then
		# Did the underlying version of libdb change?
		current_libdb_version=$(echo `ldd /opt/rudder/sbin/slapcat | grep libdb | cut -d"=" -f1`)
		previous_libdb_version=`cat /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.libdb-version`
		if [ ${current_libdb_version} != ${previous_libdb_version} ]; then
			# OK, we need to remove the old DB and import the backup
			REINIT_DB="yes"
		fi
	fi

	# If somes attribute exists in nodeId=root,ou=Nodes,cn=rudder-configuration
	# we have to redefine the ldif in order to move them to 
	#  nodeId=root,ou=Accepted Inventories,ou=Inventories,cn=rudder-configuration
	CHECK_NODE_ROOT_ATTR=`/opt/rudder/bin/ldapsearch -H ldap://localhost -x -w ${LDAP_PASSWORD} -D ${LDAP_USER} -b "nodeId=root,ou=Nodes,ou=Accepted Inventories,ou=Inventories,cn=rudder-configuration" -LLL | grep -iE "^(nodeHostname|publicKey|ipHostNumber|agentName|inventoryDate|localAdministratorAccountName|policyServerId)" | wc -l`
	if [${CHECK_NODE_ROOT_ATTR} -ne 0 ]
		cp ${BACKUP_LDIF} ${BACKUP_LDIF}.ldapEntriesFixed
		BACKUP_LDIF=${BACKUP_LDIF}.ldapEntriesFixed
		REINIT_DB="yes"
	fi

	if [ "z${REINIT_DB}" = "zyes" ]; then
		# Do we have a database backup to restore from?
		if [ ! -f ${BACKUP_LDIF} ]; then
			echo >&2 "No database backup for old version. Can't upgrade rudder-inventory-ldap database!"
			exit 1
		fi

		# Stop OpenLDAP - use forcestop to avoid the init script failing
		# when trying to do the backup with bad libdb versions
		/etc/init.d/slapd forcestop

		# Backup the old database
		mkdir -p /var/rudder/ldap/openldap-data-backup-upgrade-to-$2-${TIMESTAMP}/
		find /var/rudder/ldap/openldap-data -maxdepth 1 -mindepth 1 -not -name "DB_CONFIG" -exec mv {} /var/rudder/ldap/openldap-data-backup-upgrade-to-$2-${TIMESTAMP}/ \;

		# Import the backed up database
		/opt/rudder/sbin/slapadd -q -l ${BACKUP_LDIF}

		# Start OpenLDAP
		/etc/init.d/slapd start

		echo "OpenLDAP database was successfully upgraded to new format"
		echo "You can safely remove the backups in /var/rudder/ldap/openldap-data-backup-upgrade-to-$2/"
		echo "and ${BACKUP_LDIF}"
	fi
fi

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
