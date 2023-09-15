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
# Specification file for rudder-server
#
# Installs a Rudder server
#
# Copyright (C) 2011- Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-server
%define old_epoch       1398866025

%define maven_settings settings-external.xml

%define apache_conf_dir         %{apache}/conf.d

# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version}
%define apache                  apache2
%define apache_tools            apache2-utils
%define htpasswd_cmd            htpasswd2
%define ldap_clients            openldap2-client
%define jetty_init_script       jetty-sles.sh
%define apache_vhost_dir        %{apache}/vhosts.d
%endif
%if 0%{?rhel} || 0%{?fedora}
%define apache                  httpd
%define apache_tools            httpd-tools
%define htpasswd_cmd            htpasswd
%define ldap_clients            openldap-clients
%define jetty_init_script       jetty-rpm.sh
%define apache_vhost_dir        %{apache}/conf.d
%endif

# avoid error during byte compilation of pyc since they are removed anyway
%define _python_bytecompile_errors_terminate_build 0

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - server package
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 0
License: GPLv3
URL: https://www.rudder.io/

Group: Applications/System

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

AutoReq: 0
AutoProv: 0

Obsoletes: rudder-server-root < 7.2
Obsoletes: rudder-webapp < 7.2
Obsoletes: rudder-reports < 7.2

Requires: %(../format-dependencies rpm %{old_epoch}:%{real_version} rudder-agent)
Requires: %(../format-dependencies rpm %{real_version} rudder-relay)
Requires: %{apache}, %{apache_tools}, git-core, iproute, rsync, openssl, %{ldap_clients}, curl, acl, rudder-api-client, zip

# yum doesn't support installing a preferred package in a A or B situation
# rudder-external-db will not prevent installation of postgresql-server on rhel/sles
# amazon linux doesn't provide posrgresql-server, it provides postgresql15-server instead
%if 0%{?amazon}
Requires: postgresql15-server
%else
Requires: postgresql-server >= 13
%endif

BuildRequires: gcc, rsync

# OS-specific dependencies

## RHEL
%if 0%{?rhel} || 0%{?fedora}
BuildRequires: groff-base
BuildRequires: selinux-policy-devel
Requires: mod_ssl httpd shadow-utils
Requires: jre-17-headless
Requires: perl-Digest-SHA libtool-ltdl
BuildRequires: openssl-devel libtool-ltdl-devel git
%endif

## SLES
%if 0%{?suse_version}
BuildRequires: groff
Requires: apache2 pwdutils libltdl7
BuildRequires: libopenssl-devel git-core
%endif

%if 0%{?sle_version} && 0%{?sle_version} >= 150000
Requires: java-17-openjdk-headless 
%endif

## Python 3
BuildRequires: python3
Requires: python3

%description
Rudder is an open source configuration management and audit solution.

This package install all components required to run a Rudder root server on a machine,
including the web interface and its dependencies.

#=================================================
# Source preparation
#=================================================
%prep

cd %{_sourcedir}
make --debug rudder-sources

#=================================================
# Building
#=================================================
%build

# Ensure an appropriate environment for the compiler
export CFLAGS="$RPM_OPT_FLAGS"

cd %{_sourcedir}
make --debug build

%if 0%{?rhel} || 0%{?fedora}
# Build SELinux policy package
# Compiles rudder-webapp.te and rudder-webapp.fc into rudder-webapp.pp
make -f /usr/share/selinux/devel/Makefile
%endif


#=================================================
# Installation
#=================================================
%install

rm -rf %{buildroot}
cd %{_sourcedir}
make --debug install APACHE_VHOSTDIR=%{apache_vhost_dir} DESTDIR=%{buildroot} JETTY_SCRIPT=%{jetty_init_script} APACHE_CONFDIR=%{apache_conf_dir}

%if 0%{?rhel} || 0%{?fedora}
  # Install SELinux policy
  install -m 644  rudder-webapp.pp %{buildroot}/opt/rudder/share/selinux/
  # Replace init script
  cp jetty/bin/jetty-rpm.sh jetty/bin/jetty.sh
%else
  # Replace init script
  cp jetty/bin/jetty-sles.sh jetty/bin/jetty.sh
%endif

#=================================================
# pretrans is run before all preinst when installing more than one package
#=================================================
%pretrans

set -e

# We need to be sure that uuid.hive is set to root at beginning
mkdir -p /opt/rudder/etc
echo 'root' > /opt/rudder/etc/uuid.hive

mkdir -p /var/rudder/cfengine-community/
echo "127.0.0.1" > /var/rudder/cfengine-community/policy_server.dat

#=================================================
# Pre Installation
#=================================================
%pre

set -e

