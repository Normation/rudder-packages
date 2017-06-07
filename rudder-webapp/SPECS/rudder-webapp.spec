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
%define real_epoch              0

%define rudderdir               /opt/rudder
%define ruddervardir            /var/rudder
%define rudderlogdir            /var/log/rudder
%define sharedir                /usr/share

%define config_repository_group rudder

%define maven_settings settings-external.xml

%if 0%{?suse_version}
%define apache                  apache2
%define apache_tools            apache2-utils
%define apache_group            www
%define htpasswd_cmd            htpasswd2
%define syslogservicename       syslog
%define apache_vhost_dir        %{apache}/vhosts.d
%define ldap_clients            openldap2-client
# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version} >= 1200
%define usermod_opt             aG
%else
%define usermod_opt             A
%endif
%endif
%if 0%{?rhel} == 5 || 0%{?el5}
%define apache                  httpd
%define apache_tools            httpd-tools
%define apache_group            apache
%define htpasswd_cmd            htpasswd
%define syslogservicename       syslog
%define apache_vhost_dir        %{apache}/conf.d
%define ldap_clients            openldap-clients
%define usermod_opt             aG
%endif
%if 0%{?rhel} && 0%{?rhel} >= 6
%define apache                  httpd
%define apache_tools            httpd-tools
%define apache_group            apache
%define htpasswd_cmd            htpasswd
%define syslogservicename       rsyslog
%define apache_vhost_dir        %{apache}/conf.d
%define ldap_clients            openldap-clients
%define usermod_opt             aG
%endif

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - webapp
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: %{real_epoch}
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-users.xml
Source2: rudder.xml
Source5: rudder-upgrade
Source7: rudder-webapp
Source8: rudder-web
Source10: rudder-init
Source11: rudder-node-to-relay
Source12: rudder-root-rename
Source13: rudder-passwords.conf
Source14: rudder-plugin
Source15: post.write_technique.commit.sh
Source16: post.write_technique.rudderify.sh
Source17: rudder-metrics-reporting
Source18: ca-bundle.crt
Source19: rudder-reload-cf-serverd
Source20: rudder-webapp.te
Source22: rudder-keys
Source23: .gitignore
Source24: rudder-webapp-apache
Source25: rudder-apache-webapp-common.conf
Source26: rudder-apache-webapp-ssl.conf
Source27: rudder-apache-webapp-nossl.conf
Source28: rudder-webapp.fc

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# Dependencies
Requires: rudder-techniques = %{real_epoch}:%{real_version}, rudder-server-relay = %{real_epoch}:%{real_version}, ncf, ncf-api-virtualenv, %{apache}, %{apache_tools}, git-core, rsync, openssl, %{ldap_clients}

# We need the PostgreSQL client utilities so that we can run database checks and upgrades (rudder-upgrade, in particular)
Requires: postgresql >= 8.4

# OS-specific dependencies

##
## Those jetty packages are virtual packages provided by our Jetty and the system one.
##

## 1 - RHEL
%if 0%{?rhel} && 0%{?rhel} == 6
BuildRequires: java-1.8.0-openjdk-devel selinux-policy
%endif

%if 0%{?rhel} && 0%{?rhel} >= 7
BuildRequires: java-1.8.0-openjdk-devel selinux-policy-devel
%endif

%if 0%{?rhel}
Requires: mod_ssl jetty-eclipse
%endif

## 3 - SLES
## No Jetty provided by SLES... Use our own.
%if 0%{?suse_version}
BuildRequires: jdk >= 1.8
Requires: rudder-jetty = %{real_epoch}:%{real_version}
%endif

%description
Rudder is an open source configuration management and audit solution.

This package contains the web application that is the main user interface to
Rudder. The webapp is automatically installed and started using the Jetty
application server bundled in the rudder-jetty package.

#=================================================
# Source preparation
#=================================================
%prep

# Copy the required source files to the build directory
cp -f %{SOURCE20} %{_builddir}
cp -f %{SOURCE28} %{_builddir}
cp -rf %{_sourcedir}/rudder-sources %{_builddir}
cp -rf %{_sourcedir}/rudder-doc %{_builddir}

