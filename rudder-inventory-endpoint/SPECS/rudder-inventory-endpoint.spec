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
# Specification file for rudder-inventory-endpoint
#
# Installs Rudder's inventory WAR files using
# Apache's maven
#
# Copyright (C) 2011 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-inventory-endpoint
%define real_epoch       0

%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder

%define maven_settings settings-external.xml

%if 0%{?suse_version}
%define syslogservicename syslog
%endif

%if 0%{?rhel} == 5 || 0%{?el5}
%define syslogservicename syslog
%endif

%if 0%{?rhel} && 0%{?rhel} > 5
%define syslogservicename rsyslog
%endif

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - service to receive inventory data
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: %{real_epoch}
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: inventory-web.properties
Source2: rudder-inventory-endpoint-upgrade
Source3: rudder-inventory-endpoint
Source4: endpoint.xml

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# Dependencies

Requires: rudder-inventory-ldap = %{real_epoch}:%{real_version}

# OS-specific dependencies

##
## Those jetty packages are virtual packages provided by our Jetty and the system one.
##

## 1 - RHEL
%if 0%{?rhel}
BuildRequires: java-1.8.0-openjdk-devel
%endif

%if 0%{?rhel}
Requires: jetty-eclipse
%endif

## 3 - SLES
## No Jetty provided by SLES... Use our own.
%if 0%{?suse_version}
BuildRequires: jdk >= 1.8
Requires: rudder-jetty = %{real_epoch}:%{real_version}
%endif

%description
Rudder is an open source configuration management and audit solution.

This package contains a webapp that listens for incoming inventory data from
nodes that have rudder-agent installed on them. The webapp is automatically
installed and started using the Jetty application server bundled in the
rudder-jetty package. It then updates the inventory database provided by
the rudder-inventory-ldap package.


#=================================================
# Source preparation
#=================================================
%prep

cp -rf %{_sourcedir}/rudder-sources %{_builddir}

#=================================================
# Building
#=================================================
%build

export MAVEN_OPTS=-Xmx512m

if [ -f %{_sourcedir}/endpoint.war ]
then
  cp %{_sourcedir}/endpoint.war %{_builddir}/endpoint.war
else
  cd %{_builddir}/rudder-sources/rudder-parent-pom && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
  cd %{_builddir}/rudder-sources/rudder-commons && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
  cd %{_builddir}/rudder-sources/scala-ldap && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
  cd %{_builddir}/rudder-sources/ldap-inventory && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
  cd %{_builddir}/rudder-sources/ldap-inventory/inventory-provisioning-web && %{_sourcedir}/maven/bin/mvn --batch-mode -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install package
  cp %{_builddir}/rudder-sources/ldap-inventory/inventory-provisioning-web/target/inventory-provisioning-web*.war %{_builddir}/endpoint.war
fi

# Installation
#=================================================
%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/opt/rudder/etc/
mkdir -p %{buildroot}/opt/rudder/etc/server-roles.d/
mkdir -p %{buildroot}%{rudderdir}/bin/
mkdir -p %{buildroot}/opt/rudder/share/webapps/

cp %{_builddir}/endpoint.war %{buildroot}/opt/rudder/share/webapps/endpoint.war
cp %{SOURCE1} %{buildroot}/opt/rudder/etc/
cp %{SOURCE2} %{buildroot}%{rudderdir}/bin/

install -m 644 %{SOURCE3} %{buildroot}/opt/rudder/etc/server-roles.d/

install -m 644 %{SOURCE4} %{buildroot}%{rudderdir}/share/webapps/

%pre -n rudder-inventory-endpoint
#=================================================
# Pre Installation
#=================================================

%post -n rudder-inventory-endpoint
#=================================================
# Post Installation
#=================================================

# Create a symlink to the Jetty context if necessary
if [ -d "%{rudderdir}/jetty7/contexts" ]; then
  ln -sf %{rudderdir}/share/webapps/endpoint.xml %{rudderdir}/jetty7/contexts/endpoint.xml
fi

# Run any upgrades
echo "INFO: Launching script to check if a migration is needed"
%{rudderdir}/bin/rudder-inventory-endpoint-upgrade
echo "INFO: End of migration script"

echo -n "INFO: Restarting syslogd ..."
%if 0%{?rhel} < 7
service %{syslogservicename} restart > /dev/null && echo " Done"
%endif
%if 0%{?rhel} >= 7
/bin/systemctl restart  %{syslogservicename}.service && echo " Done"
%endif


#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-inventory-endpoint
%defattr(-, root, root, 0755)
%{rudderdir}/share/webapps/
%{rudderdir}/bin/
%{rudderdir}/etc/
%config(noreplace) /opt/rudder/etc/inventory-web.properties

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 28 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
