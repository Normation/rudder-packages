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

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - webapp
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 1299256513
License: AGPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-users.xml
Source2: rudder.xml
Source3: settings-external.xml
Source4: settings-internal.xml

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

BuildRequires: jdk >= 1.6
Requires: rudder-jetty rudder-inventory-ldap rudder-inventory-endpoint rudder-reports rudder-policy-templates apache2 apache2-utils git-core

%description
Rudder is an open source configuration management and audit solution.

This package contains the web application that is the main user interface to
Rudder. The webapp is automatically installed and started using the Jetty
application server bundled in the rudder-jetty package.


#=================================================
# Source preparation
#=================================================
%prep

cp -rf %{_sourcedir}/source %{_builddir}

#=================================================
# Building
#=================================================
%build

cd %{_builddir}/source/rudder-parent-pom && %{_sourcedir}/maven2/bin/mvn -s %{SOURCE3} -Dmaven.test.skip=true install
cd %{_builddir}/source/rudder-commons && %{_sourcedir}/maven2/bin/mvn -s %{SOURCE3} -Dmaven.test.skip=true install
cd %{_builddir}/source/scala-ldap && %{_sourcedir}/maven2/bin/mvn -s %{SOURCE3} -Dmaven.test.skip=true install
cd %{_builddir}/source/ldap-inventory && %{_sourcedir}/maven2/bin/mvn -s %{SOURCE3} -Dmaven.test.skip=true install
cd %{_builddir}/source/cf-clerk && %{_sourcedir}/maven2/bin/mvn -s %{SOURCE3} -Dmaven.test.skip=true install
cd %{_builddir}/source/rudder && %{_sourcedir}/maven2/bin/mvn -s %{SOURCE3} -Dmaven.test.skip=true install package

# Installation
#=================================================
%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{rudderdir}/etc/
mkdir -p %{buildroot}%{rudderdir}/etc/plugins/
mkdir -p %{buildroot}%{rudderdir}/bin/
mkdir -p %{buildroot}%{rudderdir}/jetty7/webapps/
mkdir -p %{buildroot}%{rudderdir}/jetty7/contexts/
mkdir -p %{buildroot}%{rudderdir}/jetty7/rudder-plugins/
mkdir -p %{buildroot}%{rudderdir}/share/tools
mkdir -p %{buildroot}%{rudderdir}/share/plugins/
mkdir -p %{buildroot}%{ruddervardir}/inventories/incoming
mkdir -p %{buildroot}%{ruddervardir}/inventories/received
mkdir -p %{buildroot}%{rudderlogdir}/apache2/
mkdir -p %{buildroot}/etc/apache2/vhosts.d/
mkdir -p %{buildroot}/etc/sysconfig/

cp %{SOURCE1} %{buildroot}%{rudderdir}/etc/
cp %{_sourcedir}/source/rudder/rudder-core/src/main/resources/ldap/bootstrap.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/source/rudder/rudder-core/src/main/resources/ldap/init-policy-server.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/source/rudder/rudder-core/src/main/resources/ldap/demo-data.ldif %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/source/rudder/rudder-web/src/main/resources/configuration.properties %{buildroot}%{rudderdir}/etc/rudder-web.properties
cp %{_sourcedir}/source/rudder/rudder-web/src/main/resources/logback.xml %{buildroot}%{rudderdir}/etc/

cp %{_builddir}/source/rudder/rudder-web/target/rudder-web*.war %{buildroot}%{rudderdir}/jetty7/webapps/rudder.war