#=================================================
# Building
#=================================================
%build

%if 0%{?rhel} || 0%{?fedora}
# Build SELinux policy package
# Compiles rudder-webapp.te and rudder-webapp.fc into rudder-webapp.pp
cd %{_builddir} && make -f /usr/share/selinux/devel/Makefile
%endif

# Build rudder-web war
export MAVEN_OPTS=-Xmx512m
if [ -f %{_sourcedir}/rudder.war ]
then
  cp %{_sourcedir}/rudder.war %{_builddir}/rudder.war
else
  cd %{_builddir}/rudder-sources/rudder-parent-pom && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
  cd %{_builddir}/rudder-sources/rudder-commons    && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
  cd %{_builddir}/rudder-sources/scala-ldap        && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
  cd %{_builddir}/rudder-sources/ldap-inventory    && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
  cd %{_builddir}/rudder-sources/rudder            && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install package
  mv %{_builddir}/rudder-sources/rudder/rudder-web/target/rudder-web*.war %{_builddir}/rudder.war
fi

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{rudderdir}/etc/
mkdir -p %{buildroot}%{rudderdir}/etc/plugins/
mkdir -p %{buildroot}%{rudderdir}/etc/server-roles.d/
mkdir -p %{buildroot}%{rudderdir}/etc/hooks.d/
mkdir -p %{buildroot}%{rudderdir}/bin/
mkdir -p %{buildroot}%{rudderdir}/share/webapps/
mkdir -p %{buildroot}%{rudderdir}/share/rudder-plugins/
mkdir -p %{buildroot}%{rudderdir}/share/tools
mkdir -p %{buildroot}%{rudderdir}/share/plugins/
mkdir -p %{buildroot}%{rudderdir}/share/upgrade-tools/
mkdir -p %{buildroot}%{rudderdir}/share/certificates/
mkdir -p %{buildroot}%{rudderdir}/share/selinux/
mkdir -p %{buildroot}%{ruddervardir}/inventories/received
mkdir -p %{buildroot}%{ruddervardir}/inventories/failed
mkdir -p %{buildroot}%{ruddervardir}/configuration-repository/ncf/ncf-hooks.d
mkdir -p %{buildroot}%{rudderlogdir}/apache2/
mkdir -p %{buildroot}/etc/%{apache_vhost_dir}/
mkdir -p %{buildroot}/etc/sysconfig/
mkdir -p %{buildroot}/usr/share/doc/rudder

# Emulate installation of file rudder.xml in order to be owned by package
mkdir -p %{buildroot}%{rudderdir}/jetty7/contexts/
touch %{buildroot}%{rudderdir}/jetty7/contexts/rudder.xml

# Install helper scripts
cp %{SOURCE10} %{buildroot}%{rudderdir}/bin/

# %{rudderdir}/bin/rudder-init.sh -> %{rudderdir}/bin/rudder-init
ln -sf %{rudderdir}/bin/rudder-init %{buildroot}%{rudderdir}/bin/rudder-init.sh

cp %{SOURCE11} %{buildroot}%{rudderdir}/bin/
cp %{SOURCE12} %{buildroot}%{rudderdir}/bin/
cp %{SOURCE14} %{buildroot}%{rudderdir}/bin/
cp %{SOURCE17} %{buildroot}%{rudderdir}/bin/
cp %{SOURCE19} %{buildroot}%{rudderdir}/bin/

cp %{SOURCE1} %{buildroot}%{rudderdir}/etc/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/ldap/bootstrap.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/ldap/init-policy-server.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/configuration.properties.sample %{buildroot}%{rudderdir}/etc/rudder-web.properties
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/logback.xml %{buildroot}%{rudderdir}/etc/

cp %{_builddir}/rudder.war %{buildroot}%{rudderdir}/share/webapps/rudder.war

