#####################################################################################
# Copyright 2011-2019 Normation SAS
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

%define real_name               rudder-server-relay
%define real_epoch              1398866025

%if 0%{?suse_version}
%define apache                  apache2
%define apache_tools            apache2-utils
%define apache_group            www
%define apache_user             wwwrun
%define apache_vhost_dir        %{apache}/vhosts.d
%define selinux                 false
%endif
%if 0%{?rhel}
%define apache                  httpd
%define apache_tools            httpd-tools
%define apache_group            apache
%define apache_user             apache
%define apache_vhost_dir        %{apache}/conf.d
%define selinux                 true
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
URL: https://www.rudder.io
Source: rudder-sources.tar.bz2

Group: Applications/System

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
Requires: mod_ssl mod_wsgi shadow-utils crontabs
BuildRequires: selinux-policy-devel

%endif

## SLES
%if 0%{?suse_version}
Requires: apache2-mod_wsgi pwdutils cron python-pyOpenSSL
%endif

%description
Rudder is an open source configuration management and audit solution.

This package is essentially a meta-package to install all components required to
run a Rudder relay server on a machine.

#=================================================
# Source preparation
#=================================================
%prep
%setup -c

# We don't know the exact version
cd rudder-sources-*/rudder/relay/sources/

#=================================================
# Building
#=================================================
%build
cd rudder-sources-*/rudder/relay/sources/

%if 0%{?suse_version}
# On SLES, change the Apache DocumentRoot to the OS default
sed -i "s%^DocumentRoot /var/www$%DocumentRoot /srv/www%" rudder-apache-relay-common.conf
%endif

make build SELINUX=%{selinux}

#=================================================
# Installation
#=================================================
%install
cd rudder-sources-*/rudder/relay/sources/

# TODO remove
rm -rf %{buildroot}

make install APACHE_VHOSTDIR=%{apache_vhost_dir} DESTDIR=%{buildroot} SELINUX=%{selinux}

mkdir -p %{buildroot}/etc/sysconfig/
install -m 644 rudder-relay-apache %{buildroot}/etc/sysconfig/rudder-relay-apache

#=================================================
# Post Installation
#=================================================
%post -n rudder-server-relay

FIRST_INSTALL=$1

%if 0%{?rhel}
  echo -n "INFO: Setting Apache HTTPd as a boot service..."
  systemctl enable %{apache} >/dev/null
  echo " Done"
%endif

%if 0%{?suse_version}
a2enmod rewrite dav dav_fs ssl version wsgi

# Add required includes in the apache2 configuration
nextline=$(grep -A1 -E "^. /etc/sysconfig/rudder-relay-apache$" /etc/sysconfig/apache2 | tail -n1)
if [ "${nextline}" = "" ]; then
  # No include currently
  echo -e '# This sources the modules/defines needed by Rudder\n. /etc/sysconfig/rudder-relay-apache' >> /etc/sysconfig/apache2
  echo -e '# This line is necessary for fillup not to remove any lines above. See #11153\nAPACHE_RUDDER_RELAY_CUSTOMIZED="true"' >> /etc/sysconfig/apache2
fi
%endif

%if 0%{?rhel}
# SELinux support
# Check "sestatus" presence, and if here tweak our installation to be
# SELinux compliant
if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
  # Add/Update the rudder-relay SELinux policy
  semodule -i /opt/rudder/share/selinux/rudder-relay.pp
  # Ensure inventory directories context is set by resetting
  # their context to the contexts defined in SELinux configuration,
  # including the file contexts defined in the rudder-relay module
  restorecon -R /var/rudder/inventories
  restorecon -R /var/log/rudder/apache2
fi
%endif

if [ $FIRST_INSTALL -eq 1 ];  then
  echo 'DAVLockDB /tmp/davlock.db' > /etc/%{apache}/conf.d/dav_mod.conf
fi

/opt/rudder/share/package-scripts/rudder-server-relay-postinst "${FIRST_INSTALL}" "%{apache}" "%{apache_user}" "%{apache_group}"

#=================================================
# Post Uninstallation
#=================================================
%postun -n rudder-server-relay

# Do it only during uninstallation
if [ $1 -eq 0 ]; then
  # Restart apache since it is still using this user
  systemctl restart %{apache} >/dev/null
  # Remove package user and groups
  if getent group rudder >/dev/null; then
    echo -n "INFO: Removing the rudder group ..."
    groupdel rudder >/dev/null 2>&1
    echo " Done"
  fi
   if getent group rudder-policy-reader >/dev/null; then
    echo -n "INFO: Removing the rudder-policy-reader group ..."
    groupdel rudder-policy-reader >/dev/null 2>&1
    echo " Done"
  fi
  if getent passwd rudder >/dev/null; then
    echo -n "INFO: Removing the rudder user..."
    userdel rudder >/dev/null 2>&1
    echo " Done"
  fi
fi

%if 0%{?rhel}
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
/etc/%{apache_vhost_dir}/
%config(noreplace) /etc/%{apache_vhost_dir}/rudder.conf
%config(noreplace) /opt/rudder/etc/rudder-apache-relay-common.conf
%config(noreplace) /opt/rudder/etc/rudder-apache-relay-ssl.conf
%config(noreplace) /opt/rudder/etc/rudder-networks-24.conf
%config(noreplace) /opt/rudder/etc/rudder-networks-policy-server-24.conf
%config(noreplace) /etc/sysconfig/rudder-relay-apache
%config /etc/cron.d/rudder-relay
%attr(0440, root, root) %config /etc/sudoers.d/rudder-relay
/var/rudder/inventories/incoming
/var/rudder/inventories/accepted-nodes-updates
/var/rudder/shared-files/
/var/rudder/share/
/var/log/rudder/apache2/
/opt/rudder/etc/
/opt/rudder/share/selinux/
/opt/rudder/share/relay-api/
/opt/rudder/share/python/
/opt/rudder/bin/rudder-pkg
/opt/rudder/share/package-scripts/rudder-server-relay-postinst

# Avoid having .pyo and .pyc files in our package
# as they will always be regenerated
%exclude %(find /opt/rudder/share/ -type f -name '*.pyc')
%exclude %(find /opt/rudder/share/ -type f -name '*.pyo')

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <dev@rudder.io> %{version}
- See https://docs.rudder.io/changelogs/current/index.html for changelogs