cp -rf %{_sourcedir}/source/rudder/rudder-web/src/main/resources/load-page %{buildroot}%{rudderdir}/share/
cp %{_sourcedir}/source/rudder/rudder-core/src/test/resources/script/cfe-red-button.sh %{buildroot}%{rudderdir}/bin/
cp %{_sourcedir}/source/rudder/rudder-core/src/main/resources/reportsInfo.xml %{buildroot}%{rudderdir}/etc/
cp %{_sourcedir}/source/rudder/rudder-web/src/main/resources/apache2-default.conf %{buildroot}/etc/apache2/vhosts.d/rudder-default.conf
cp %{_sourcedir}/source/rudder/rudder-web/src/main/resources/apache2-sysconfig %{buildroot}/etc/sysconfig/rudder-apache
cp %{SOURCE2} %{buildroot}%{rudderdir}/jetty7/contexts/

%pre -n rudder-webapp
#=================================================
# Pre Installation
#=================================================

%post -n rudder-webapp
#=================================================
# Post Installation
#=================================================

# Variables
VAR_RUDDER="/var/rudder"
PT_DIR="${VAR_RUDDER}/configuration-repository/policy-templates"

echo "Setting apache2 as a boot service"
/sbin/chkconfig --add apache2

echo "Reloading syslogd ..."
/etc/init.d/syslog reload

/etc/init.d/apache2 stop
# a2dissite default

# Do this ONLY at first install
if [ $1 -eq 1 ]
then
		echo -e '# This sources the Rudder needed by Rudder\n. /etc/sysconfig/rudder-apache' >> /etc/sysconfig/apache2
		echo 'DAVLockDB /tmp/davlock.db' >> /etc/apache2/conf.d/dav_mod.conf

		mkdir -p /var/rudder/configuration-repository
		mkdir -p /var/rudder/configuration-repository/shared-files
		touch /var/rudder/configuration-repository/shared-files/.placeholder
		cp -a /opt/rudder/share/policy-templates /var/rudder/configuration-repository/
fi

# Update /etc/sysconfig/apache2 in case an old module loading entry has already been created by Rudder
if grep -q 'APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http' /etc/sysconfig/apache2
then
	echo "Upgrading the /etc/sysconfig/apache2 file, Rudder needed modules for Apache are now listed in /etc/sysconfig/rudder-apache"
	sed -i 's%APACHE_MODULES="${APACHE_MODULES} rewrite dav dav_fs proxy proxy_http.*%# This sources the Rudder needed by Rudder\n. /etc/sysconfig/rudder-apache%' /etc/sysconfig/apache2
fi

# Add right to apache user to access /var/rudder/inventories/incoming
chmod 751 /var/rudder/inventories
chown root:www %{ruddervardir}/inventories/incoming
chmod 2770 %{ruddervardir}/inventories/incoming
chmod 755 -R %{rudderdir}/share/tools
chmod 655 -R %{rudderdir}/share/load-page
htpasswd2 -bc %{rudderdir}/etc/htpasswd-webdav rudder rudder
/etc/init.d/apache2 restart

# Migrate from 2.3.0 format policy-template store: /var/rudder/policy-templates
if [ -d /var/rudder/policy-templates -a ! -d /var/rudder/configuration-repository ]; then
	echo "***** WARNING *****"
	echo "The policy template store for Rudder has changed. It will be"
	echo "automatically moved from /var/rudder/policy-templates to"
	echo "/var/rudder/configuration-repository/policy-templates."

	cd /var/rudder/policy-templates && git add . && git add -u && git commit -am "Committing all pending policy template changes for automatic migration of the policy template store to /var/rudder/configuration-repository/policy-templates" || true

	mkdir -p /var/rudder/configuration-repository
	mv /var/rudder/policy-templates/.git /var/rudder/configuration-repository/
	mv /var/rudder/policy-templates /var/rudder/configuration-repository/
	cd /var/rudder/configuration-repository/ && git add -u
	cd /var/rudder/configuration-repository/ && git add policy-templates/
	cd /var/rudder/configuration-repository/ && git commit -m "Move policy-templates into configuration-repository directory"

	sed -i 's%^rudder.dir.policyPackages *= */var/rudder/policy-templates/\?$%rudder.dir.policyPackages=/var/rudder/configuration-repository/policy-templates%' /opt/rudder/etc/rudder-web.properties
	echo "rudder.dir.gitRoot=/var/rudder/configuration-repository" >> /opt/rudder/etc/rudder-web.properties

	echo "Automatic migration to /var/rudder/configuration-repository/policy-templates done."
