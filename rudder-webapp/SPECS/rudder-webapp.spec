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
%define real_name        rudder-webapp

%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder
%define sharedir         /usr/share

%define maven_settings settings-external.xml

%if 0%{?sles_version}
%define apache              apache2
%define apache_tools        apache2-utils
%define apache_group        www
%define htpasswd_cmd        htpasswd2
%define sysloginitscript    /etc/init.d/syslog
%define apache_vhost_dir    %{apache}/vhosts.d
%endif
%if 0%{?el5}
%define apache              httpd
%define apache_tools        httpd-tools
%define apache_group        apache
%define htpasswd_cmd        htpasswd
%define sysloginitscript    /etc/init.d/syslog
%define apache_vhost_dir    %{apache}/conf.d
%endif
%if 0%{?el6}
%define apache              httpd
%define apache_tools        httpd-tools
%define apache_group        apache
%define htpasswd_cmd        htpasswd
%define sysloginitscript    /etc/init.d/rsyslog
%define apache_vhost_dir    %{apache}/conf.d
%endif

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - webapp
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 0
License: AGPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-users.xml
Source2: rudder.xml
Source3: rudder-networks.conf
Source5: rudder-upgrade
Source6: rudder-upgrade-database

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

BuildRequires: jdk >= 1.6
Requires: rudder-jetty rudder-techniques ncf %{apache} %{apache_tools} git-core rsync openssl

%if 0%{?rhel}
Requires: mod_ssl
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

cp -rf %{_sourcedir}/rudder-sources %{_builddir}
cp -rf %{_sourcedir}/rudder-doc %{_builddir}

#=================================================
# Building
#=================================================
%build

export MAVEN_OPTS=-Xmx512m
cd %{_builddir}/rudder-sources/rudder-parent-pom && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/rudder-commons    && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/scala-ldap        && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/ldap-inventory    && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/cf-clerk          && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/rudder            && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install package

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{rudderdir}/etc/
mkdir -p %{buildroot}%{rudderdir}/etc/ssl/
mkdir -p %{buildroot}%{rudderdir}/etc/plugins/
mkdir -p %{buildroot}%{rudderdir}/bin/
mkdir -p %{buildroot}%{rudderdir}/jetty7/webapps/
mkdir -p %{buildroot}%{rudderdir}/jetty7/contexts/
mkdir -p %{buildroot}%{rudderdir}/jetty7/rudder-plugins/
mkdir -p %{buildroot}%{rudderdir}/share/tools
mkdir -p %{buildroot}%{rudderdir}/share/plugins/
mkdir -p %{buildroot}%{rudderdir}/share/upgrade-tools/
mkdir -p %{buildroot}%{ruddervardir}/inventories/incoming
mkdir -p %{buildroot}%{ruddervardir}/inventories/accepted-nodes-updates
mkdir -p %{buildroot}%{ruddervardir}/inventories/received
mkdir -p %{buildroot}%{ruddervardir}/inventories/failed
mkdir -p %{buildroot}%{rudderlogdir}/apache2/
mkdir -p %{buildroot}/etc/%{apache_vhost_dir}/
mkdir -p %{buildroot}/etc/sysconfig/
mkdir -p %{buildroot}/usr/share/doc/rudder

cp %{SOURCE1} %{buildroot}%{rudderdir}/etc/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/ldap/bootstrap.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/ldap/init-policy-server.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/ldap/demo-data.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/configuration.properties.sample %{buildroot}%{rudderdir}/etc/rudder-web.properties
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/logback.xml %{buildroot}%{rudderdir}/etc/

cp %{_builddir}/rudder-sources/rudder/rudder-web/target/rudder-web*.war %{buildroot}%{rudderdir}/jetty7/webapps/rudder.war

cp -rf %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/load-page %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/test/resources/script/cfe-red-button.sh %{buildroot}%{rudderdir}/bin/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/reportsInfo.xml %{buildroot}%{rudderdir}/etc/
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/rudder-apache-common.conf %{buildroot}%{rudderdir}/etc/rudder-apache-common.conf
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/rudder-vhost.conf %{buildroot}/etc/%{apache_vhost_dir}/rudder-vhost.conf
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/rudder-vhost-ssl.conf %{buildroot}/etc/%{apache_vhost_dir}/rudder-vhost-ssl.conf
cp %{_sourcedir}/rudder-sources/rudder/rudder-web/src/main/resources/apache2-sysconfig %{buildroot}/etc/sysconfig/rudder-apache
cp %{SOURCE2} %{buildroot}%{rudderdir}/jetty7/contexts/
cp %{SOURCE3} %{buildroot}%{rudderdir}/etc/

