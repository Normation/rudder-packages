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
# Specification file for rudder-cfengine-community
#
# Install Cfengine Community
#
# Copyright (C) 2011 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name        rudder-cfengine-community
%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - CFEngine server component
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 1299256513
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source2: cfengine-community.init
Source3: cfengine-community.default

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#Generic requirement
BuildRequires: gcc, openssl-devel, bison, flex, pcre-devel
Requires: pcre, openssl

#Specific requirement
%if 0%{?sles_version} == 11
BuildRequires: libdb-4_5-devel
Requires: libdb-4_5 pmtools
%endif
%if 0%{?sles_version} == 10
BuildRequires: db42-devel
Requires: db42 pmtools
%endif
%if 0%{?rhel_version}
Requires: dmidecode
%endif

%description
Rudder is an open source configuration management and audit solution.

This package contains CFEngine Community 3 and is used to install a Rudder
server, where it provides a policy server for managed nodes.

#=================================================
# Source preparation
#=================================================
%prep
# Nothing here

#=================================================
# Building
#=================================================
%build
cd %{_sourcedir}/cfengine-source

# Ensure an appropriate environment for the compiler
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"

./configure BERKELEY_DB_LIB=-ldb --build=%_target --prefix=%{rudderdir} --with-workdir=%{ruddervardir}/cfengine-community --enable-static=yes --enable-shared=no
make %{?_smp_mflags}

#=================================================
# Installation
#=================================================
%install
rm -rf %{buildroot}
cd %{_sourcedir}/cfengine-source
make install DESTDIR=%{buildroot} STRIP=""

# Directories
mkdir -p %{buildroot}%{rudderdir}
mkdir -p %{buildroot}%{rudderdir}/etc
mkdir -p %{buildroot}%{ruddervardir}/cfengine-community/bin
mkdir -p %{buildroot}%{ruddervardir}/cfengine-community/inputs

# Init script
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
install -m 755 %{SOURCE2} %{buildroot}/etc/init.d/cfengine-community
install -m 644 %{SOURCE3} %{buildroot}/etc/default/cfengine-community

%pre -n rudder-cfengine-community
#=================================================
# Pre Installation
#=================================================


%post -n rudder-cfengine-community
#=================================================
# Post Installation
#=================================================

CFRUDDER_FIRST_INSTALL=0

# Do this at first install
if [ $1 -eq 1 ]
then
	# Set cfengine-community as service
	/sbin/chkconfig --add cfengine-community

	CFRUDDER_FIRST_INSTALL=1
fi

# Copy new binaries to workdir, make sure daemons are stopped first
if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 -a -x /etc/init.d/cfengine-community ]; then /etc/init.d/cfengine-community stop; fi
cp -a %{rudderdir}/sbin/cf-* %{ruddervardir}/cfengine-community/bin/

# Restart daemons if we stopped them, otherwise not
if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 ]
  then
    /etc/init.d/cfengine-community start
  else
  echo "rudder-cfengine-community has been installed, but not started"
fi

# Create a key if we don't have one yet
if [ ! -f %{ruddervardir}/cfengine-community/ppkeys/localhost.priv ]
then
	%{ruddervardir}/cfengine-community/bin/cf-key
fi

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-cfengine-community
%defattr(-, root, root, 0755)
%{rudderdir}
%{ruddervardir}
/etc/init.d/cfengine-community
/etc/default/cfengine-community

#=================================================
# Changelog
#=================================================
%changelog
* Tue Aug 02 2011 - Nicolas Perron <nicolas.perron@normation.com> 2.3-alpha4-1
- Initial package
