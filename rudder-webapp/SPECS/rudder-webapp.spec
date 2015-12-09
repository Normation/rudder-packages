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
# Specification file for rudder-webapp
#
# Installs Rudder's WAR files
#
# Copyright (C) 2011 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name               rudder-webapp

%define rudderdir               /opt/rudder
%define ruddervardir            /var/rudder
%define rudderlogdir            /var/log/rudder
%define sharedir                /usr/share

%define config_repository_group rudder

%define maven_settings settings-external.xml

%if 0%{?sles_version}
%define apache                  apache2
%define apache_tools            apache2-utils
%define apache_group            www
%define htpasswd_cmd            htpasswd2
%define syslogservicename       syslog
%define apache_vhost_dir        %{apache}/vhosts.d
%define ldap_clients            openldap2-client
%define usermod_opt             A
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
Epoch: 0
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-users.xml
Source2: rudder.xml
Source3: rudder-networks.conf
Source4: rudder-networks-24.conf
Source5: rudder-upgrade
Source6: rudder-upgrade-database
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
Source21: rudder-webapp.fc
Source22: rudder-keys
Source23: .gitignore

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# Dependencies
Requires: rudder-techniques ncf ncf-api-virtualenv %{apache} %{apache_tools} git-core rsync openssl %{ldap_clients}

# We need the PostgreSQL client utilities so that we can run database checks and upgrades (rudder-upgrade, in particular)
Requires: postgresql >= 8.4

# OS-specific dependencies

##
## Those jetty packages are virtual packages provided by our Jetty and the system one.
##

## 1 - RHEL
%if 0%{?rhel} && 0%{?rhel} == 6
BuildRequires: java7-devel selinux-policy
%endif

%if 0%{?rhel} && 0%{?rhel} >= 7
BuildRequires: java-devel selinux-policy-devel
%endif

%if 0%{?rhel}
Requires: mod_ssl jetty-eclipse
%endif

## 2 - Fedora
%if 0%{?fedora}
# Cf. https://fedoraproject.org/wiki/Packaging:Java for details
BuildRequires: java-devel selinux-policy-devel
Requires: jetty-server
%endif

## 3 - SLES
## No Jetty provided by SLES... Use our own.
%if 0%{?sles_version}
BuildRequires: jdk >= 1.7
Requires: rudder-jetty
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
cp -f %{SOURCE21} %{_builddir}
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
cd %{_builddir}/rudder-sources/rudder-parent-pom && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/rudder-commons    && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/scala-ldap        && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/ldap-inventory    && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/rudder            && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install package

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{rudderdir}/etc/
mkdir -p %{buildroot}%{rudderdir}/etc/ssl/
mkdir -p %{buildroot}%{rudderdir}/etc/plugins/
mkdir -p %{buildroot}%{rudderdir}/etc/server-roles.d/
mkdir -p %{buildroot}%{rudderdir}/bin/
mkdir -p %{buildroot}%{rudderdir}/share/webapps/
mkdir -p %{buildroot}%{rudderdir}/share/rudder-plugins/
mkdir -p %{buildroot}%{rudderdir}/share/tools
mkdir -p %{buildroot}%{rudderdir}/share/plugins/
mkdir -p %{buildroot}%{rudderdir}/share/upgrade-tools/
mkdir -p %{buildroot}%{rudderdir}/share/certificates/
mkdir -p %{buildroot}%{rudderdir}/share/selinux/
mkdir -p %{buildroot}%{ruddervardir}/inventories/incoming
mkdir -p %{buildroot}%{ruddervardir}/inventories/accepted-nodes-updates
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

cp %{_builddir}/rudder-sources/rudder/rudder-web/target/rudder-web*.war %{buildroot}%{rudderdir}/share/webapps/rudder.war

