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
# Variables
#=================================================
%define real_name               rudder-webapp
%define real_epoch              1398866025

%define config_repository_group rudder

%define maven_settings settings-external.xml

# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version}
%define apache                  apache2
%define apache_tools            apache2-utils
%define apache_group            www
%define htpasswd_cmd            htpasswd2
%define ldap_clients            openldap2-client
%define jetty_init_script       jetty-sles.sh
%define apache_vhost_dir        %{apache}/vhosts.d
%endif
%if 0%{?rhel}
%define apache                  httpd
%define apache_tools            httpd-tools
%define apache_group            apache
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
Summary: Configuration management and audit tool - webapp
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: %{real_epoch}
License: GPLv3
URL: https://www.rudder.io/

Group: Applications/System

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

AutoReq: 0
AutoProv: 0

# Smooth upgrade
Obsoletes: ncf, ncf-api-virtualenv, rudder-techniques, rudder-inventory-ldap, rudder-ldap
# Prevent reinstalling old versions
Conflicts: ncf, ncf-api-virtualenv, rudder-techniques, rudder-inventory-ldap, rudder-ldap

BuildRequires: gcc
Requires: rsyslog

# Dependencies
Requires: %(../format-dependencies rpm %{real_epoch}:%{real_version} rudder-server-relay), %{apache}, %{apache_tools}, git-core, rsync, openssl, %{ldap_clients}, curl

# We need the PostgreSQL client utilities so that we can run database checks and upgrades (rudder-upgrade, in particular)
Requires: postgresql >= 9.2

# TODO obsolete / provides / conflicts

# OS-specific dependencies

## RHEL
%if 0%{?rhel}
BuildRequires: selinux-policy-devel
Requires: mod_ssl httpd shadow-utils
Requires: jre-headless >= 1.8
Requires: perl-Digest-SHA libtool-ltdl
BuildRequires: openssl-devel libtool-ltdl-devel
%endif

## SLES
%if 0%{?suse_version}
Requires: apache2 pwdutils libltdl7
BuildRequires: libopenssl-devel
%endif

%if 0%{?sle_version} && 0%{?sle_version} >= 120100 && 0%{?sle_version} < 150000
Requires: java-1_8_0-openjdk-headless
%endif

%if 0%{?sle_version} && 0%{?sle_version} >= 150000
Requires: jre-headless >= 8 insserv-compat
%endif

## Python 3
%if 0%{?rhel} && 0%{?rhel} == 7
BuildRequires: python
Requires: python, mod_wsgi
%endif
%if 0%{?rhel} && 0%{?rhel} == 8
BuildRequires: python3
Requires: python3, python3-mod_wsgi
%endif
# Doc for suse versioning https://en.opensuse.org/openSUSE:Packaging_for_Leap
%if 0%{?suse_version} && 0%{?suse_version} < 1500
BuildRequires: python
Requires: python, apache2-mod_wsgi, python-pyOpenSSL
%endif
%if 0%{?suse_version} && 0%{?suse_version} >= 1500
BuildRequires: python3
Requires: python3, apache2-mod_wsgi-python3
%endif


%description
Rudder is an open source configuration management and audit solution.

This package contains the web application that is the main user interface to
Rudder.

#=================================================
# Source preparation
#=================================================
%prep

cd %{_sourcedir}
make rudder-sources

# rhel7 and sles12 don't have mod wsgi python 3 so we force python2 instead
%if 0%{?rhel} == 7 || ( 0%{?suse_version} && 0%{?suse_version} < 1500 )
find . -type f | xargs sed -i '1,1s|#!/usr/bin/python3|#!/usr/bin/python2|'
%endif

#=================================================
# Building
#=================================================
%build

# Ensure an appropriate environment for the compiler
export CFLAGS="$RPM_OPT_FLAGS"

cd %{_sourcedir}
%if 0%{?rhel} == 7 || ( 0%{?suse_version} && 0%{?suse_version} < 1500 )
make build PYTHON=python2
%else
make build
%endif

