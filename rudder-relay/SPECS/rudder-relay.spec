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

# Disable totally debug info package
%define debug_package %{nil}

%define real_name               rudder-relay
%define old_epoch              1398866025

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
Epoch: 0
License: GPLv3
URL: https://www.rudder.io
Source: rudder-sources.tar.bz2

Group: Applications/System

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Requirements

AutoReq: 0
AutoProv: 0

Obsoletes: rudder-server-relay < 7.2

## General
BuildRequires: pkgconfig, postgresql-devel
Requires: %(../format-dependencies rpm %{old_epoch}:%{real_version} rudder-agent), %{apache}, %{apache_tools}, binutils, xz, postgresql, rsync, sudo

## RHEL
%if 0%{?rhel}
Requires: mod_ssl shadow-utils apr-util-bdb
BuildRequires: selinux-policy-devel
%endif

%if 0%{?rhel} && 0%{?rhel} > 7
Requires: python3-policycoreutils policycoreutils-python-utils
%endif
%if 0%{?rhel} && 0%{?rhel} <= 7
Requires: policycoreutils-python
%endif

%if 0%{?rhel} && 0%{?rhel} >= 9
Requires: libpq
%endif

## SLES
%if 0%{?suse_version}
Requires: pwdutils
%endif

# Doc for suse versioning https://en.opensuse.org/openSUSE:Packaging_for_Leap
%if 0%{?suse_version} && 0%{?suse_version} < 1500
BuildRequires: python
Requires: python, python-pyOpenSSL
%endif
%if 0%{?suse_version} && 0%{?suse_version} >= 1500
BuildRequires: python3
Requires: python3
%endif


## Python
%if 0%{?rhel} == 7 || ( 0%{?suse_version} && 0%{?suse_version} < 1500 )
BuildRequires: python, python-setuptools, python-lxml, python-requests
Requires: python, python-setuptools, python-lxml, python-requests
%else
BuildRequires: python3, python3-pip, python3-lxml, python3-requests
Requires: python3, python3-lxml, python3-requests, python3-setuptools
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

# rhel7 doesn't have python 3 so we force python2 instead
%if 0%{?rhel} == 7 || ( 0%{?suse_version} && 0%{?suse_version} < 1500 )
find . -type f | xargs sed -i '1,1s|#!/usr/bin/python3|#!/usr/bin/python2|'
%endif

#=================================================
# Building
#=================================================
%build
cd rudder-sources-*/rudder/relay/sources/

%if 0%{?suse_version}
# On SLES, change the Apache DocumentRoot to the OS default
sed -i "s|^DocumentRoot /var/www$|DocumentRoot /srv/www|" apache/rudder-apache-relay-common.conf
%endif

%if 0%{?rhel} == 7
make --debug build SELINUX=%{selinux} PYTHON=python2
%else
make --debug build SELINUX=%{selinux}
%endif

#=================================================
# Installation
#=================================================
%install
cd rudder-sources-*/rudder/relay/sources/

# TODO remove
rm -rf %{buildroot}

make --debug install APACHE_VHOSTDIR=%{apache_vhost_dir} DESTDIR=%{buildroot} SELINUX=%{selinux}

#=================================================
# Post Installation
#=================================================
%post -n rudder-relay

set -e

CFRUDDER_FIRST_INSTALL=$1

%if 0%{?rhel}
systemctl enable %{apache} >/dev/null 2>&1
%endif

%if 0%{?suse_version}
a2enmod rewrite dav dav_fs ssl version proxy proxy_http

# Add required includes in the apache2 configuration
nextline=$(grep -A1 -E "^. /etc/sysconfig/rudder-relay-apache$" /etc/sysconfig/apache2 | tail -n1)
if [ "${nextline}" = "" ]; then
  # No include currently
  echo -e '# This sources the modules/defines needed by Rudder\n. /etc/sysconfig/rudder-relay-apache' >> /etc/sysconfig/apache2
  echo -e '# This line is necessary for fillup not to remove any lines above. See #11153\nAPACHE_RUDDER_RELAY_CUSTOMIZED="true"' >> /etc/sysconfig/apache2