cp -rf %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/load-page %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/test/resources/script/cfe-red-button.sh %{buildroot}%{rudderdir}/bin/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/reportsInfo.xml %{buildroot}%{rudderdir}/etc/
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/rudder-apache-common.conf %{buildroot}%{rudderdir}/etc/rudder-apache-common.conf
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/rudder-vhost.conf %{buildroot}/etc/%{apache_vhost_dir}/rudder-vhost.conf
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/rudder-vhost-ssl.conf %{buildroot}/etc/%{apache_vhost_dir}/rudder-vhost-ssl.conf
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/apache2-sysconfig %{buildroot}/etc/sysconfig/rudder-apache

install -m 644 %{SOURCE2} %{buildroot}%{rudderdir}/share/webapps/

# Copy stub rudder-networks*.conf
cp %{SOURCE3} %{buildroot}%{rudderdir}/etc/
cp %{SOURCE4} %{buildroot}%{rudderdir}/etc/

%if 0%{?sles_version}
# On SLES, change the Apache DocumentRoot to the OS default
sed -i "s%^DocumentRoot /var/www$%DocumentRoot /srv/www%" %{buildroot}%{rudderdir}/etc/rudder-apache-common.conf
%endif

# Install upgrade tools and migration scripts

## SQL
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-change-ids-in-tables.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-migrate-reports-per-node.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.10-2.10-historization-of-groups-in-rules.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.10-2.10-historization-of-agent-schedule.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.11-2.12-add-nodeconfigids-columns.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.11-3.0-add-insertionids-column.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.11-3.0-remove-varchar.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.11-3.0-set-migration-needed-flag-for-EventLog.sql %{buildroot}%{rudderdir}/share/upgrade-tools/

## LDAP
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/ldapMigration-3.0-3.1-set-syslog-protocol.ldif %{buildroot}%{rudderdir}/share/upgrade-tools/

cp %{SOURCE5} %{buildroot}%{rudderdir}/bin/
cp %{SOURCE6} %{buildroot}%{rudderdir}/bin/

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

%post -n rudder-webapp
#=================================================
# Post Installation
#=================================================

# Currently, we assume that the server where the webapp is installed
# is the root server. Force the UUID.
echo 'root' > /opt/rudder/etc/uuid.hive

echo -n "INFO: Setting Apache HTTPd as a boot service..."
chkconfig --add %{apache} 2&> /dev/null
%if 0%{?rhel} && 0%{?rhel} >= 6
chkconfig %{apache} on
%endif
echo " Done"

echo -n "INFO: Restarting syslog..."
service %{syslogservicename} restart > /dev/null
echo " Done"

echo -n "INFO: Stopping Apache HTTPd..."
service %{apache} stop >/dev/null 2>&1
echo " Done"

# Do this ONLY at first install
if [ $1 -eq 1 ]
then
		echo -e '# This sources the configuration file needed by Rudder\n. /etc/sysconfig/rudder-apache' >> /etc/sysconfig/apache2
		echo 'DAVLockDB /tmp/davlock.db' > /etc/%{apache}/conf.d/dav_mod.conf
fi

# Create the configuration-repository group if it does not exist
if ! getent group %{config_repository_group} > /dev/null; then
  echo -n "INFO: Creating group %{config_repository_group}..."
  groupadd --system %{config_repository_group}
  echo " Done"
fi

# Add the ncf-api-venv user to this group
if ! getent group %{config_repository_group} | grep -q ncf-api-venv > /dev/null; then
  echo -n "INFO: Adding ncf-api-venv to the %{config_repository_group} group..."
  usermod -%{usermod_opt} %{config_repository_group} ncf-api-venv
  echo " Done"
fi

# Add required includes in the SLES apache2 configuration
%if 0%{?sles_version}
if ! grep -qE "^. /etc/sysconfig/rudder-apache$" /etc/sysconfig/apache2
then
	echo -e '# This sources the modules/defines needed by Rudder\n. /etc/sysconfig/rudder-apache' >> /etc/sysconfig/apache2
fi
%endif

