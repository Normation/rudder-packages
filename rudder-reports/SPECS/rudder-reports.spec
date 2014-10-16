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
# Specification file for rudder-reports
#
# Configure Postgresql for Rudder
#
# Copyright (C) 2011 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-reports
%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder
%define suse_rsyslogpsl  rsyslog-module-pgsql

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - reports database
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 0
License: AGPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-sources
Source2: rudder.conf
Source3: rudder-reports
Source4: rudder-db

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

#BuildRequires: gcc
Requires: postgresql-server >= 8
Requires: rsyslog >= 4

%if 0%{?sles_version} && 0%{?sles_version} == 10
Requires: %{suse_rsyslogpsl} >= 4
%endif

%if 0%{?sles_version} && 0%{?sles_version} == 11
Requires: %{suse_rsyslogpsl} >= 4
%endif

%if 0%{?rhel} && 0%{?rhel} >= 6
Requires: rsyslog-pgsql >= 4
%endif

%description
Rudder is an open source configuration management and audit solution.

This packages creates and initializes a PostgreSQL database to receive reports
sent from nodes managed with Rudder. These reports are used by rudder-webapp to
calculate compliance to given configuration rules.


#=================================================
# Source preparation
#=================================================
%prep

#=================================================
# Building
#=================================================
%build

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}
# Directories
mkdir -p %{buildroot}%{rudderdir}/etc/postgresql/
mkdir -p %{buildroot}%{rudderdir}/etc/server-roles.d/
mkdir -p %{buildroot}/etc/rsyslog.d

cp %{SOURCE1}/rudder/rudder-core/src/main/resources/reportsSchema.sql %{buildroot}%{rudderdir}/etc/postgresql/
cp -a %{SOURCE2} %{buildroot}/etc/rsyslog.d/rudder.conf

install -m 644 %{SOURCE3} %{buildroot}/opt/rudder/etc/server-roles.d/
install -m 644 %{SOURCE4} %{buildroot}/opt/rudder/etc/server-roles.d/

%pre -n rudder-reports
#=================================================
# Pre Installation
#=================================================

#Check if postgresql is started
service postgresql status > /dev/null

if [ $? -ne 0 ]
then
%if 0%{?rhel} && 0%{?rhel} >= 6
  service postgresql initdb
%endif
  service postgresql start
fi

#HACK: Give rights for login without unix account
RUDDER_PG_DEFINED=`grep "rudder" /var/lib/pgsql/data/pg_hba.conf | wc -l`
if [ ${RUDDER_PG_DEFINED} -le 0 ]; then
	sed -i 1i"host    all             rudder             ::1/128              md5" /var/lib/pgsql/data/pg_hba.conf
	sed -i 1i"host    all             rudder          127.0.0.1/32            md5" /var/lib/pgsql/data/pg_hba.conf
fi

#Apply changes in postgresql
service postgresql reload

%post -n rudder-reports
#=================================================
# Post Installation
#=================================================

#Check if postgresql is started
service postgresql status >/dev/null 2>&1

if [ $? -ne 0 ]
then
  service postgresql start >/dev/null 2>&1
fi

echo -n "INFO: Setting postgresql as a boot service..."
chkconfig --add postgresql >/dev/null 2>&1
%if 0%{?rhel} && 0%{?rhel} >= 6
chkconfig postgresql on >/dev/null 2>&1
%endif
echo " Done"

echo -n "INFO: Waiting for postgresql to be up..."
CPT=0
TIMEOUT=60
while ! su - postgres -c "psql -q --output /dev/null -c \"SELECT COUNT(*) FROM pg_catalog.pg_authid\"" >/dev/null 2>&1
do
        echo -n "."
        sleep 1
        CPT=$((${CPT}+1))
        if [ ${CPT} -eq ${TIMEOUT} ]
        then
                echo -e "\nERROR: Connection to PostgreSQL has not been established before timeout. Exiting"
                exit 1
        fi
done
echo " Done"

dbname="rudder"
usrname="rudder"
CHK_PG_DB=$(su - postgres -c "psql -t -c \"select count(1) from pg_catalog.pg_database where datname = '${dbname}'\"")
CHK_PG_USER=$(su - postgres -c "psql -t -c \"select count(1) from pg_user where usename = '${usrname}'\"")
# Rudder user
if [ ${CHK_PG_USER} -eq 0 ]
then
  echo -n "INFO: Creating Rudder PostgreSQL user..."
  su - postgres -c "psql -q -c \"CREATE USER ${usrname} WITH PASSWORD 'Normation'\"" >/dev/null 2>&1
  echo " Done"
fi

# Rudder database
if [ ${CHK_PG_DB} -eq 0 ]
then
  echo -n "INFO: Creating Rudder PostgreSQL database..."
  su - postgres -c "psql -q -c \"CREATE DATABASE ${dbname} WITH OWNER = ${usrname}\"" >/dev/null 2>&1
  echo "localhost:5432:${dbname}:${usrname}:Normation" > /root/.pgpass
  chmod 600 /root/.pgpass
  psql -q -U rudder -h localhost -d rudder -f %{rudderdir}/etc/postgresql/reportsSchema.sql  >/dev/null 2>&1
  echo " Done"
fi


#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-reports
%defattr(-, root, root, 0755)
%{rudderdir}/etc/postgresql/reportsSchema.sql
%{rudderdir}/etc/server-roles.d/
/etc/rsyslog.d/rudder.conf

#=================================================
# Changelog
#=================================================
%changelog
* Mon Aug 01 2011 - Nicolas Perron <nicolas.perron@normation.com> 2.3-alpha4-1
- Initial package