CFRUDDER_FIRST_INSTALL=$1
LOG_FILE="/var/log/rudder/install/%{name}.log"

echo "`date` - Starting %{name} pre installation script" >> ${LOG_FILE}

# Only do this on package upgrade
if [ $1 -ne 1 ]
  then
  # When upgrading OpenLDAP, we may need to dump the database
  # so that it can be restored from LDIF
  TIMESTAMP=`date +%%Y%%m%%d%%H%%M%%S`
  # Ensure backup folder exist
  mkdir -p /var/rudder/ldap/backup/

  # We need it to be able to open big mdb memory-mapped databases
  ulimit -v unlimited

  [ -x /opt/rudder/sbin/slapcat ] && /opt/rudder/sbin/slapcat -b "cn=rudder-configuration" -l /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.ldif

  # If the stops fails, it's probably because it was not started
  systemctl stop rudder-jetty >&2 > /dev/null || true

  if [ -x /opt/rudder/bin/rudder-pkg ]
  then
    /opt/rudder/bin/rudder-pkg plugin save-status > /tmp/rudder-plugins-upgrade
  else
    rudder package plugin save-status > /tmp/rudder-plugins-upgrade
  fi

  getfacl --absolute-names --recursive /opt/rudder/etc/hooks.d/ > /tmp/rudder-hooks-upgrade

  # Backup in case there was custom changes when it was a conffile
  # not used anymore
  if [ -f /opt/rudder/etc/rudder-apache-webapp-common.conf ]; then
    cp /opt/rudder/etc/rudder-apache-webapp-common.conf "${BACKUP_DIR}/rudder-apache-webapp-common-`date +%Y%m%d`.conf"
    cp /opt/rudder/etc/rudder-apache-webapp-ssl.conf "${BACKUP_DIR}/rudder-apache-webapp-ssl-`date +%Y%m%d`.conf"
    cp /opt/rudder/etc/rudder-apache-webapp-nossl.conf "${BACKUP_DIR}/rudder-apache-webapp-nossl-`date +%Y%m%d`.conf"
  fi
else
  # make sure keys and certificate are the server ones
  [ -x /opt/rudder/bin/rudder ] && /opt/rudder/bin/rudder agent check -f -s keys
fi


#=================================================
# Post Installation
#=================================================
%post

set -e

RUDDER_FIRST_INSTALL="false"
%if 0%{?rhel} || 0%{?fedora}
# rhel does'nt initialize postgresql
DB_NOT_INITIALIZED="true"
%else
DB_NOT_INITIALIZED="false"
%endif

# Do this ONLY at first install
if [ $1 -eq 1 ]
then
  RUDDER_FIRST_INSTALL="true"
  echo 'DAVLockDB /tmp/davlock.db' > /etc/%{apache}/conf.d/dav_mod.conf
fi

%if 0%{?suse_version}
a2enmod rewrite dav dav_fs ssl version

# Add required includes in the apache2 configuration
nextline=$(grep -A1 -E "^. /etc/sysconfig/rudder-webapp-apache$" /etc/sysconfig/apache2 | tail -n1)
if [ "${nextline}" = "" ]; then
  # No include currently
  echo -e '# This sources the modules/defines needed by Rudder\n. /etc/sysconfig/rudder-webapp-apache' >> /etc/sysconfig/apache2
  echo -e '# This line is necessary for fillup not to remove any lines above. See #11153\nAPACHE_RUDDER_RELAY_CUSTOMIZED="true"' >> /etc/sysconfig/apache2
fi
%endif


# Update /etc/sysconfig/apache2 in case an old module loading entry has already been created by Rudder
if [ -f /etc/sysconfig/apache2 ] && grep -q 'APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http' /etc/sysconfig/apache2
then
  echo "INFO: Upgrading the /etc/sysconfig/apache2 file, Rudder needed modules for Apache are now listed in /etc/sysconfig/rudder-webapp-apache"
  sed -i 's|APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http.*|# This sources the Rudder needed by Rudder\n. /etc/sysconfig/rudder-webapp-apache|' /etc/sysconfig/apache2
fi

if ! /opt/rudder/share/package-scripts/rudder-server-postinst "${RUDDER_FIRST_INSTALL}" "%{apache}" "${DB_NOT_INITIALIZED}"; then
  echo "**************************************************************************************"
  echo "ERROR: rudder-server postinstall script failed !"
  echo ""
  echo "Trying to recover the problem, you should check that your instance is properly working"
  echo ""
  echo "You should also try to manually execute: /opt/rudder/bin/rudder-upgrade"
  echo ""
  echo "   Such errors should not happen, please open an issue for this problem on "
  echo "            https://issues.rudder.io/projects/rudder/issues/new"
  echo "**************************************************************************************"
  LOG_FILE="/var/log/rudder/install/rudder-webapp-fail-$(date +%%Y%%m%%d%%H%%M%%S).log"
  /opt/rudder/bin/rudder-fix-repository-permissions  >> ${LOG_FILE}