# Update /etc/sysconfig/apache2 in case an old module loading entry has already been created by Rudder
if grep -q 'APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http' /etc/sysconfig/apache2
then
	echo "INFO: Upgrading the /etc/sysconfig/apache2 file, Rudder needed modules for Apache are now listed in /etc/sysconfig/rudder-apache"
	sed -i 's%APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http.*%# This sources the Rudder needed by Rudder\n. /etc/sysconfig/rudder-apache%' /etc/sysconfig/apache2
fi

# Add right to apache user to access /var/rudder/inventories/incoming
chmod 751 /var/rudder/inventories
chown root:%{apache_group} %{ruddervardir}/inventories/incoming
chmod 2770 %{ruddervardir}/inventories/incoming
chown root:%{apache_group} %{ruddervardir}/inventories/accepted-nodes-updates
chmod 2770 %{ruddervardir}/inventories/accepted-nodes-updates
chmod 755 -R %{rudderdir}/share/tools
chmod 655 -R %{rudderdir}/share/load-page

%{htpasswd_cmd} -bc %{rudderdir}/etc/htpasswd-webdav-initial rudder rudder  >/dev/null 2>&1
%{htpasswd_cmd} -bc %{rudderdir}/etc/htpasswd-webdav rudder rudder  >/dev/null 2>&1

# If the current Rudder HTTPd configuration uses /var/log/rudder/httpd, change it
for i in /etc/%{apache_vhost_dir}/rudder-*.conf
do
	if grep -q /var/log/rudder/httpd "${i}"; then
		echo -n "INFO: Old logging configuration detected in ${i}, changing to log into %{rudderlogdir}/apache2..."
		sed -i "s%/var/log/rudder/httpd/\(.*\).log%/var/log/rudder/apache2/\1.log%" "${i}"
		echo " Done"
	fi
done

