#####################################################################################
# Copyright 2011- Normation SAS
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
# Configure PostgreSQL for Rudder
#
# Copyright (C) 2011- Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name          rudder-reports
%define real_epoch         1398866025

%define rudderdir          /opt/rudder
%define ruddervardir       /var/rudder
%define rudderlogdir       /var/log/rudder
%define suse_rsyslog_pgsql rsyslog-module-pgsql

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - reports database
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: %{real_epoch}
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-sources
Source2: rudder-reports
Source3: rudder-db

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch


Requires: postgresql-server >= 9.2
Requires: rsyslog >= 4

# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version}
Requires: %{suse_rsyslog_pgsql} >= 4
%endif

%if 0%{?rhel}
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

cp %{SOURCE1}/rudder/rudder-core/src/main/resources/reportsSchema.sql %{buildroot}%{rudderdir}/etc/postgresql/

install -m 644 %{SOURCE2} %{buildroot}/opt/rudder/etc/server-roles.d/
install -m 644 %{SOURCE3} %{buildroot}/opt/rudder/etc/server-roles.d/

%pre -n rudder-reports
#=================================================
# Pre Installation
#=================================================


%post -n rudder-reports
#=================================================
# Post Installation
#=================================================

POSTGRESQL_SERVICE_NAME=$(systemctl list-unit-files --type service | awk -F'.' '{print $1}' | grep -E "^postgresql-?[0-9]*$" | tail -n 1)
%if 0%{?suse_version} && 0%{?suse_version} < 1500
  # on sles 12 postgresql uses an old init file but is properly managed by systemd so this is the only place we need a workaround
  POSTGRESQL_SERVICE_NAME=$(chkconfig 2>/dev/null | awk '{ print $1 }' | grep "postgresql" | tail -n 1)
%endif

if [ -z "${POSTGRESQL_SERVICE_NAME}" ]; then
  POSTGRESQL_SERVICE_NAME="postgresql"
fi

# Check if PostgreSQL is started
systemctl status ${POSTGRESQL_SERVICE_NAME} 2>&1 >/dev/null

if [ $? -ne 0 ]; then
%if 0%{?rhel}
  # Detecting path of postgresql-setup
  POSTGRESQL_SETUP=$(ls -1  /usr/pgsql-*/bin/postgresql*-setup 2>/dev/null | sort -V | tail -1)
  if [ -z "${POSTGRESQL_SETUP}" ]; then
    POSTGRESQL_SETUP="postgresql-setup"
  fi

  echo -n "INFO: Initializing PostgreSQL ..."
  ${POSTGRESQL_SETUP} initdb
  echo " Done"
%endif

  systemctl start ${POSTGRESQL_SERVICE_NAME} 
fi

PG_HBA_FILE=$(su - postgres -c "psql -t -P format=unaligned -c 'show hba_file';")
if [ $? -ne 0 ]; then
  echo "Postgresql failed to start! Halting"
  exit 1
fi

#HACK: Give rights for login without unix account
if [ -f ${PG_HBA_FILE} ]; then
  RUDDER_PG_DEFINED=`grep "rudder" ${PG_HBA_FILE} | wc -l`
  if [ ${RUDDER_PG_DEFINED} -le 0 ]; then
    # we cannot put at the bottom the rules
    # Check that the defining line for file is there
    grep -q "^# TYPE" ${PG_HBA_FILE}
    if [ $? -eq 0 ]; then
      sed -i  '/^# TYPE.*/a # Rudder specific access for PostgreSQL' ${PG_HBA_FILE}
    else
      # Put it on top
      sed -i 1i"# Rudder specific access for PostgreSQL" ${PG_HBA_FILE}
    fi
    sed -i  '/^# Rudder specific access for PostgreSQL/a host    all             rudder          127.0.0.1/32            md5' ${PG_HBA_FILE}
    sed -i  '/^# Rudder specific access for PostgreSQL/a host    all             rudder             ::1/128              md5' ${PG_HBA_FILE}

    # Apply changes in PostgreSQL
    systemctl reload ${POSTGRESQL_SERVICE_NAME}
  fi
fi

echo -n "INFO: Setting PostgreSQL as a boot service..."
%if 0%{?rhel}
  systemctl enable ${POSTGRESQL_SERVICE_NAME} >/dev/null 
%endif
echo " Done"

echo -n "INFO: Waiting for PostgreSQL to be up..."
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

DBNAME="rudder"
USERNAME="rudder"
CHK_PG_DB=$(su - postgres -c "psql -t -c \"select count(1) from pg_catalog.pg_database where datname = '${DBNAME}'\"")
CHK_PG_USER=$(su - postgres -c "psql -t -c \"select count(1) from pg_user where usename = '${USERNAME}'\"")

# Rudder user
if [ ${CHK_PG_USER} -eq 0 ]
then
  echo -n "INFO: Creating Rudder PostgreSQL user..."
  su - postgres -c "psql -q -c \"CREATE USER ${USERNAME} WITH PASSWORD 'Normation'\"" >/dev/null 2>&1
  echo " Done"
fi

# Rudder database
if [ ${CHK_PG_DB} -eq 0 ]
then
  echo -n "INFO: Creating Rudder PostgreSQL database..."
  su - postgres -c "psql -q -c \"CREATE DATABASE ${DBNAME} WITH OWNER = ${USERNAME}\"" >/dev/null 2>&1
  echo "localhost:5432:${DBNAME}:${USERNAME}:Normation" > /root/.pgpass
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

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <rudder-dev@rudder-project.org> %{version}
- See https://www.rudder-project.org/site/documentation/user-manual/ for changelogs
