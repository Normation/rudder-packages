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
# Specification file for rudder-agent
#
# Install CFEngine
# Install Rudder initial promises
# Generate a UUID
#
# Copyright (C) 2011 Normation
#=================================================

#=================================================
# Variables
#=================================================
%define real_name            rudder-agent

%define rudderdir            /opt/rudder
%define ruddervardir         /var/rudder
%define rudderlogdir         /var/log/rudder
# is_tokyocabinet_here checks if to build CFEngine we will need to build 
# Tokyocabinet or if a package already exists on the system.
# Default value is true in order to handle cases which are not caught below
%define is_tokyocabinet_here true

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - agent
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 1299256513
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: rudder-agent.init
Source2: rudder-agent.default
Source3: run-inventory
Source4: uuid.hive
Source5: rudder-agent.cron
# This file will contain path of /opt/rudder/lib for ld which will
# find there all necessary libraries for tokyocabinet.
Source6: rudder.conf

%if 0%{?rhel} == 4
Patch1: fix-missing-headers
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#Generic requirement
BuildRequires: gcc openssl-devel bison flex pcre-devel
Requires: pcre openssl

#Specific requirements
%if 0%{?rhel}
BuildRequires: make byacc
%endif

# dmiecode is provided in the "dmidecode" package on EL4+ and on kernel-utils
# on EL3
%if 0%{?rhel} && 0%{?rhel} >= 4
Requires: dmidecode
%endif

%if 0%{?rhel} && 0%{?rhel} < 4
Requires: kernel-utils
%endif

## Each tests of OS version comparison with "greater" or "lesser version than"
## need to test before if we compare the right OS.
%if 0%{?rhel} && 0%{?rhel} <= 5
BuildRequires: bzip2-devel zlib-devel
%define is_tokyocabinet_here false
%endif

%if 0%{?rhel} && 0%{?rhel} >= 6
BuildRequires: tokyocabinet-devel
Requires: tokyocabinet
%define is_tokyocabinet_here true
%endif

%if 0%{?sles_version} && 0%{?sles_version} >= 11
BuildRequires: libbz2-devel zlib-devel
Requires: pmtools
%define is_tokyocabinet_here false
%endif

## Contents of package 'libbz2-devel' in SLES 11 is included in the package of bzip2
## in SLES 10 which is on the system by default.
## cf http://linux.derkeiler.com/Mailing-Lists/SuSE/2003-11/2640.html
%if 0%{?sles_version} == 10
BuildRequires: zlib-devel
Requires: pmtools
%define is_tokyocabinet_here false
%endif

# Replaces rudder-cfengine-community since 2.4.0~beta3
Provides: rudder-cfengine-community
Obsoletes: rudder-cfengine-community

# We have PERL things in here. Do not try to outsmart me by adding dummy dependencies, you silly tool.
# Same for TokyoCabinet, don't require the libs when we bundle them in this package, duh.
AutoProv: 0
%global _use_internal_dependency_generator 0
%global __find_requires_orig %{__find_requires}
%define __find_requires %{_sourcedir}/filter-reqs.pl %{is_tokyocabinet_here} %{__find_requires_orig}
%global __find_provides_orig %{__find_provides}
%define __find_provides %{_sourcedir}/filter-reqs.pl %{is_tokyocabinet_here} %{__find_provides_orig}


%description
Rudder is an open source configuration management and audit solution.

This package contains the agent that must be installed on all nodes to be
managed by Rudder. It is based on two main components: CFEngine Community 3 and
FusionInventory.

#=================================================
# Source preparation
#=================================================
%prep
%if 0%{?rhel} == 4
%patch1 -p1
%endif

#=================================================
# Building
#=================================================
%build

cd %{_sourcedir}

%{_sourcedir}/perl-prepare.sh


# Ensure an appropriate environment for the compiler
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"

%if %{is_tokyocabinet_here} == "false"
# Remove all remaining files from temporary build folder before to compile tokyocabinet
rm -rf %{buildroot}
# Compile Tokyocabinet library and install it in /opt/rudder/lib
cd %{_sourcedir}/tokyocabinet-source
./configure --prefix=%{rudderdir}
make %{?_smp_mflags}
make install DESTDIR=%{buildroot}
%endif

# Prepare CFEngine 3.4.x build
cd %{_sourcedir}/cfengine-source
%if %{is_tokyocabinet_here} == "false"
## Define path of tokyocabinet if built before instead of being provided by the system.
%define tokyocabinet_arg "--with-tokyocabinet=%{buildroot}%{rudderdir}"
%else
%define tokyocabinet_arg ""
%endif
./configure --build=%_target --prefix=%{rudderdir} --with-workdir=%{ruddervardir}/cfengine-community --enable-static=yes --enable-shared=no %{tokyocabinet_arg}

make %{?_smp_mflags}

#=================================================
# Installation
#=================================================
%install
%if %{is_tokyocabinet_here} == "true"
# Remove all remaining files from temporary build folder since no actions should
# have been made before in this directory (if tokyocabinet has not been
# built).
# Besides, all actions should not have been made before macro 'install', so removing all 
# the files from %{buildroot} should be made at the begining of macro 'install'.
# Build of and embeded library (here, tokyocabinet)is an exception.
rm -rf %{buildroot}
%endif
cd %{_sourcedir}/cfengine-source
make install DESTDIR=%{buildroot} STRIP=""