%if 0%{?rhel}
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
# python should not be needed at install time, but build is run twice, i don't know why
%if 0%{?rhel} == 7 || ( 0%{?suse_version} && 0%{?suse_version} < 1500 )
make install APACHE_VHOSTDIR=%{apache_vhost_dir} DESTDIR=%{buildroot} JETTY_SCRIPT=%{jetty_init_script} APACHE_CONFDIR=%{apache_vhost_dir} PYTHON=python2
%else
make install APACHE_VHOSTDIR=%{apache_vhost_dir} DESTDIR=%{buildroot} JETTY_SCRIPT=%{jetty_init_script} APACHE_CONFDIR=%{apache_vhost_dir}
%endif

%if 0%{?rhel}
  # Install SELinux policy
  install -m 644  ncf-api-virtualenv.pp %{buildroot}/usr/share/ncf-api-virtualenv/share/selinux/
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
# We need to be sure that uuid.hive is set to root at beginning
mkdir -p /opt/rudder/etc
echo 'root' > /opt/rudder/etc/uuid.hive
mkdir -p /var/rudder/cfengine-community/
echo "127.0.0.1" > /var/rudder/cfengine-community/policy_server.dat

#=================================================
# Pre Installation
#=================================================
%pre -n rudder-webapp

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

  /opt/rudder/sbin/slapcat -b "cn=rudder-configuration" -l /var/rudder/ldap/backup/openldap-data-pre-upgrade-${TIMESTAMP}.ldif

  # Copy default file for migration
  [ -f /etc/default/rudder-slapd ] && mkdir -p /var/rudder/tmp/ && cp /etc/default/rudder-slapd /var/rudder/tmp/default-rudder-slapd
fi

service rudder-jetty stop >&2 > /dev/null
if [ -x /opt/rudder/bin/rudder-pkg ]
then
  /opt/rudder/bin/rudder-pkg plugin save-status > /tmp/rudder-plugins-upgrade
fi

CFRUDDER_FIRST_INSTALL=$1

if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 ]
then
    service rudder-jetty stop
fi

#=================================================
# Post Installation
#=================================================
%post -n rudder-webapp

RUDDER_FIRST_INSTALL="false"

if [ $1 -eq 1 ]
then
  RUDDER_FIRST_INSTALL="true"
fi

/opt/rudder/share/package-scripts/rudder-ldap-postinst "${RUDDER_FIRST_INSTALL}"

# Do this ONLY at first install
if [ $1 -eq 1 ]
then
  echo 'DAVLockDB /tmp/davlock.db' > /etc/%{apache}/conf.d/dav_mod.conf
fi

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


# Update /etc/sysconfig/apache2 in case an old module loading entry has already been created by Rudder
if [ -f /etc/sysconfig/apache2 ] && grep -q 'APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http' /etc/sysconfig/apache2
then
  echo "INFO: Upgrading the /etc/sysconfig/apache2 file, Rudder needed modules for Apache are now listed in /etc/sysconfig/rudder-relay-apache"
  sed -i 's%APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http.*%# This sources the Rudder needed by Rudder\n. /etc/sysconfig/rudder-relay-apache%' /etc/sysconfig/apache2
fi

/opt/rudder/share/package-scripts/rudder-webapp-postinst "${FIRST_INSTALL}" "%{apache}" "%{apache_user}" "%{apache_group}"

%if 0%{?rhel}
# SELinux support
# Check "sestatus" presence, and if here tweak our installation to be
# SELinux compliant
if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
  echo -n "INFO: Applying selinux policy..."
  # Add/Update the rudder-webapp SELinux policy
  semodule -i /opt/rudder/share/selinux/rudder-webapp.pp
  # Ensure inventory directories context is set by resetting
  # their context to the contexts defined in SELinux configuration,
  # including the file contexts defined in the rudder-webapp module
  restorecon -RF /var/rudder/configuration-repository/techniques

  # Add/Update the ncf-api-virtualenv SELinux policy
  semodule -i /usr/share/ncf-api-virtualenv/share/selinux/ncf-api-virtualenv.pp
  restorecon -RF /var/lib/ncf-api-venv/
  echo " Done"
fi
%endif

#=================================================
# Post Uninstallation
#=================================================
%postun -n rudder-webapp

# Do it only during uninstallation
if [ $1 -eq 0 ]; then
  if getent group %{config_repository_group} > /dev/null; then
    # Remove the configuration-repository group
    echo -n "INFO: Removing group %{config_repository_group}..."
    groupdel %{config_repository_group}
    echo " Done"
  fi

