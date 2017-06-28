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

%define rudder_user rudder
%define rudder_group rudder

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

# avoid error during byte compilation of pyc since they are removed anyway
%define _python_bytecompile_errors_terminate_build 0


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
Source9: rudder-relay.cron
Source10: rudder-relay.sudo
Source11: rudder-relay.fc
Source12: rudder-relay.te

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Requirements

# Disable dependency auto-generation, to prevent Python requirements
# autodetection, which is not desired here.
AutoReq: 0
AutoProv: 0

## General
BuildRequires: python, python-devel
Requires: rudder-agent >= %{real_epoch}:%{real_version}, rsyslog, openssl, %{apache}, %{apache_tools}, python, binutils, xz

## RHEL
%if 0%{?rhel}
Requires: mod_ssl
%endif

## RHEL & Fedora
%if 0%{?rhel} || 0%{?fedora}
Requires: mod_wsgi shadow-utils crontabs
%endif

## SLES
%if 0%{?suse_version}
Requires: apache2-mod_wsgi pwdutils cron
%endif

%if 0%{?suse_version} && 0%{?suse_version} >= 1200
Requires: python-pyOpenSSL
%endif

## SELinux
%if 0%{?rhel} && 0%{?rhel} == 6
BuildRequires: selinux-policy
%endif

%if 0%{?rhel} && 0%{?rhel} >= 7
BuildRequires: selinux-policy-devel
%endif

%if 0%{?fedora}
BuildRequires: selinux-policy-devel
%endif

%description
Rudder is an open source configuration management and audit solution.

This package is essentially a meta-package to install all components required to
run a Rudder relay server on a machine.

#=================================================
# Source preparation
#=================================================
%prep

%if 0%{?suse_version}
# On SLES, change the Apache DocumentRoot to the OS default
sed -i "s%^DocumentRoot /var/www$%DocumentRoot /srv/www%" %{SOURCE5}
%endif

cp -f %{SOURCE11} %{_builddir}
cp -f %{SOURCE12} %{_builddir}

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
flask/bin/easy_install pip==1.2.1
%else
python virtualenv/virtualenv.py flask
%endif

# Get all requirements via pip
flask/bin/pip install -r requirements.txt

# Clean up unwanted binaries
if [ "%{real_name}" != "" ]; then
  for i in easy_install python pip; do
      rm -f %{real_name}/bin/${i}*
  done
else
  echo "WARNING: Skipping Virtualenv cleanup, as it"
  echo "WARNING: would operate on /bin ..."
  echo "WARNING: Please make sure the real_name macro"
  echo "WARNING: is defined"
fi

%if 0%{?rhel} && 0%{?rhel} >= 6 || 0%{?fedora}
# Build SELinux policy package
# Compiles rudder-relay.te and rudder-relay.fc into rudder-relay.pp
cd %{_builddir} && make -f /usr/share/selinux/devel/Makefile
%endif


#=================================================
# Installation
#=================================================
%install

rm -rf %{buildroot}

# Directories
mkdir -p %{buildroot}/etc/%{apache_vhost_dir}
mkdir -p %{buildroot}%{rudderdir}/bin/
mkdir -p %{buildroot}%{rudderdir}/etc/
mkdir -p %{buildroot}%{rudderdir}/etc/ssl/
mkdir -p %{buildroot}%{rudderdir}/share/selinux/
mkdir -p %{buildroot}%{ruddervardir}/inventories/incoming
mkdir -p %{buildroot}%{ruddervardir}/inventories/accepted-nodes-updates
mkdir -p %{buildroot}%{ruddervardir}/shared-files
mkdir -p %{buildroot}%{rudderlogdir}/apache2/
mkdir -p %{buildroot}/etc/sysconfig/
mkdir -p %{buildroot}/etc/cron.d/
mkdir -p %{buildroot}/etc/sudoers.d/
mkdir -p %{buildroot}%{rudderdir}/share/relay-api/
mkdir -p %{buildroot}%{rudderdir}/share/python/