# If this machine has old logging entries on RHEL, migrate them.
if [ -d %{rudderlogdir}/httpd ]; then
	echo -n "INFO: Old logging directory detected (%{rudderlogdir}/httpd), migrating to %{rudderlogdir}/apache2..."
	mkdir -p %{rudderlogdir}/apache2
	mv %{rudderlogdir}/httpd/* %{rudderlogdir}/apache2/
	rmdir %{rudderlogdir}/httpd
	echo " Done"
fi

# Move old virtual hosts out of the way
for OLD_VHOST in rudder-default rudder-default-ssl rudder-default.conf rudder-default-ssl.conf; do
	if [ -f /etc/%{apache_vhost_dir}/${OLD_VHOST} ]; then
		echo -n "INFO: An old rudder virtual host file has been detected (${OLD_VHOST}), it will be moved to /var/backups."
		mkdir -p /var/backups
		mv /etc/%{apache_vhost_dir}/${OLD_VHOST} /var/backups/${OLD_VHOST}-$(date +%s)
		echo " Done"
	fi
done

# Generate the SSL certificates if needed
if [ ! -f /opt/rudder/etc/ssl/rudder-webapp.crt ] || [ ! -f /opt/rudder/etc/ssl/rudder-webapp.key ]; then
	echo -n "INFO: No usable SSL certificate detected for Rudder HTTP/S support, generating one automatically..."
	openssl req -new -x509 -newkey rsa:2048 -subj "/CN=$(hostname --fqdn)/" -keyout /opt/rudder/etc/ssl/rudder-webapp.key -out /opt/rudder/etc/ssl/rudder-webapp.crt -days 1460 -nodes -sha256 >/dev/null 2>&1
	chgrp %{apache_group} /opt/rudder/etc/ssl/rudder-webapp.key && chmod 640 /opt/rudder/etc/ssl/rudder-webapp.key
	echo " Done"
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
  restorecon -R /var/rudder/inventories
  restorecon -R /var/log/rudder/apache2
fi
%endif

echo -n "INFO: Starting Apache HTTPd..."
service %{apache} start >/dev/null 2>&1
echo " Done"

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
fi

# Apply selinux context on configuration repository so technique editor (via apache/httpd) can write in this directory
if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
  semanage fcontext -a -t httpd_sys_rw_content_t '/var/rudder/configuration-repository/techniques(/.*)?'
  restorecon -RF /var/rudder/configuration-repository/techniques
fi

# Go into configuration-repository to manage git
cd /var/rudder/configuration-repository

# Initialize git repository if it is missing, so permissions can be set on it afterwards
if [ ! -d /var/rudder/configuration-repository/.git ]; then

  git init --shared=group

  # Specify default git user name and email (git will refuse to commit without them)
  git config user.name "root user (CLI)"
  git config user.email "root@localhost"

  git add .
  git commit -q -m "initial commit"
else

  # This should have been set during repository initialization, but might need to be
  # added if we are upgrading an existing repository
  if [ $(git config --get-regexp "user.name|user.email"|wc -l) -ne 2 ]; then
    git config user.name "root user (CLI)"
    git config user.email "root@localhost"
  fi

  # Set shared repository value to group if not set
  if ! git config core.sharedRepository >/dev/null 2>&1; then
    git config core.sharedRepository group
  fi

fi

# Adjust permissions on /var/rudder/configuration-repository
chgrp -R %{config_repository_group} /var/rudder/configuration-repository

## Add execution permission for ncf-api only on directories and files with user execution permission
chmod -R u+rwX,g+rwsX %{ruddervardir}/configuration-repository/.git
chmod -R u+rwX,g+rwsX %{ruddervardir}/configuration-repository/ncf
chmod -R u+rwX,g+rwsX %{ruddervardir}/configuration-repository/techniques

## Add execution permission for ncf-apo on pre/post-hooks
chmod -R 2750 %{ruddervardir}/configuration-repository/ncf/ncf-hooks.d/

# Create a symlink to the Jetty context if necessary
if [ -d "%{rudderdir}/jetty7/contexts" ]; then
  ln -sf %{rudderdir}/share/webapps/rudder.xml %{rudderdir}/jetty7/contexts/rudder.xml
fi

# Warn the user that Jetty needs restarting. This can't be done automatically due to a bug in Jetty's init script.
# See http://www.rudder-project.org/redmine/issues/2807
echo "********************************************************************************"
echo "rudder-webapp has been upgraded, but for the upgrade to take effect, please"
echo "restart the jetty application server as follows:"
echo "# service rudder-jetty restart"
echo "********************************************************************************"

%postun -n rudder-webapp
#=================================================
# Post Uninstallation
#=================================================

# Do it only during uninstallation
if [ $1 -eq 0 ]; then
  if getent group %{config_repository_group} > /dev/null; then
    # Remove the configuration-repository group
    echo -n "INFO: Removing group %{config_repository_group}..."
    groupdel %{config_repository_group}
    echo " Done"
  fi
fi

%if 0%{?rhel} || 0%{?fedora}
  # Do it only during uninstallation
  if [ $1 -eq 0 ]; then
    if type sestatus >/dev/null 2>&1 && sestatus | grep -q "enabled"; then
      if semodule -l | grep -q rudder-webapp; then
        # Remove the rudder-webapp SELinux policy
        semanage fcontext -d '/var/rudder/configuration-repository/techniques(/.*)?'
        restorecon -RF /var/rudder/configuration-repository/techniques
        semodule -r rudder-webapp
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
%{ruddervardir}/inventories/accepted-nodes-updates
%{ruddervardir}/inventories/incoming
%{ruddervardir}/inventories/received
%{ruddervardir}/inventories/failed
%{ruddervardir}/configuration-repository/.gitignore
%{ruddervardir}/configuration-repository/ncf/ncf-hooks.d
%{rudderlogdir}/apache2/
/etc/%{apache_vhost_dir}/
%config(noreplace) %{rudderdir}/etc/rudder-apache-common.conf
%config(noreplace) /etc/%{apache_vhost_dir}/rudder-vhost.conf
%config(noreplace) /etc/%{apache_vhost_dir}/rudder-vhost-ssl.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks-24.conf
%config(noreplace) /etc/sysconfig/rudder-apache
/usr/share/doc/rudder
%{rudderdir}/bin/rudder-upgrade-database

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 28 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