%if 0%{?suse_version}
  # Remove required includes in the SLES apache2 configuration
  if [ -f /etc/sysconfig/apache2 ]; then
    sed -i "/# This sources the modules\/defines needed by Rudder/d" /etc/sysconfig/apache2
    sed -i "/. \/etc\/sysconfig\/rudder-webapp-apache/d" /etc/sysconfig/apache2

    # Also remove an older comment that was erroneously added until 2.11.21 / 3.0.16 / 3.1.10 / 3.2.3
    sed -i "/# This sources the configuration file needed by Rudder/d" /etc/sysconfig/apache2
  fi
%endif

  # Remove the package user
  if getent passwd rudder-slapd >/dev/null; then
    echo -n "INFO: Removing the rudder-slapd user..."
    userdel rudder-slapd >/dev/null 2>&1
    echo " Done"
  fi
fi

%if 0%{?rhel}
  # Do it only during uninstallation
  if [ $1 -eq 0 ]; then
    if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
      if semodule -l | grep -q rudder-webapp; then
        echo -n "INFO: Removing selinux policy..."
        # Remove the ncf-api-virtualenv SELinux policy
        semodule -r ncf-api-virtualenv 2>/dev/null
        restorecon -RF /var/lib/ncf-api-venv/
        # Remove the rudder-webapp SELinux policy
        semodule -r rudder-webapp
        restorecon -RF /var/rudder/configuration-repository/techniques
        echo " Done"
      fi
    fi
  fi
%endif

# Do it only during uninstallation
if [ $1 -eq 0 ]; then
  # restart apache2 since it uses the user ncf
  systemctl restart %{apache} >/dev/null
  # Remove the package user
  if getent passwd ncf-api-venv >/dev/null; then
    echo -n "INFO: Removing the ncf-api-venv user..."
    userdel ncf-api-venv >/dev/null 2>&1
    echo " Done"
  fi
fi


#=================================================
# Pre Un-installation
#=================================================
%preun -n rudder-webapp

if [[ $1 -eq 0 ]]
then
  systemctl stop rudder-jetty
  systemctl stop rudder-slapd
fi


#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-webapp
%defattr(-, root, root, 0755)

/opt/rudder/etc/
%config(noreplace) /opt/rudder/etc/openldap/slapd.conf
%config(noreplace) /etc/rsyslog.d/rudder-slapd.conf
%config(noreplace) /opt/rudder/etc/rudder-web.properties
%config(noreplace) /opt/rudder/etc/rudder-users.xml
%config(noreplace) /opt/rudder/etc/logback.xml
%config(noreplace) /opt/rudder/etc/rudder-passwords.conf
%config(noreplace) /etc/default/rudder-jetty
%attr(0600, root, root) /opt/rudder/etc/rudder-passwords.conf
%attr(0755, rudder-slapd, rudder-slapd) /var/rudder/ldap/openldap-data
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
/var/rudder/run
/var/rudder/inventories/received
/var/rudder/inventories/failed
/var/rudder/configuration-repository/.gitignore
/var/log/rudder/ldap
/var/log/rudder/apache2/
/var/log/rudder/webapp/
/etc/%{apache_vhost_dir}/
%config /opt/rudder/etc/rudder-apache-webapp-common.conf
%config /opt/rudder/etc/rudder-apache-webapp-ssl.conf
%config /opt/rudder/etc/rudder-apache-webapp-nossl.conf
%config(noreplace) /etc/sysconfig/rudder-webapp-apache
/usr/share/doc/rudder
/usr/share/ncf/
/usr/share/ncf-api-virtualenv/
%attr(- , ncf-api-venv,ncf-api-venv) /var/lib/ncf-api-venv/
/etc/%{apache_vhost_dir}/ncf-api-virtualenv.conf

%config(noreplace) /opt/rudder/etc/inventory-web.properties


%if ! 0%{?suse_version}
# Avoid having .pyo and .pyc files in our package
# as they will always be regenerated
%exclude /usr/share/ncf/tree/10_ncf_internals/modules/templates/*.pyc
%exclude /usr/share/ncf/tree/10_ncf_internals/modules/templates/*.pyo
%endif


#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <dev@rudder.io> %{version}
- See https://docs.rudder.io/changelogs/current/index.html for changelogs