fi

# Check default folder for shared-files exists
if [ ! -d /var/rudder/configuration-repository/shared-files ]; then
	echo "/var/rudder/configuration-repository/shared-files doesn't exist !"
	mkdir -p /var/rudder/configuration-repository/shared-files
	# If this folder doesn't contain files, git won't commit it
	# To simplify usage, we want that the user can add files simply
	# So when he will add files into shared-files they will appears in git status
	# So we force git to add the folder
	CONTENT=`ls /var/rudder/configuration-repository/shared-files/ | wc -l`
	if [ ${CONTENT} -eq 0 ]; then
		touch /var/rudder/configuration-repository/shared-files/.placeholder
		# Check if git init has been made, if not rudder will do it so we don't have to
		if [ -d /var/rudder/configuration-repository/.git ]; then
			cd /var/rudder/configuration-repository/ && git add shared-files/
			cd /var/rudder/configuration-repository/ && git commit -m "Add default shared-files directory" shared-files/
		fi
	fi
	echo "/var/rudder/configuration-repository/shared-files created"
fi
# Check shared-files folder is set in rudder-web.properties
ATTRIBUTESET=`grep "^rudder.dir.shared.files.folder" /opt/rudder/etc/rudder-web.properties | wc -l`
if [ ${ATTRIBUTESET} -gt 0 ]; then
	#Idea: when we will be asking for shared files folder path, sed will be used here
	echo "rudder.dir.shared.files.folder attribute already set in rudder-web.properties"
else
	echo "rudder.dir.shared.files.folder=/var/rudder/configuration-repository/shared-files" >> /opt/rudder/etc/rudder-web.properties
	echo "rudder.dir.shared.files.folder attribute set in rudder-web.properties"
fi