# relay api
cp -r %{_sourcedir}/relay-api/flask %{buildroot}%{rudderdir}/share/relay-api/
cp -r %{_sourcedir}/relay-api/relay_api %{buildroot}%{rudderdir}/share/relay-api/
cp %{_sourcedir}/relay-api/apache/relay-api.wsgi %{buildroot}%{rudderdir}/share/relay-api/
install -m 755 %{_sourcedir}/relay-api/cleanup.sh %{buildroot}%{rudderdir}/share/relay-api/

# rudder packaging
install -m 755 %{_sourcedir}/rudder-pkg %{buildroot}%{rudderdir}/bin/
cp %{_sourcedir}/docopt.py %{buildroot}%{rudderdir}/share/python/

# Others
install -m 644 %{SOURCE1} %{buildroot}/etc/%{apache_vhost_dir}/rudder.conf
install -m 644 %{SOURCE5} %{buildroot}%{rudderdir}/etc/rudder-apache-relay-common.conf
install -m 644 %{SOURCE6} %{buildroot}/etc/sysconfig/rudder-relay-apache
install -m 644 %{SOURCE9} %{buildroot}/etc/cron.d/rudder-relay
install -m 644 %{SOURCE10} %{buildroot}/etc/sudoers.d/rudder-relay

# Copy stub rudder-networks*.conf
cp %{SOURCE2} %{buildroot}%{rudderdir}/etc/
cp %{SOURCE3} %{buildroot}%{rudderdir}/etc/
cp %{SOURCE7} %{buildroot}%{rudderdir}/etc/
cp %{SOURCE8} %{buildroot}%{rudderdir}/etc/

%if 0%{?rhel} && 0%{?rhel} >= 6 || 0%{?fedora}
# Install SELinux policy
install -m 644  %{_builddir}/rudder-relay.pp %{buildroot}%{rudderdir}/share/selinux/
%endif

%post -n rudder-server-relay
#=================================================
# Post Installation
#=================================================

# Create the rudder group
if ! getent group %{rudder_group} > /dev/null; then
  echo -n "INFO: Creating group %{rudder_group}..."
  groupadd --system %{rudder_group}
  echo " Done"
fi

# Create the rudder user
if ! getent passwd %{rudder_user} >/dev/null; then
  echo -n "INFO: Creating the %{rudder_user} user..."
  useradd -r -m -s /bin/false -g %{rudder_group} -d /var/rudder -c "Rudder,,," %{rudder_user} >/dev/null 2>&1
  echo " Done"
fi

# change some directory to rudder owner
chown rudder: /var/rudder/shared-files
chmod 770 /var/rudder/shared-files

# Include files from /etc/sudoers.d (needed on SLES11)
if ! grep -qE "^#includedir /etc/sudoers.d$" /etc/sudoers; then
  if [[ ${RUDDER_NO_SUDOERS_EDIT} = 1 ]]; then
    echo "WARN: Skipping editing /etc/sudoers. Make sure the sudo rules are in place!"
  else
    echo -e '#includedir /etc/sudoers.d' >> /etc/sudoers
  fi
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
MODULES_TO_ENABLE="rewrite dav dav_fs ssl version wsgi"

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
%endif

# Create inventory repositories and add rights to the apache user to
# access /var/rudder/inventories/incoming
chmod 751 %{ruddervardir}/inventories

for inventorydir in %{ruddervardir}/inventories/incoming %{ruddervardir}/inventories/accepted-nodes-updates
do
  chmod 770 ${inventorydir}
  chown root:%{apache_group} ${inventorydir}
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
  openssl req -new -x509 -newkey rsa:2048 -subj "/C=FR/ST=France/L=Paris/CN=$(hostname --fqdn)/emailAddress=root@$(hostname --fqdn)/" -keyout /opt/rudder/etc/ssl/rudder.key -out /opt/rudder/etc/ssl/rudder.crt -days 1460 -nodes -sha256 >/dev/null 2>&1
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

# Remove old apache config file
rm -f %{rudderdir}/etc/rudder-apache-common.conf

echo -n "INFO: Starting Apache HTTPd..."
%if 0%{?rhel} < 7
service %{apache} start > /dev/null && echo " Done"
%endif
%if 0%{?rhel} >= 7
/bin/systemctl start  %{apache}.service && echo " Done"
%endif