# Directories
mkdir -p %{buildroot}%{rudderdir}
mkdir -p %{buildroot}%{rudderdir}/etc
mkdir -p %{buildroot}%{ruddervardir}/cfengine-community/bin
mkdir -p %{buildroot}%{ruddervardir}/cfengine-community/inputs
mkdir -p %{buildroot}%{ruddervardir}/tmp
mkdir -p %{buildroot}%{ruddervardir}/tools

# ld.so.conf.d is not supported on CentOS 3
%if 0%{?rhel} != 3
mkdir -p %{buildroot}/etc/ld.so.conf.d
%endif

# Init script
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
install -m 755 %{SOURCE1} %{buildroot}/etc/init.d/rudder-agent
install -m 644 %{SOURCE2} %{buildroot}/etc/default/rudder-agent

# Cron
mkdir -p %{buildroot}/etc/cron.d
install -m 644 %{SOURCE5} %{buildroot}/etc/cron.d/rudder-agent

# Initial promises
cp -a %{_sourcedir}/initial-promises %{buildroot}%{rudderdir}/share/

# Fusion
cp -a %{_sourcedir}/perl-custom/opt/rudder/* %{buildroot}%{rudderdir}

# Wrapper script
install -m 755 %{SOURCE3} %{buildroot}/opt/rudder/bin/run-inventory

# Install an empty uuid.hive file before generating an uuid
cp %{SOURCE4} %{buildroot}%{rudderdir}/etc/

%if %{is_tokyocabinet_here} == "false" && 0%{?rhel} != 3
# Install /etc/ld.so.conf.d/rudder.conf in order to use libraries
# contained in /opt/rudder/lib like tokyocabinet
install -m 644 %{SOURCE6} %{buildroot}/etc/ld.so.conf.d/rudder.conf
%endif

%pre -n rudder-agent
#=================================================
# Pre Installation
#=================================================

%post -n rudder-agent
#=================================================
# Post Installation
#=================================================

CFRUDDER_FIRST_INSTALL=0

echo "Making sure that the permissions on the CFEngine key directory are correct..."
if [ -d %{ruddervardir}/cfengine-community/ppkeys ]; then
chmod 700 %{ruddervardir}/cfengine-community/ppkeys
  if [ `ls %{ruddervardir}/cfengine-community/ppkeys | wc -l` -gt 0 ]; then
    chmod 600 %{ruddervardir}/cfengine-community/ppkeys/*
  fi
fi

# Do this at first install
if [ $1 -eq 1 ]
then
	# Set rudder-agent as service
	/sbin/chkconfig --add rudder-agent

	CFRUDDER_FIRST_INSTALL=1
fi

# Reload configuration of ldd if new configuration has been added
%if %{is_tokyocabinet_here} == "false" && 0%{?rhel} != 3
if [ -f /etc/ld.so.conf.d/rudder.conf ]; then
	ldconfig
fi
%endif

# Reload configuration of ldd if new configuration has been added,
# CentOS 3 style.
%if %{is_tokyocabinet_here} == "false" && 0%{?rhel} == 3
if [ ! `grep "/opt/rudder/lib" /etc/ld.so.conf` ]; then
	echo "/opt/rudder/lib" >> /etc/ld.so.conf
fi

# Reload the linker configuration
ldconfig
%endif

# Always do this

# Generate a UUID if we don't have one yet
if [ ! -e /opt/rudder/etc/uuid.hive ]
then
	uuidgen > /opt/rudder/etc/uuid.hive
else
	# UUID is valid only if it has been generetaed by uuidgen or if it is set to 'root' for policy server
	CHECK_UUID=`cat /opt/rudder/etc/uuid.hive | grep -E "^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}|root" | wc -l`
	# If the UUID is not valid, regenerate it
	if [ ${CHECK_UUID} -ne 1 ]
	then
		uuidgen > /opt/rudder/etc/uuid.hive
	fi
fi

# Copy new binaries to workdir, make sure daemons are stopped first

# Set a "lock" to avoid CFEngine being restarted during the upgrade process
I_SET_THE_LOCK=0
if [ ! -e /opt/rudder/etc/disable-agent ]; then
	I_SET_THE_LOCK=1
	touch /opt/rudder/etc/disable-agent
fi

if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 -a -x /etc/init.d/rudder-agent ]; then /sbin/service rudder-agent stop; fi

# Copy CFEngine binaries
cp -a /opt/rudder/bin/cf-* /var/rudder/cfengine-community/bin/
NB_COPIED_BINARIES=`ls -1 /var/rudder/cfengine-community/bin/ | wc -l`
if [ ${NB_COPIED_BINARIES} -gt 0 ];then echo "CFEngine binaries copied to workdir"; fi

# Copy initial promises if there aren't any already
if [ ! -e /var/rudder/cfengine-community/inputs/promises.cf ]
then
	cp -r /opt/rudder/share/initial-promises/* /var/rudder/cfengine-community/inputs
fi

# Remove the lock on CFEngine
if [ ${I_SET_THE_LOCK} -eq 1 ]; then
	rm -f /opt/rudder/etc/disable-agent
fi

# Restart daemons if we stopped them, otherwise not
if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 ]
then
	if [ -r /var/rudder/cfengine-community/inputs/failsafe.cf -o -r /var/rudder/cfengine-community/inputs/promises.cf ]
	then
		/sbin/service rudder-agent start
	fi
else
	echo "********************************************************************************"
	echo "rudder-agent has been installed (not started). This host can be a Rudder node."
	echo "To get started, configure your Rudder server's hostname and launch the agent:"
	echo "# echo 'rudder.server' > /var/rudder/cfengine-community/policy_server.dat"
	echo "# service rudder-agent start"
	echo "This node will then appear in the Rudder web interface under 'Accept new nodes'."
	echo "********************************************************************************"
fi

# Create a key if we don't have one yet
if [ ! -f /var/rudder/cfengine-community/ppkeys/localhost.priv ]
then
	echo -n "INFO: Creating keys for CFEngine agent..."
	/var/rudder/cfengine-community/bin/cf-key > /dev/null 2>&1
	echo " Done."
fi

# Generate a UUID if we don't have one yet
if [ ! -e /opt/rudder/etc/uuid.hive ]
then
	echo -n "INFO: Creating a new UUID for Rudder..."
	uuidgen > /opt/rudder/etc/uuid.hive
	echo " Done."
else
	# UUID is valid only if it has been generetaed by uuidgen or if it is set to 'root' for policy server
	CHECK_UUID=`cat /opt/rudder/etc/uuid.hive | grep -E "^[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}|root" | wc -l`
	# If the UUID is not valid, regenerate it
	if [ ${CHECK_UUID} -ne 1 ]
	then
		echo -n "INFO: Creating a new UUID for Rudder as the existing one is invalid..."
		uuidgen > /opt/rudder/etc/uuid.hive
		echo " Done."
	fi
fi

%preun -n rudder-agent
#=================================================
# Pre Uninstallation
#=================================================

# Do it during upgrade and uninstall
# Keep a backup copy of uuid.hive
mkdir -p /var/backups/rudder
cp -f /opt/rudder/etc/uuid.hive /var/backups/rudder/uuid-$(date +%Y%m%d).hive
echo "INFO: A back up copy of the /opt/rudder/etc/uuid.hive has been created in /var/backups/rudder"

# Keep a backup copy of CFEngine ppkeys
cp -af /var/rudder/cfengine-community/ppkeys/ /var/backups/rudder/ppkeys-$(date +%Y%m%d)
echo "INFO: A back up copy of the /var/rudder/cfengine-community/ppkeys has been created in /var/backups/rudder"


%postun -n rudder-agent
#=================================================
# Post Uninstallation
#=================================================

# Do it only during uninstallation
if [ $1 -eq 0 ]; then
  # Make sure that CFEngine is not running anymore
  for component in cf-agent cf-serverd cf-execd cf-monitord; do
    kill -9 `pidof ${component}`
  done

  # Remove the cron script we create at installation to prevent mail
  # flooding, re-installation surprises, and general system garbage.
  rm -f /etc/cron.d/rudder-agent

  # Make sure that Rudder agent specific files have been removed
  rm -f /etc/init.d/rudder-agent
  rm -f /etc/default/rudder-agent
  rm -f /opt/rudder/etc/uuid.hive
fi

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n rudder-agent
%defattr(-, root, root, 0755)
%{rudderdir}
%config(noreplace) %{rudderdir}/etc/uuid.hive
/etc/init.d/rudder-agent
/etc/default/rudder-agent
/etc/cron.d/rudder-agent
%{ruddervardir}
%attr(0600, -, -) %dir %{ruddervardir}/cfengine-community/ppkeys
%if %{is_tokyocabinet_here} == "false" && 0%{?rhel} != 3
%config(noreplace) /etc/ld.so.conf.d/rudder.conf
%endif

#=================================================
# Changelog
#=================================================
%changelog
* Fri Apr  27 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.2-beta1-2
- The packages now builds correctly on both x86 and x86_64 archs, and on EL4/CentOS 4.
* Tue Mar  1 2011 - Jonathan CLARKE <jonathan.clarke@normation.com> 2.2-beta1-1
- Release 2.2.beta1
* Fri Feb 25 2011 - Jonathan CLARKE <jonathan.clarke@normation.com> 2.2-beta0-4
- Fix bug in postinstall script - stop daemons before replacing them!
* Fri Feb 25 2011 - Jonathan CLARKE <jonathan.clarke@normation.com> 2.2-beta0-3
- Fix bug to get initial promises in RPM, using the right git branch
* Fri Feb 25 2011 - Jonathan CLARKE <jonathan.clarke@normation.com> 2.2-beta0-2
- Fix bug to get initial promises in RPM
* Fri Feb 25 2011 - Jonathan CLARKE <jonathan.clarke@normation.com> 2.2-beta0-1
- Initial package