cp -rf %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/load-page %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/test/resources/script/cfe-red-button.sh %{buildroot}%{rudderdir}/bin/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/reportsInfo.xml %{buildroot}%{rudderdir}/etc/
cp %{SOURCE25} %{buildroot}%{rudderdir}/etc/rudder-apache-webapp-common.conf
cp %{SOURCE26} %{buildroot}%{rudderdir}/etc/rudder-apache-webapp-ssl.conf
cp %{SOURCE27} %{buildroot}%{rudderdir}/etc/rudder-apache-webapp-nossl.conf
cp %{SOURCE24} %{buildroot}/etc/sysconfig/rudder-webapp-apache

cp -r %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/hooks.d %{buildroot}%{rudderdir}/etc/

install -m 644 %{SOURCE2} %{buildroot}%{rudderdir}/share/webapps/

# Install upgrade tools and migration scripts

## SQL
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.10-2.10-historization-of-groups-in-rules.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.10-2.10-historization-of-agent-schedule.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.11-2.11-index-eventlog.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-3.0-3.0-add-index-changes-executiontimestamp.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-3.2.x-4.0-add-nodeconfigurations.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-3.2.x-4.0-add-archived-tables.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-4.0.x-4.1-add-compliance-table.sql %{buildroot}%{rudderdir}/share/upgrade-tools/

## LDAP
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/ldapMigration-2.11-2.11-add-api-compatibility-mode.ldif %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/ldapMigration-3.1.x-3.1.14-3.2.7-disable-js-directive.ldif %{buildroot}%{rudderdir}/share/upgrade-tools/

cp %{SOURCE5} %{buildroot}%{rudderdir}/bin/

install -m 644 %{SOURCE7} %{buildroot}/opt/rudder/etc/server-roles.d/
cp %{SOURCE13} %{buildroot}%{rudderdir}/etc/

install -m 755 %{SOURCE15} %{buildroot}%{ruddervardir}/configuration-repository/ncf/ncf-hooks.d/
install -m 755 %{SOURCE16} %{buildroot}%{ruddervardir}/configuration-repository/ncf/ncf-hooks.d/

# Add rudder-metrics-reporting
cp %{SOURCE17} %{buildroot}%{rudderdir}/bin/
cp %{SOURCE18} %{buildroot}%{rudderdir}/share/certificates/

# Install documentation
cp -rf %{_builddir}/rudder-doc/pdf %{buildroot}/usr/share/doc/rudder
cp -rf %{_builddir}/rudder-doc/html %{buildroot}/usr/share/doc/rudder

%if 0%{?rhel} || 0%{?fedora}
# Install SELinux policy
install -m 644  %{_builddir}/rudder-webapp.pp %{buildroot}%{rudderdir}/share/selinux/
%endif

# Install rudder keys
install -m 755 %{SOURCE22} %{buildroot}%{rudderdir}/bin/

# Install gitignore file for our git repo
install -m 644 %{SOURCE23} %{buildroot}%{ruddervardir}/configuration-repository/

%pre -n rudder-webapp
#=================================================
# Pre Installation
#=================================================
service rudder-jetty stop
if [ -x /opt/ruder/bin/rudder-pkg ]
then
  /opt/ruder/bin/rudder-pkg save-status > /tmp/rudder-plugins-upgrade
fi

%post -n rudder-webapp
#=================================================
# Post Installation
#=================================================

# Currently, we assume that the server where the webapp is installed
# is the root server. Force the UUID.
echo 'root' > /opt/rudder/etc/uuid.hive

echo -n "INFO: Setting Apache HTTPd as a boot service..."
%if 0%{?rhel} && 0%{?rhel} < 7
chkconfig --add %{apache} 2&> /dev/null
%endif
%if 0%{?rhel} && 0%{?rhel} == 6
chkconfig %{apache} on
%endif
%if 0%{?rhel} && 0%{?rhel} >= 7
systemctl enable %{apache}.service
%endif
echo " Done"

echo -n "INFO: Restarting syslog..."
%if 0%{?rhel} < 7
service %{syslogservicename} restart > /dev/null
%endif
%if 0%{?rhel} >= 7
/bin/systemctl restart  rsyslog.service
%endif
echo " Done"