%if 0%{?rhel} && 0%{?rhel} >= 6 || 0%{?fedora}
# SELinux support
# Check "sestatus" presence, and if here tweak our installation to be
# SELinux compliant
if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
  # Remove old webapp policy if exists because it conflicts with rudder-server-relay
  # First version in 4.1 is 1.4
  if semodule -l | egrep -q "rudder-webapp[[:space:]]+1\.[0-3]"; then
    semodule -r rudder-webapp
  fi
  # Add/Update the rudder-relay SELinux policy
  semodule -i /opt/rudder/share/selinux/rudder-relay.pp
  # Ensure inventory directories context is set by resetting
  # their context to the contexts defined in SELinux configuration,
  # including the file contexts defined in the rudder-relay module
  restorecon -R /var/rudder/inventories
  restorecon -R /var/log/rudder/apache2
fi
%endif

# Only output this notice during initial installation
if [ $1 -eq 1 ]; then
  echo "INFO: rudder-server-relay setup complete."
  uuid_file="/opt/rudder/etc/uuid.hive"
  if [ -f "${uuid_file}" ]; then
    uuid=$(cat ${uuid_file})
    if [ "${uuid}" != "root" ]; then
      echo ""
      echo "*****************************************************************************************"
      echo "INFO: Now run on your root server:                                                             "
      echo "INFO:   '/opt/rudder/bin/rudder-node-to-relay ${uuid}"
      echo "INFO: Please look at the documentation for details (Section 'Relay servers')           "
      echo "*******************************************************************i*********************"
    fi
  else # if for some reason there is no uuid here
    echo ""
    echo "*****************************************************************************************"
    echo "INFO: * If you are installing a root server, configuration is automatically done         "
    echo "INFO: * If you are installing a simple relay, run:                                       "
    echo "INFO:   '/opt/rudder/bin/rudder-node-to-relay <your uuid>'          "
    echo "INFO:   on your root server to complete this node transition to a relay server.          "
    echo "INFO:   Please look at the documentation for details (Section 'Relay servers')           "
    echo "*****************************************************************************************"
  fi
fi

%postun -n rudder-server-relay
#=================================================
# Post Uninstallation
#=================================================

%if 0%{?rhel} && 0%{?rhel} >= 6 || 0%{?fedora}
  # Do it only during uninstallation
  if [ $1 -eq 0 ]; then
    if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
      if semodule -l | grep -q rudder-relay; then
        # Remove the rudder-relay SELinux policy
        semodule -r rudder-relay
        restorecon -RF /var/rudder/inventories
        restorecon -RF /var/log/rudder/apache2
        restorecon -RF /opt/rudder/etc/uuid.hive
        restorecon -RF /var/rudder/configuration-repository/techniques
      fi
    fi
  fi
%endif

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
%{rudderdir}/share/selinux/
/etc/%{apache_vhost_dir}/
%config(noreplace) /etc/%{apache_vhost_dir}/rudder.conf
%config(noreplace) %{rudderdir}/etc/rudder-apache-relay-common.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks-24.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks-policy-server.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks-policy-server-24.conf
%config(noreplace) /etc/sysconfig/rudder-relay-apache
%config /etc/cron.d/rudder-relay
%attr(0440, root, root) %config /etc/sudoers.d/rudder-relay
%{ruddervardir}/inventories/incoming
%{ruddervardir}/inventories/accepted-nodes-updates
%{ruddervardir}/shared-files/
%{rudderlogdir}/apache2/
%{rudderdir}/share/relay-api/
%{rudderdir}/share/python/
%{rudderdir}/bin/rudder-pkg

# on sles11, .pyc and .pyo files are not generated, which fails with rpmbuild
# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if ! 0%{?suse_version} || 0%{?suse_version} >= 1200
# Avoid having .pyo and .pyc files in our package
# as they will always be regenerated
%exclude %(find %{rudderdir}/share/ -type f -name '*.pyc')
%exclude %(find %{rudderdir}/share/ -type f -name '*.pyo')
%endif

#=================================================
# Changelog
#=================================================
%changelog
* Mon Nov 03 2014 - Matthieu Cerda <matthieu.cerda@normation.com> 3.0-alpha1-1
- Initial package
