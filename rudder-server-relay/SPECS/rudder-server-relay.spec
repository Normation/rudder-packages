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
%define real_epoch       0

%define rudderdir               /opt/rudder
%define ruddervardir            /var/rudder
%define rudderlogdir            /var/log/rudder

%if 0%{?suse_version}
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
Epoch: %{real_epoch}
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-vhost.conf
Source2: rudder-networks.conf
Source3: rudder-networks-24.conf
Source5: rudder-apache-relay-common.conf
Source6: rudder-relay-apache
Source7: rudder-networks-policy-server.conf
Source8: rudder-networks-policy-server-24.conf

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Requirements

## General
BuildRequires: python, python-devel
Requires: rudder-agent >= %{real_epoch}:%{real_version}, rsyslog, openssl, %{apache}, %{apache_tools}, python

## RHEL
%if 0%{?rhel}
Requires: mod_ssl
%endif

## RHEL & Fedora
%if 0%{?rhel} || 0%{?fedora}
Requires: mod_wsgi shadow-utils
%endif

## SLES
%if 0%{?suse_version}
Requires: apache2-mod_wsgi pwdutils
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

# Build Virtualenv
cd %{_sourcedir}/relay-api

# Build Virtualenv
%if 0%{?suse_version} && 0%{?suse_version} < 1200
# SLES specific exception, see http://www.rudder-project.org/redmine/issues/6365
python virtualenv-1.10.1/virtualenv.py flask

# Using a recent pip on SLES is not possible due to
# bad interaction between pip and an old OpenSSL.
# See http://stackoverflow.com/questions/17416938/pip-can-not-install-anything
%{real_name}/bin/easy_install pip==1.2.1
%else
python virtualenv/virtualenv.py flask
%endif

# Get all requirements via pip
flask/bin/pip install -r requirements.txt

# Clean up unwanted binaries
if [ "z%{real_name}" != "" ]; then
  for i in easy_install python pip; do
      rm -f %{real_name}/bin/${i}*
  done
else
  echo "WARNING: Skipping Virtualenv cleanup, as it"
  echo "WARNING: would operate on /bin ..."
  echo "WARNING: Please make sure the real_name macro"
  echo "WARNING: is defined"
fi

#=================================================
# Installation
#=================================================
%install

rm -rf %{buildroot}

# Directories
mkdir -p %{buildroot}/etc/%{apache_vhost_dir}
mkdir -p %{buildroot}%{rudderdir}/etc/
mkdir -p %{buildroot}%{rudderdir}/etc/ssl/
mkdir -p %{buildroot}%{ruddervardir}/inventories/incoming
mkdir -p %{buildroot}%{ruddervardir}/inventories/accepted-nodes-updates
mkdir -p %{buildroot}%{rudderlogdir}/apache2/
mkdir -p %{buildroot}/etc/sysconfig/
mkdir -p %{buildroot}%{rudderdir}/share/relay-api/

# relay api
cp -r %{_sourcedir}/relay-api/flask %{buildroot}%{rudderdir}/share/relay-api/
cp -r %{_sourcedir}/relay-api/relay_api %{buildroot}%{rudderdir}/share/relay-api/
cp %{_sourcedir}/relay-api/apache/relay-api.wsgi %{buildroot}%{rudderdir}/share/relay-api/
install -m 644 %{_sourcedir}/relay-api/apache/relay-api.conf %{buildroot}/etc/%{apache_vhost_dir}/relay-api.conf

# Others
install -m 644 %{SOURCE1} %{buildroot}/etc/%{apache_vhost_dir}/rudder.conf
install -m 644 %{SOURCE5} %{buildroot}%{rudderdir}/etc/rudder-apache-relay-common.conf
install -m 644 %{SOURCE6} %{buildroot}/etc/sysconfig/rudder-relay-apache

# Copy stub rudder-networks*.conf
cp %{SOURCE2} %{buildroot}%{rudderdir}/etc/
cp %{SOURCE3} %{buildroot}%{rudderdir}/etc/
cp %{SOURCE7} %{buildroot}%{rudderdir}/etc/
cp %{SOURCE8} %{buildroot}%{rudderdir}/etc/

%post -n rudder-server-relay
#=================================================
# Post Installation
#=================================================

# Create the rudder user
if ! getent passwd rudder >/dev/null; then
  echo -n "INFO: Creating the rudder user..."
  useradd -r -m -d /var/rudder -c "Rudder,,," rudder >/dev/null 2>&1
  echo " Done"
fi

echo -n "INFO: Setting Apache HTTPd as a boot service..."
chkconfig --add %{apache} 2&> /dev/null
%if 0%{?rhel} && 0%{?rhel} >= 6
chkconfig %{apache} on
%endif
echo " Done"

echo -n "INFO: Stopping Apache HTTPd..."
%if 0%{?rhel} < 7
service %{apache} stop > /dev/null && echo " Done"
%endif
%if 0%{?rhel} >= 7
/bin/systemctl stop %{apache}.service && echo " Done"
%endif

%if 0%{?suse_version}
# On SuSE, enable the required modules
MODULES_TO_ENABLE="dav dav_fs ssl version wsgi"

for enmod in ${MODULES_TO_ENABLE}
do
  a2enmod ${enmod} >/dev/null 2>&1
done
%endif

# Do this ONLY at first install
if [ $1 -eq 1 ];  then
  echo 'DAVLockDB /tmp/davlock.db' > /etc/%{apache}/conf.d/dav_mod.conf
