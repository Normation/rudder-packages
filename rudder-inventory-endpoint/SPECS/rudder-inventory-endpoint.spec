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

%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder

%define maven_settings settings-external.xml

%if 0%{?sles_version} 
%define sysloginitscript /etc/init.d/syslog
%endif
%if 0%{?el5} 
%define sysloginitscript /etc/init.d/syslog
%endif
%if 0%{?el6} 
%define sysloginitscript /etc/init.d/rsyslog
%endif

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - service to receive inventory data
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 1299256513
License: AGPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: inventory-web.properties

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

BuildRequires: jdk >= 1.6
Requires: rudder-jetty rudder-inventory-ldap

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
cd %{_builddir}/rudder-sources/rudder-parent-pom && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/rudder-commons && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/scala-ldap && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/ldap-inventory && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install
cd %{_builddir}/rudder-sources/ldap-inventory/inventory-provisioning-web && %{_sourcedir}/maven2/bin/mvn -s %{_sourcedir}/%{maven_settings} -Dmaven.test.skip=true install package

# Installation
#=================================================
%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/opt/rudder/jetty7/webapps/
mkdir -p %{buildroot}/opt/rudder/etc/

cp %{_builddir}/rudder-sources/ldap-inventory/inventory-provisioning-web/target/inventory-provisioning-web*.war %{buildroot}/opt/rudder/jetty7/webapps/endpoint.war
cp %{SOURCE1} %{buildroot}/opt/rudder/etc/

%pre -n rudder-inventory-endpoint
#=================================================
# Pre Installation
#=================================================

%post -n rudder-inventory-endpoint
#=================================================
# Post Installation
#=================================================

echo "Reloading syslogd ..."
%{sysloginitscript} reload

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
/opt/rudder/jetty7/webapps/
/opt/rudder/etc/
%config(noreplace) /opt/rudder/etc/inventory-web.properties

#=================================================
# Changelog
#=================================================
%changelog
* Thu Jul 28 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.3-alpha4-1
- Initial package