# Migration of PT 'Set the permissions of files' (Ensure that all actions below won't happen if migration has already made)
if [ ! -f ${PT_DIR}/fileConfiguration/fileSecurity/filesPermissions/1.0/policy.xml -a -f ${PT_DIR}/fileConfiguration/security/filesPermissions/1.0/policy.xml ]; then
    ## Commit all modifications before migration
    cd ${PT_DIR} && git add . && git add -u && git commit -am "Committing all pending policy template changes for automatic migration of the policy template from ${PT_DIR}/fileConfiguration/security/ to ${PT_DIR}/fileConfiguration/fileSecurity/" || true
  ## Create right folder if it doesn't exist
  if [ ! -d ${PT_DIR}/fileConfiguration/fileSecurity/ ]; then
    mkdir -p "${PT_DIR}/fileConfiguration/fileSecurity"
    echo "${PT_DIR}/fileConfiguration/fileSecurity has been created"
  else
    echo "${PT_DIR}/fileConfiguration/fileSecurity already exists"
  fi

  if [ -d ${PT_DIR}/fileConfiguration/security/ ]; then
    ## Check that filePermissions.st located in fileConfiguration/security/ is not duplicated and in the right folder
    if [ -d ${PT_DIR}/fileConfiguration/security/filesPermissions/ ]; then
      echo "The Policy Template 'Set the permissions of files' is not correctly located"
      cd ${PT_DIR} && git mv fileConfiguration/security/* fileConfiguration/fileSecurity/
      cd ${PT_DIR} && git commit -m "Correct Policy Template 'Set the permissions of files' location"
      echo "The location of the Policy Template 'Set the permissions of files' is now correct"
    fi
    ## Remove the folder which should contain no more files or folder
    rm -rf ${PT_DIR}/fileConfiguration/security/ # Not using git since it can't manage folder without file
    echo  "${PT_DIR}/fileConfiguration/security/ has been removed"
  fi
fi

# Check that Rudder database is able to handle backslash
CHECK_BACKSLASH=$(su - postgres -c "psql -t -d rudder -c \"select '\\foo';\"" 2> /dev/null | grep "foo" | wc -l)
if [ ${CHECK_BACKSLASH} -ne 1 ]; then
  echo "Rudder database is not backslash compliant, then a modification will be made."
  su - postgres -c "psql -t -d rudder -c \"alter database rudder set standard_conforming_strings=true;\""
  echo "Done. PostgreSQL and Rudder will be restarted"
  /etc/init.d/postgresql restart
  /etc/init.d/jetty restart
fi

# Get LDAP credentials
if [ -f /opt/rudder/etc/rudder-web.properties -a ${LDAP_CREDENTIALS} -eq 2 ]; then
	LDAP_USER=$(grep -E "^ldap.authdn=" /opt/rudder/etc/rudder-web.properties |cut -d "=" -f 2-)
	LDAP_PASSWORD=$(grep -E "^ldap.authpw=" /opt/rudder/etc/rudder-web.properties |cut -d "=" -f 2-)
else
	echo "WARNING: LDAP properties are missing in /opt/rudder/etc/rudder-web.properties"
	if [ -f /opt/rudder/etc/openldap/slapd.conf ]; then
		LDAP_USER=$(grep "^rootdn" /opt/rudder/etc/openldap/slapd.conf | sed "s/\w*\s*['\"]\?\([^\"']*\)['\"]\?$/\1/")
		LDAP_PASSWORD=$(grep "^rootpw" /opt/rudder/etc/openldap/slapd.conf | sed "s/\w*\s*['\"]\?\([^\"']*\)['\"]\?$/\1/")
	else
		echo "ERROR: /opt/rudder/etc/openldap/slapd.conf doesn't exist"
		exit 1
	fi
fi


# Upgrade LDAP : convert cpuSpeed attributes to valid integers ( introduced in 2.4.0~beta2 update )
LDAP_CPUSPEED_IS_NOT_INTEGER=$(/opt/rudder/bin/ldapsearch -H ldap://localhost -x -w ${LDAP_PASSWORD} -D "${LDAP_USER}" -b cn=rudder-configuration -LLL "(cpuSpeed=*)" cpuSpeed |grep -E "^cpuSpeed: [0-9]+\.[0-9]+$"|wc -l)
if [ ${LDAP_CPUSPEED_IS_NOT_INTEGER} -ne 0 ]; then
	/opt/rudder/bin/ldapsearch -H ldap://localhost -x -w ${LDAP_PASSWORD} -D ${LDAP_USER} -b cn=rudder-configuration -LLL "(cpuSpeed=*)" cpuSpeed| \
	sed "s%\(cpuSpeed:.*\)%changetype: modify\nreplace: cpuSpeed\n\1%"| \
	sed "s%cpuSpeed: \(.*\)\..*%cpuSpeed: \1%g"| \
	/opt/rudder/bin/ldapmodify -H ldap://localhost -x -w ${LDAP_PASSWORD} -D ${LDAP_USER} >/dev/null 2>&1

	echo "Some cpuSpeed attributes were converted to integers"
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

%{rudderdir}/etc/
%config(noreplace) %{rudderdir}/etc/rudder-web.properties
%config(noreplace) %{rudderdir}/etc/rudder-users.xml
%config(noreplace) %{rudderdir}/etc/logback.xml
%{rudderdir}/bin/
%{rudderdir}/jetty7/webapps/
%{rudderdir}/jetty7/rudder-plugins/
%{rudderdir}/jetty7/contexts/rudder.xml
%{rudderdir}/share
%{ruddervardir}/inventories/incoming
%{ruddervardir}/inventories/received
%{rudderlogdir}/apache2/
/etc/apache2/vhosts.d/
%config(noreplace) /etc/apache2/vhosts.d/rudder-default.conf
%config(noreplace) /etc/sysconfig/rudder-apache

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 28 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