echo -n "INFO: Stopping Apache HTTPd..."
%if 0%{?rhel} < 7
service %{apache} stop >/dev/null 2>&1
%endif
%if 0%{?rhel} >= 7
/bin/systemctl stop %{apache}.service
%endif
echo " Done"

# Do this ONLY at first install
if [ $1 -eq 1 ]
then
  echo 'DAVLockDB /tmp/davlock.db' > /etc/%{apache}/conf.d/dav_mod.conf
fi

# Create the configuration-repository group if it does not exist
if ! getent group %{config_repository_group} > /dev/null; then
  echo -n "INFO: Creating group %{config_repository_group}..."
  groupadd --system %{config_repository_group}
  echo " Done"
fi

# Create the rudder-policy-reader group
if ! getent group rudder-policy-reader > /dev/null; then
  echo -n "INFO: Creating group rudder-policy-reader..."
  groupadd --system rudder-policy-reader
%if 0%{?suse_version}
  usermod -a -G rudder-policy-reader wwwrun
%endif
%if 0%{?rhel}
  usermod -a -G rudder-policy-reader apache
%endif
  echo " Done"
fi

# Add the ncf-api-venv user to this group
if ! getent group %{config_repository_group} | grep -q ncf-api-venv > /dev/null; then
  echo -n "INFO: Adding ncf-api-venv to the %{config_repository_group} group..."
  usermod -%{usermod_opt} %{config_repository_group} ncf-api-venv
  echo " Done"
fi

# Add required includes in the SLES apache2 configuration
%if 0%{?suse_version}
if ! grep -qE "^. /etc/sysconfig/rudder-webapp-apache$" /etc/sysconfig/apache2
then
	echo -e '# This sources the modules/defines needed by Rudder\n. /etc/sysconfig/rudder-webapp-apache' >> /etc/sysconfig/apache2
fi
%endif

# Update /etc/sysconfig/apache2 in case an old module loading entry has already been created by Rudder
if [ -f /etc/sysconfig/apache2 ] && grep -q 'APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http' /etc/sysconfig/apache2
then
	echo "INFO: Upgrading the /etc/sysconfig/apache2 file, Rudder needed modules for Apache are now listed in /etc/sysconfig/rudder-relay-apache"
	sed -i 's%APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http.*%# This sources the Rudder needed by Rudder\n. /etc/sysconfig/rudder-relay-apache%' /etc/sysconfig/apache2
fi

# Add perms on tools and inventories
chmod 751 /var/rudder/inventories
chmod 755 -R %{rudderdir}/share/tools
chmod 655 -R %{rudderdir}/share/load-page

# Run any upgrades
# Note this must happen *before* creating the technique store, as it was moved in version 2.3.2
# and creating it manually would break the upgrade logic
echo "INFO: Launching script to check if a migration is needed"
%{rudderdir}/bin/rudder-upgrade
echo "INFO: End of migration script"

# Create and populate technique store
if [ ! -d /var/rudder/configuration-repository/shared-files ]; then
  mkdir -p /var/rudder/configuration-repository/shared-files
  touch /var/rudder/configuration-repository/shared-files/.placeholder
fi
if [ ! -d /var/rudder/configuration-repository/techniques ]; then
	cp -a %{rudderdir}/share/techniques /var/rudder/configuration-repository/
        touch /opt/rudder/etc/force_technique_reload
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

echo -n "INFO: Starting Apache HTTPd..."
%if 0%{?rhel} < 7
service %{apache} start >/dev/null 2>&1
%endif
%if 0%{?rhel} >= 7
/bin/systemctl start %{apache}.service
%endif
echo " Done"


# Go into configuration-repository to manage git
cd /var/rudder/configuration-repository

# Initialize git repository if it is missing, so permissions can be set on it afterwards
if [ ! -d /var/rudder/configuration-repository/.git ]; then

  git init --shared=group

  # Specify default git user name and email (git will refuse to commit without them)
  git config user.name "root user (CLI)"
  git config user.email "root@localhost"

  git add .
  git commit -q -m "initial commit"