fi
%endif

if [ $CFRUDDER_FIRST_INSTALL -eq 1 ];  then
  echo 'DAVLockDB /tmp/davlock.db' > /etc/%{apache}/conf.d/dav_mod.conf
fi

/opt/rudder/share/package-scripts/rudder-relay-postinst "${CFRUDDER_FIRST_INSTALL}" "%{apache}" "%{apache_user}" "%{apache_group}" "%{apache_vhost_dir}" "%{selinux}"

%preun
#=================================================
# Pre Uninstallation
#=================================================
# Do it during upgrade and uninstall
set -e

/opt/rudder/share/package-scripts/rudder-relay-prerm

#=================================================
# Post Uninstallation
#=================================================
%postun -n rudder-relay

set -e

# Do it only during uninstallation
# common to all distro but cannot be done in a commond script since its is *post*rm
if [ $1 -eq 0 ]; then
  # Restart apache since it is still using this user
  systemctl restart %{apache} >/dev/null
  # remove users before groups
  if getent passwd rudder >/dev/null; then
    userdel rudder >/dev/null 2>&1
  fi
  if getent passwd rudder-relayd >/dev/null; then
    userdel rudder-relayd >/dev/null 2>&1
  fi
  if getent group rudder >/dev/null; then
    groupdel rudder >/dev/null 2>&1
  fi
   if getent group rudder-policy-reader >/dev/null; then
    groupdel rudder-policy-reader >/dev/null 2>&1
  fi
fi

%if 0%{?rhel}
  # Do it only during uninstallation
  if [ $1 -eq 0 ]; then
    if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
      if semodule -l | grep -q rudder-relay; then
        # Remove the rudder-relay SELinux policy
        semodule -r rudder-relay
        restorecon -RF /var/rudder
        restorecon -RF /var/log/rudder/apache2
        restorecon -RF /opt/rudder/etc/uuid.hive
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
%files -n rudder-relay
%defattr(-, root, root, 0755)
/etc/%{apache_vhost_dir}/
%config(noreplace) /etc/%{apache_vhost_dir}/rudder.conf
%config(noreplace) /opt/rudder/etc/rudder-networks-24.conf
%config(noreplace) /opt/rudder/etc/rudder-networks-policy-server-24.conf
%config(noreplace) /opt/rudder/etc/rudder-pkg/rudder-pkg.conf
%config(noreplace) /opt/rudder/etc/relayd/main.conf
%config(noreplace) /opt/rudder/etc/relayd/logging.conf
# only used on SLES
%config(noreplace) /etc/sysconfig/rudder-relay-apache
%attr(0440, root, root) %config /etc/sudoers.d/rudder-relay
%attr(700, root, root) /opt/rudder/etc/rudder-pkg/
/var/rudder/inventories/incoming
/var/rudder/inventories/failed
/var/rudder/inventories/accepted-nodes-updates
/var/rudder/reports/incoming
/var/rudder/reports/failed
/var/rudder/shared-files/
/var/rudder/share/
/var/rudder/lib/ssl/
/var/rudder/lib/relay/
/var/log/rudder/apache2/
/usr/lib/systemd/system/rudder-relayd.service
/opt/rudder/bin/rudder-relayd
/opt/rudder/bin/rudder-pkg
/opt/rudder/etc/rudder-pkg/rudder_plugins_key.pub
/opt/rudder/etc/rudder-apache-relay-nossl.conf
/opt/rudder/etc/rudder-pkg/rudder_plugins_key.pub
/opt/rudder/etc/rudder-apache-relay-common.conf
/opt/rudder/etc/rudder-apache-relay-ssl.conf
/opt/rudder/etc/ssl/openssl.cnf
/opt/rudder/share/commands/package
/opt/rudder/share/man/man1/rudder-relayd.1.gz
/opt/rudder/share/selinux/
/opt/rudder/share/package-scripts/rudder-relay-postinst
/opt/rudder/share/package-scripts/rudder-relay-prerm
/opt/rudder/share/python/
/etc/bash_completion.d/rudder-pkg.sh

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