fi

%if 0%{?rhel} || 0%{?fedora}
# SELinux support
# Check "sestatus" presence, and if here tweak our installation to be
# SELinux compliant
if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
  # Add/Update the rudder-webapp SELinux policy
  semodule -i /opt/rudder/share/selinux/rudder-webapp.pp
  # Ensure inventory directories context is set by resetting
  # their context to the contexts defined in SELinux configuration,
  # including the file contexts defined in the rudder-webapp module
  restorecon -RF /var/rudder/configuration-repository/techniques
fi
%endif

#=================================================
# Pre Un-installation
#=================================================
%preun

set -e

if [[ $1 -eq 0 ]]
then
  systemctl stop rudder-jetty
  systemctl stop rudder-slapd
fi


#=================================================
# Post Uninstallation
#=================================================
%postun

set -e

# Do it only during uninstallation
if [ $1 -eq 0 ]; then

  # Clean up all logrotate leftovers
  rm -rf %{_sysconfdir}/logrotate.d/rudder*
  # Clean up all syslog leftovers
  rm -rf %{_sysconfdir}/rsyslog.d/rudder*

%if 0%{?suse_version}
  # Remove required includes in the SLES apache2 configuration
  if [ -f /etc/sysconfig/apache2 ]; then
    sed -i "/# This sources the modules\/defines needed by Rudder/d" /etc/sysconfig/apache2
    sed -i "/. \/etc\/sysconfig\/rudder-webapp-apache/d" /etc/sysconfig/apache2

    # Also remove an older comment that was erroneously added until 2.11.21 / 3.0.16 / 3.1.10 / 3.2.3
    sed -i "/# This sources the configuration file needed by Rudder/d" /etc/sysconfig/apache2
  fi
%endif

%if 0%{?rhel} || 0%{?fedora}
  if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
    if semodule -l | grep -q rudder-webapp; then
      # Remove the rudder-webapp SELinux policy
      semodule -r rudder-webapp
      restorecon -RF /var/rudder/configuration-repository/techniques
    fi
  fi
%endif

  if getent passwd rudder-slapd >/dev/null; then
    userdel rudder-slapd >/dev/null 2>&1
  fi

fi

#=================================================
# Post transaction
#=================================================
%posttrans

set -e

# during upgrade, service may have been stopped by uninstall of rudder-inventory-ldap or rudder-jetty
# 7.2 should not happen anymore
systemctl start rudder-slapd >/dev/null
systemctl start rudder-jetty >/dev/null

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files
%defattr(-, root, root, 0755)
/opt/rudder/share/package-scripts/rudder-server-postinst
/usr/lib/systemd/system/rudder-server.service
/opt/rudder/share/versions/rudder-server-version
/opt/rudder/etc/postgresql/reportsSchema.sql
/opt/rudder/share/package-scripts/
%config(noreplace) /opt/rudder/etc/openldap/slapd.conf
%config(noreplace) /opt/rudder/etc/rudder-web.properties
%config(noreplace) /opt/rudder/etc/rudder-users.xml
%config(noreplace) /opt/rudder/etc/logback.xml
%config(noreplace) /opt/rudder/etc/rudder-passwords.conf
%config(noreplace) /etc/default/rudder-jetty
%attr(0600, root, root) /opt/rudder/etc/rudder-passwords.conf
/usr/lib/systemd/system/
/opt/rudder/jetty
/opt/rudder/etc
/opt/rudder/bin
/opt/rudder/sbin
/opt/rudder/share
/opt/rudder/share
/opt/rudder/include
/opt/rudder/lib
/opt/rudder/var
/opt/rudder/libexec
/var/rudder/ldap/openldap-data
/var/rudder/run
/var/rudder/inventories/received
/var/log/rudder/ldap
/var/log/rudder/apache2/
/var/log/rudder/webapp/
/etc/%{apache_vhost_dir}/
/opt/rudder/etc/rudder-apache-webapp-common.conf
/opt/rudder/etc/rudder-apache-webapp-ssl.conf
/opt/rudder/etc/rudder-apache-webapp-nossl.conf
%config(noreplace) /etc/sysconfig/rudder-webapp-apache
/usr/share/doc/rudder
/usr/share/ncf/

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <dev@rudder.io> %{version}
- See https://docs.rudder.io/changelogs/current/index.html for changelogs