fi

%if 0%{?suse_version}
# Add required includes in the apache2 configuration
if ! grep -qE "^. /etc/sysconfig/rudder-relay-apache$" /etc/sysconfig/apache2; then
  echo -e '# This sources the modules/defines needed by Rudder\n. /etc/sysconfig/rudder-relay-apache' >> /etc/sysconfig/apache2
fi

# Remove old includes in the SLES apache2 configuration
if [ -f /etc/sysconfig/apache2 ]; then
  if grep -qE "^. /etc/sysconfig/rudder-apache$" /etc/sysconfig/apache2; then
    sed -i "/. \/etc\/sysconfig\/rudder-apache/d" /etc/sysconfig/apache2
  fi
fi

# On SLES, change the Apache DocumentRoot to the OS default
sed -i "s%^DocumentRoot /var/www$%DocumentRoot /srv/www%" %{buildroot}%{rudderdir}/etc/rudder-apache-relay-common.conf
%endif

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

# Migrate existing certificates
if [ ! -f /opt/rudder/etc/ssl/rudder.crt ] || [ ! -f /opt/rudder/etc/ssl/rudder.key ]; then
  for source in relay webapp; do
    if [ -f /opt/rudder/etc/ssl/rudder-${source}.crt ] && [ -f /opt/rudder/etc/ssl/rudder-${source}.key ]; then
      echo -n "INFO: Importing existing ${source} certificates..."
      mv /opt/rudder/etc/ssl/rudder-${source}.crt /opt/rudder/etc/ssl/rudder.crt
      mv /opt/rudder/etc/ssl/rudder-${source}.key /opt/rudder/etc/ssl/rudder.key
      echo " Done"
    fi
  done
fi

# Generate certificates if needed
if [ ! -f /opt/rudder/etc/ssl/rudder.crt ] || [ ! -f /opt/rudder/etc/ssl/rudder.key ]; then
  echo -n "INFO: No usable SSL certificate detected for Rudder HTTP/S support, generating one automatically..."
  openssl req -new -x509 -newkey rsa:2048 -subj "/CN=$(hostname --fqdn)/" -keyout /opt/rudder/etc/ssl/rudder.key -out /opt/rudder/etc/ssl/rudder.crt -days 1460 -nodes -sha256 >/dev/null 2>&1
  chgrp %{apache_group} /opt/rudder/etc/ssl/rudder.key && chmod 640 /opt/rudder/etc/ssl/rudder.key
  echo " Done"
fi

# Move old virtual hosts out of the way
for OLD_VHOST in rudder-default rudder-default-ssl rudder-default.conf rudder-default-ssl.conf rudder-vhost.conf rudder-vhost-ssl.conf rudder-relay-vhost.conf rudder-relay-vhost-ssl.conf; do
	if [ -f /etc/%{apache_vhost_dir}/${OLD_VHOST} ]; then
		echo -n "INFO: An old rudder virtual host file has been detected (${OLD_VHOST}), it will be moved to /var/backups."
		mkdir -p /var/backups
		mv /etc/%{apache_vhost_dir}/${OLD_VHOST} /var/backups/${OLD_VHOST}-$(date +%s)
		echo " Done"
	fi
done

echo -n "INFO: Starting Apache HTTPd..."
%if 0%{?rhel} < 7
service %{apache} start > /dev/null && echo " Done"
%endif
%if 0%{?rhel} >= 7
/bin/systemctl start  %{apache}.service && echo " Done"
%endif

# Do this ONLY at first install
if [ $1 -eq 1 ]
then
  echo ""
  echo "*****************************************************************************************"
  echo "INFO: rudder-server-relay setup complete.                                                "
  echo "INFO:                                                                                    "
  echo "INFO: * If you are installing a root server, configuration is automatically done         "
  echo "INFO: * If you are installing a simple relay, run:                                       "
  echo "INFO:   '/opt/rudder/bin/rudder-node-to-relay $(cat /opt/rudder/etc/uuid.hive)'          "
  echo "INFO:   on your root server to complete this node transition to a relay server.          "
  echo "INFO:   Please look at the documentation for details (Section 'Relay servers')           "
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
%{rudderdir}/etc/
/etc/%{apache_vhost_dir}/
%config(noreplace) /etc/%{apache_vhost_dir}/rudder.conf
%config(noreplace) %{rudderdir}/etc/rudder-apache-relay-common.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks-24.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks-policy-server.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks-policy-server-24.conf
%config(noreplace) /etc/sysconfig/rudder-relay-apache
%{ruddervardir}/inventories/incoming
%{ruddervardir}/inventories/accepted-nodes-updates
%{rudderlogdir}/apache2/
%{rudderdir}/share/relay-api/

# on sles11, .pyc and .pyo files are not generated, which fails with rpmbuild
# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if ! 0%{?suse_version} || 0%{?suse_version} >= 1200
# Avoid having .pyo and .pyc files in our package
# as they will always be regenerated
%exclude %(find %{rudderdir}/share/relay-api/ -type f -name '*.pyc')
%exclude %(find %{rudderdir}/share/relay-api/ -type f -name '*.pyo')
%endif

#=================================================
# Changelog
#=================================================
%changelog
* Mon Nov 03 2014 - Matthieu Cerda <matthieu.cerda@normation.com> 3.0-alpha1-1
- Initial package