else

  # This should have been set during repository initialization, but might need to be
  # added if we are upgrading an existing repository
  if [ $(git config --get-regexp "user.name|user.email"|wc -l) -ne 2 ]; then
    git config user.name "root user (CLI)"
    git config user.email "root@localhost"
  fi

  # Set shared repository value to group if not set
  if ! git config core.sharedRepository >/dev/null 2>&1; then
    git config core.sharedRepository group
  fi

fi

# Adjust permissions on /var/rudder/configuration-repository
chgrp -R %{config_repository_group} /var/rudder/configuration-repository

## Add execution permission for ncf-api only on directories and files with user execution permission
chmod -R u+rwX,g+rwX %{ruddervardir}/configuration-repository/.git
chmod -R u+rwX,g+rwX %{ruddervardir}/configuration-repository/ncf
chmod -R u+rwX,g+rwX %{ruddervardir}/configuration-repository/techniques

## Add setgid to directories so that all files created here belong to the %{config_repository_group} group
find %{ruddervardir}/configuration-repository/.git %{ruddervardir}/configuration-repository/ncf %{ruddervardir}/configuration-repository/techniques -type d -exec chmod g+s "{}" \;

## Add execution permission for ncf-api on pre/post-hooks
chmod -R 2750 %{ruddervardir}/configuration-repository/ncf/ncf-hooks.d/

# Create a symlink to the Jetty context if necessary
if [ -d "%{rudderdir}/jetty7/contexts" ]; then
  ln -sf %{rudderdir}/share/webapps/rudder.xml %{rudderdir}/jetty7/contexts/rudder.xml
fi

if [ -f /tmp/rudder-plugins-upgrade ]
then
  /opt/ruder/bin/rudder-pkg restore-status < /tmp/rudder-plugins-upgrade
fi

service rudder-jetty start

%postun -n rudder-webapp
#=================================================
# Post Uninstallation
#=================================================

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

fi

%if 0%{?rhel} || 0%{?fedora}
  # Do it only during uninstallation
  if [ $1 -eq 0 ]; then
    if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
      if semodule -l | grep -q rudder-webapp; then
        # Remove the rudder-webapp SELinux policy
        semodule -r rudder-webapp
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
%files -n rudder-webapp
%defattr(-, root, root, 0755)

%{rudderdir}/etc/
%config(noreplace) %{rudderdir}/etc/rudder-web.properties
%config(noreplace) %{rudderdir}/etc/rudder-users.xml
%config(noreplace) %{rudderdir}/etc/logback.xml
%config(noreplace) %{rudderdir}/etc/rudder-passwords.conf
%attr(0600, root, root) %{rudderdir}/etc/rudder-passwords.conf
# Prevent /opt/rudder/jetty7/contexts/rudder.xml to be erased during upgrade
%ghost %{rudderdir}/jetty7/contexts/rudder.xml

%{rudderdir}/bin/
%{rudderdir}/bin/rudder-node-to-relay
%{rudderdir}/bin/rudder-init
%{rudderdir}/bin/rudder-init.sh
%{rudderdir}/bin/rudder-root-rename
%{rudderdir}/bin/rudder-reload-cf-serverd
%{rudderdir}/share/webapps/
%{rudderdir}/share/rudder-plugins/
%{rudderdir}/share
%{ruddervardir}/inventories/received
%{ruddervardir}/inventories/failed
%{ruddervardir}/configuration-repository/.gitignore
%{ruddervardir}/configuration-repository/ncf/ncf-hooks.d
%{rudderlogdir}/apache2/
/etc/%{apache_vhost_dir}/
%config %{rudderdir}/etc/rudder-apache-webapp-common.conf
%config %{rudderdir}/etc/rudder-apache-webapp-ssl.conf
%config %{rudderdir}/etc/rudder-apache-webapp-nossl.conf
%config(noreplace) /etc/sysconfig/rudder-webapp-apache
/usr/share/doc/rudder

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 28 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
