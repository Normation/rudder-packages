#####################################################################################
# Copyright 2011-2014 Normation SAS
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
# Specification file for rudder-server-relay
#=================================================
#
# Sets up a machine to become a Rudder relay
#
#=================================================

#=================================================
# Variables
#=================================================

%define real_name               rudder-server-relay
%define rudderdir               /opt/rudder
%define ruddervardir            /var/rudder
%define rudderlogdir            /var/log/rudder

%if 0%{?sles_version}
%define apache                  apache2
%define apache_tools            apache2-utils
%define apache_group            www
%define htpasswd_cmd            htpasswd2
%define apache_vhost_dir        %{apache}/vhosts.d
%endif
%if 0%{?rhel} || 0%{?fedora}
%define apache                  httpd
%define apache_tools            httpd-tools
%define apache_group            apache
%define htpasswd_cmd            htpasswd
%define apache_vhost_dir        %{apache}/conf.d
%endif

#=================================================
# Header
#=================================================

Summary: Configuration management and audit tool - Rudder server relay package
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 0
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-relay-vhost.conf
Source2: rudder-networks.conf
Source3: rudder-networks-24.conf

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# Requirements

## General
Requires: rsyslog

## RHEL
%if 0%{?rhel}
Requires: httpd httpd-tools
%endif

## SuSE
%if 0%{?sles_version}
Requires: apache2 apache2-utils
%endif

%description
Rudder is an open source configuration management and audit solution.

This package is essentially a meta-package to install all components required to
run a Rudder relay server on a machine.

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
mkdir -p %{buildroot}/etc/%{apache_vhost_dir}
mkdir -p %{buildroot}%{rudderdir}/etc/
mkdir -p %{buildroot}%{ruddervardir}/inventories/incoming
mkdir -p %{buildroot}%{ruddervardir}/inventories/accepted-nodes-updates
mkdir -p %{buildroot}%{rudderlogdir}/apache2/

# Others
install -m 644 %{SOURCE1} %{buildroot}/etc/%{apache_vhost_dir}/rudder-relay-vhost.conf

# Copy stub rudder-networks*.conf
cp %{SOURCE2} %{buildroot}%{rudderdir}/etc/
cp %{SOURCE3} %{buildroot}%{rudderdir}/etc/

%post -n rudder-server-relay
#=================================================
# Post Installation
#=================================================

echo -n "INFO: Setting Apache HTTPd as a boot service..."
chkconfig --add %{apache} 2&> /dev/null
%if 0%{?rhel} && 0%{?rhel} >= 6
chkconfig %{apache} on
%endif
echo " Done"

echo -n "INFO: Stopping Apache HTTPd..."
service %{apache} stop >/dev/null 2>&1
echo " Done"

%if 0%{?sles_version}
# On SuSE, enable the required modules
MODULES_TO_ENABLE="dav dav_fs"

for enmod in ${MODULES_TO_ENABLE}
do
  a2enmod ${enmod} >/dev/null 2>&1
done
%endif

# Do this ONLY at first install
if [ $1 -eq 1 ]
then
  echo 'DAVLockDB /tmp/davlock.db' > /etc/%{apache}/conf.d/dav_mod.conf
fi

# Create inventory repositories and add rights to the apache user to
# access /var/rudder/inventories/incoming
chmod 751 %{ruddervardir}/inventories

for inventorydir in %{ruddervardir}/inventories/incoming %{ruddervardir}/inventories/accepted-nodes-updates
do
  chmod 770 ${inventorydir}
  chown -R root:%{apache_group} ${inventorydir}
done

# Setup password files for inventory reception WebDAV access
for passwdfile in %{rudderdir}/etc/htpasswd-webdav-initial %{rudderdir}/etc/htpasswd-webdav
do
  %{htpasswd_cmd} -bc ${passwdfile} rudder rudder >/dev/null 2>&1
done

echo -n "INFO: Starting Apache HTTPd..."
service %{apache} start >/dev/null 2>&1
echo " Done"

# Do this ONLY at first install
if [ $1 -eq 1 ]
then
  echo ""
  echo "*****************************************************************************************"
  echo "INFO: rudder-server-relay setup complete.                                                "
  echo "INFO:                                                                                    "
  echo "INFO: Now run '/opt/rudder/bin/rudder-node-to-relay $(cat %{rudderdir}/etc/uuid.hive)'   "
  echo "INFO: on your root server to complete this node transition to a relay server.            "
  echo "INFO:                                                                                    "
  echo "INFO: Please look at the documentation for details (Section 'Relay servers')             "
  echo "*****************************************************************************************"
fi

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-server-relay
%defattr(-, root, root, 0755)
%config(noreplace) /etc/%{apache_vhost_dir}/rudder-relay-vhost.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks-24.conf
%{ruddervardir}/inventories/incoming
%{ruddervardir}/inventories/accepted-nodes-updates
%{rudderlogdir}/apache2/

#=================================================
# Changelog
#=================================================
%changelog
* Mon Nov 03 2014 - Matthieu Cerda <matthieu.cerda@normation.com> 3.0-alpha1-1
- Initial package