# Install upgrade tools
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.4-2.4-set-migration-needed-flag-for-EventLog.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.6-2.7-set-migration-needed-flag-for-EventLog.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.8-2.9-set-migration-needed-flag-for-EventLog.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.7-2.8-add-nodes-executions-storage.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-upgrade-LDAP-schema-2.6-2.7-add-global-parameter-ou.ldif %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-upgrade-LDAP-schema-2.6-2.7-add-default-global-parameter.ldif %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-2.6-2.6-index-reports.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-change-ids-in-tables.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-migrate-reports-per-node.sql %{buildroot}%{rudderdir}/share/upgrade-tools/
cp %{_sourcedir}/rudder-sources/rudder/rudder-core/src/main/resources/Migration/ldapMigration-2.10-2.11-add-server-roles.ldif %{buildroot}%{rudderdir}/share/upgrade-tools/

cp %{SOURCE5} %{buildroot}%{rudderdir}/bin/
cp %{SOURCE6} %{buildroot}%{rudderdir}/bin/


# Install documentation
cp -rf %{_builddir}/rudder-doc/pdf %{buildroot}/usr/share/doc/rudder
cp -rf %{_builddir}/rudder-doc/html %{buildroot}/usr/share/doc/rudder

%pre -n rudder-webapp
#=================================================
# Pre Installation
#=================================================

%post -n rudder-webapp
#=================================================
# Post Installation
#=================================================

echo -n "INFO: Setting Apache HTTPd as a boot service..."
/sbin/chkconfig --add %{apache} 2&> /dev/null
%if 0%{?rhel} >= 6
/sbin/chkconfig %{apache} on
%endif
echo " Done"

echo -n "INFO: Restrating syslog..."
%{sysloginitscript} restart > /dev/null
echo " Done"

echo -n "INFO: Stopping Apache HTTPd..."
/sbin/service %{apache} stop >/dev/null 2>&1
echo " Done"

# Do this ONLY at first install
if [ $1 -eq 1 ]
then
		echo -e '# This sources the configuration file needed by Rudder\n. /etc/sysconfig/rudder-apache' >> /etc/sysconfig/apache2
		echo 'DAVLockDB /tmp/davlock.db' > /etc/%{apache}/conf.d/dav_mod.conf

		mkdir -p /var/rudder/configuration-repository
		mkdir -p /var/rudder/configuration-repository/shared-files
		touch /var/rudder/configuration-repository/shared-files/.placeholder
		cp -a %{rudderdir}/share/techniques /var/rudder/configuration-repository/
		ncf init /var/rudder/configuration-repository/ncf
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

echo -n "INFO: Starting Apache HTTPd..."
/sbin/service %{apache} start >/dev/null 2>&1
echo " Done"

# Run any upgrades
# Note this must happen *before* creating the technique store, as it was moved in version 2.3.2
# and creating it manually would break the upgrade logic
echo "INFO: Launching script to check if a migration is needed"
%{rudderdir}/bin/rudder-upgrade
echo "INFO: End of migration script"

# Create and populate technique store
if [ ! -d /var/rudder/configuration-repository ]; then mkdir -p /var/rudder/configuration-repository; fi
if [ ! -d /var/rudder/configuration-repository/shared-files ]; then mkdir -p /var/rudder/configuration-repository/shared-files; fi
if [ ! -d /var/rudder/configuration-repository/techniques ]; then
	cp -a %{rudderdir}/share/techniques /var/rudder/configuration-repository/
fi
if [ ! -d /var/rudder/configuration-repository/ncf ]; then
	ncf init /var/rudder/configuration-repository/ncf
fi

# Warn the user that Jetty needs restarting. This can't be done automatically due to a bug in Jetty's init script.
# See http://www.rudder-project.org/redmine/issues/2807
echo "********************************************************************************"
echo "rudder-webapp has been upgraded, but for the upgrade to take effect, please"
echo "restart the jetty application server as follows:"
echo "# /sbin/service rudder-jetty restart"
echo "********************************************************************************"

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
%{rudderdir}/bin/
%{rudderdir}/jetty7/webapps/
%{rudderdir}/jetty7/rudder-plugins/
%{rudderdir}/jetty7/contexts/rudder.xml
%{rudderdir}/share
%{ruddervardir}/inventories/accepted-nodes-updates
%{ruddervardir}/inventories/incoming
%{ruddervardir}/inventories/received
%{ruddervardir}/inventories/failed
%{rudderlogdir}/apache2/
/etc/%{apache_vhost_dir}/
%config(noreplace) %{rudderdir}/etc/rudder-apache-common.conf
%config(noreplace) /etc/%{apache_vhost_dir}/rudder-vhost.conf
%config(noreplace) /etc/%{apache_vhost_dir}/rudder-vhost-ssl.conf
%config(noreplace) %{rudderdir}/etc/rudder-networks.conf
%config(noreplace) /etc/sysconfig/rudder-apache
/usr/share/doc/rudder
%{rudderdir}/bin/rudder-upgrade-database

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 28 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
