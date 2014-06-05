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
Epoch: 0
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
Source7: check-rudder-agent
Source8: vzps.py
Source9: rudder-agent.sh
Source10: detect_os.sh
Source11: rudder-perl

# uuidgen doesn't exist on AIX, so we provide a simple shell compatible version
%if "%{?_os}" == "aix"
Source100: uuidgen
%endif

# We have PERL things in here. Do not try to outsmart me by adding dummy dependencies, you silly tool.
AutoReq: 0
AutoProv: 0

%if 0%{?rhel} == 4
Patch1: fix-missing-headers
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

#Generic requirement
BuildRequires: gcc openssl-devel bison flex pcre-devel
Requires: pcre openssl

# Specific requirements

## For EL and Fedora
%if 0%{?rhel} || 0%{?fedora}
BuildRequires: make byacc
Requires: crontabs
%endif

## For SLES
%if 0%{?sles_version}
Requires: cron
%endif

# dmiecode is provided in the "dmidecode" package on EL4+ and on kernel-utils
# on EL3
%if 0%{?rhel} && 0%{?rhel} >= 4
Requires: dmidecode
%endif

%if 0%{?rhel} && 0%{?rhel} < 4
Requires: kernel-utils
%endif

# dmidecode is provided by "dmidecode" too on Fedora platforms, but I'm adding
# another if block to prevent cluttering the conditions on the >= el4 one and
# prevent possible unwanted non-matches.
%if 0%{?fedora}
Requires: dmidecode
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

# Fedora 7 is the first known version to officially
# support TokyoCabinet in the official repositories
%if 0%{?fedora} && 0%{?fedora} >= 7
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

# AIX builds support TokyoCabinet via M. Perzl's
# packages.
# cf http://www.perzl.org/aix/
%if "%{?_os}" == "aix"
BuildRequires: tokyocabinet-devel
Requires: tokyocabinet
%define is_tokyocabinet_here true
%endif

%define install_command        install
%define cp_a_command           cp -a
%define fusioninventory_folder %{_sourcedir}/fusioninventory-agent

%if "%{?_os}" == "aix"
%define install_command        installbsd -c
%define cp_a_command           cp -hpPr
%define fusioninventory_folder %{_sourcedir}/fusioninventory-agent-2.3.6
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

%{_sourcedir}/perl-prepare.sh %{fusioninventory_folder}

# Ensure an appropriate environment for the compiler
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"

%if "%{is_tokyocabinet_here}" != "true"
# Remove all remaining files from temporary build folder before to compile tokyocabinet
rm -rf %{buildroot}
# Compile Tokyocabinet library and install it in /opt/rudder/lib
cd %{_sourcedir}/tokyocabinet-source
./configure --prefix=%{rudderdir}
make %{?_smp_mflags}
make install DESTDIR=%{buildroot}
%endif

# Prepare CFEngine build
cd %{_sourcedir}/cfengine-source

%if "%{is_tokyocabinet_here}" != "true"
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
%if "%{is_tokyocabinet_here}" == "true"
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

# Init script
# AIX does not use init scripts, instead we set up a subsystem in the post scriptlet below
%if "%{?_os}" != "aix"
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
%{install_command} -m 755 %{SOURCE1} %{buildroot}/etc/init.d/rudder-agent
%{install_command} -m 644 %{SOURCE2} %{buildroot}/etc/default/rudder-agent
%endif

# Cron
# AIX does not support cron.d
%if "%{?_os}" != "aix"
mkdir -p %{buildroot}/etc/cron.d
%{install_command} -m 644 %{SOURCE5} %{buildroot}/etc/cron.d/rudder-agent
%endif

# Initial promises
cp -r %{_sourcedir}/initial-promises %{buildroot}%{rudderdir}/share/

# Fusion
%{cp_a_command} %{_sourcedir}/perl-custom/opt/rudder/* %{buildroot}%{rudderdir}

# Wrapper script
%{install_command} -m 755 %{SOURCE3} %{buildroot}/opt/rudder/bin/run-inventory

# Install an empty uuid.hive file before generating an uuid
cp %{SOURCE4} %{buildroot}%{rudderdir}/etc/

# ld.so.conf.d is not supported on CentOS 3
%if "%{is_tokyocabinet_here}" != "true" && 0%{?rhel} != 3
# Install /etc/ld.so.conf.d/rudder.conf in order to use libraries
# contained in /opt/rudder/lib like tokyocabinet
mkdir -p %{buildroot}/etc/ld.so.conf.d
%{install_command} -m 644 %{SOURCE6} %{buildroot}/etc/ld.so.conf.d/rudder.conf
%endif

%{install_command} -m 755 %{SOURCE7} %{buildroot}/opt/rudder/bin/check-rudder-agent

%{install_command} -m 755 %{SOURCE8} %{buildroot}/opt/rudder/bin/vzps.py

%{install_command} -m 755 %{SOURCE11} %{buildroot}/opt/rudder/bin/rudder-perl

# Install a profile script to make cf-* part of the PATH
# AIX does not support profile.d and /etc/profile should not be modified, so we don't do this on AIX at all
%if "%{?_os}" != "aix"
mkdir -p %{buildroot}/etc/profile.d
%{install_command} -m 644 %{SOURCE9} %{buildroot}/etc/profile.d/rudder-agent.sh
%endif

# Install the uuidgen command on AIX
%if "%{?_os}" == "aix"
mkdir -p %{buildroot}%{rudderdir}/bin
%{install_command} -m 755 %{SOURCE100} %{buildroot}%{rudderdir}/bin/
%endif

# Build a list of files to include in this package for use in the %files section below
find %{buildroot}%{rudderdir} %{buildroot}%{ruddervardir} -type f -o -type l | sed "s,%{buildroot},," | sed "s,\.py$,\.py*," | grep -v "%{rudderdir}/etc/uuid.hive" | grep -v "%{ruddervardir}/cfengine-community/ppkeys" > %{_builddir}/file.list.%{name}

%pre -n rudder-agent
#=================================================
# Pre Installation
#=================================================

# Do this only during upgrade process
if [ $1 -eq 2 ];then
%if "%{?_os}" != "aix"
	# Keep a backup copy of Rudder agent init and cron files to prevent http://www.rudder-project.org/redmine/issues/3995
	mkdir -p /var/backups/rudder
	%{install_command} -m 755 /etc/init.d/rudder-agent /var/backups/rudder/rudder-agent.init-$(date +%Y%m%d) && echo "INFO: A back up copy of the /etc/init.d/rudder-agent has been created in /var/backups/rudder"
	%{install_command} -m 644 /etc/default/rudder-agent /var/backups/rudder/rudder-agent.default-$(date +%Y%m%d) && echo "INFO: A back up copy of the /etc/default/rudder-agent has been created in /var/backups/rudder"
	%{install_command} -m 644 /etc/cron.d/rudder-agent /var/backups/rudder/rudder-agent.cron-$(date +%Y%m%d) && echo "INFO: A back up copy of the /etc/cron.d/rudder-agent has been created in /var/backups/rudder"
%else
	echo "INFO: No init script / cron script backup necessary on AIX builds yet. Skipping..."
%endif
fi

%post -n rudder-agent
#=================================================
# Post Installation
#=================================================

# Ensure our PATH includes Rudder's bin dir (for uuidgen on AIX in particular)
export PATH=%{rudderdir}/bin/:$PATH

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
%if "%{?_os}" == "aix"
	/usr/bin/mkssys -s rudder-agent -p %{ruddervardir}/cfengine-community/bin/cf-execd -a "-F" -u root -S -n15 -f9 -R
	/usr/sbin/mkitab "rudder-agent:23456789:once:/usr/bin/startsrc -s rudder-agent"
	# No need to tell init to re-read /etc/inittab, it does it automatically every 60 seconds
%else
	/sbin/chkconfig --add rudder-agent
%endif
	%if 0%{?rhel} >= 6
	/sbin/chkconfig rudder-agent on
	%endif

	CFRUDDER_FIRST_INSTALL=1
fi

# Reload configuration of ldd if new configuration has been added
%if "%{is_tokyocabinet_here}" != "true" && 0%{?rhel} != 3
if [ -f /etc/ld.so.conf.d/rudder.conf ]; then
	ldconfig
fi
%endif

# Reload configuration of ldd if new configuration has been added,
# CentOS 3 style.
%if "%{is_tokyocabinet_here}" != "true" && 0%{?rhel} == 3
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

%if "%{?_os}" == "aix"
if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 ]; then /usr/bin/stopsrc -s rudder-agent; fi
%else
if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 -a -x /etc/init.d/rudder-agent ]; then /sbin/service rudder-agent stop; fi
%endif

# Copy CFEngine binaries
%{cp_a_command} -f /opt/rudder/bin/cf-* /var/rudder/cfengine-community/bin/
NB_COPIED_BINARIES=`ls -1 /var/rudder/cfengine-community/bin/ | wc -l`
if [ ${NB_COPIED_BINARIES} -gt 0 ];then echo "CFEngine binaries copied to workdir"; fi

# Copy initial promises if there aren't any already
if [ ! -e /var/rudder/cfengine-community/inputs/promises.cf ]
then
	cp -r /opt/rudder/share/initial-promises/* /var/rudder/cfengine-community/inputs
fi

# If the cf-promises validation fails, it means we have a broken set of promises (possibly a pre-2.8 set).
# Reset the initial promises so the server is able to send the agent a new set of correct ones.
RUDDER_UUID=`cat /opt/rudder/etc/uuid.hive 2>/dev/null || true`
if ! /var/rudder/cfengine-community/bin/cf-promises >/dev/null 2>&1 && [ "z${RUDDER_UUID}" != "zroot" ]
then
	rm -rf /var/rudder/cfengine-community/inputs/*
	%{cp_a_command} /opt/rudder/share/initial-promises/* /var/rudder/cfengine-community/inputs/
fi

# This fix is required for upgrades from 2.6 or earlier. Since we didn't support AIX on those versions,
# we don't need it. And it breaks on AIX because their "sed" doesn't have a "-i" option. Grrr.
%if "%{?_os}" != "aix"
# Migration to CFEngine 3.5: Correct a specific Technique that breaks the most recent CFEngine versions
if [ -f /var/rudder/cfengine-community/inputs/distributePolicy/1.0/passwordCheck.cf ]
then
	sed -i 's%^\(.*ALTER USER rudder WITH PASSWORD.*p.psql_password.*\)"",$%\1""%' /var/rudder/cfengine-community/inputs/distributePolicy/1.0/passwordCheck.cf
fi
%endif

# Remove the lock on CFEngine
if [ ${I_SET_THE_LOCK} -eq 1 ]; then
	rm -f /opt/rudder/etc/disable-agent
fi

# Restart daemons if we stopped them, otherwise not
if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 ]
then
	# Check if agent is disabled
	if [ ! -f /opt/rudder/etc/disable-agent ]
	then
		if [ -r /var/rudder/cfengine-community/inputs/failsafe.cf -o -r /var/rudder/cfengine-community/inputs/promises.cf ]
		then
%if "%{?_os}" == "aix"
			/usr/bin/startsrc -s rudder-agent
%else
			/sbin/service rudder-agent start
%endif
		fi
	else
		echo "********************************************************************************"
		echo "rudder-agent has been updated, but was not started as it is disabled."
		echo "To enable rudder agent, you have to remove disable file, and start rudder-agent:"
		echo "# rm -f /opt/rudder/etc/disable-agent"
%if "%{?_os}" == "aix"
		echo "# startsrc -s rudder-agent"
%else
		echo "# /sbin/service rudder-agent start"
%endif
		echo "********************************************************************************"
	fi
else
	echo "********************************************************************************"
	echo "rudder-agent has been installed (not started). This host can be a Rudder node."
	echo "To get started, configure your Rudder server's hostname and launch the agent:"
	echo "# echo 'rudder.server' > /var/rudder/cfengine-community/policy_server.dat"
%if "%{?_os}" == "aix"
	echo "# startsrc -s rudder-agent"
%else
	echo "# service rudder-agent start"
%endif
	echo "This node will then appear in the Rudder web interface under 'Accept new nodes'."
	echo "********************************************************************************"
fi

# Create a key if we don't have one yet
if [ ! -f /var/rudder/cfengine-community/ppkeys/localhost.priv ]
then
	echo "INFO: Creating keys for CFEngine agent..."
	/var/rudder/cfengine-community/bin/cf-key > /dev/null 2>&1
	echo "INFO: Created a new key for CFEngine agent in /var/rudder/cfengine-community/ppkeys/"
fi

%if "%{?_os}" != "aix"
# Add temporary cron for checking UUID. This cron is created in postinst
# in order to remove it later without complains of the package manager.
CHECK_RUDDER_AGENT_CRON=`grep "/opt/rudder/bin/check-rudder-agent" /etc/cron.d/rudder-agent | wc -l`
TMP_CRON=/etc/cron.d/rudder-agent-uuid
# Add it only if the default cron file does not call check-rudder-agent script
if [ ${CHECK_RUDDER_AGENT_CRON} -eq 0 ]; then
	if [ ! -f ${TMP_CRON} ]; then
		echo "0,5,10,15,20,25,30,35,40,45,50,55 * * * * root /opt/rudder/bin/check-rudder-agent" > ${TMP_CRON}
	fi
fi

# Vixie-cron and cronie (at least) expect specific permissions to be applied
# on /etc/cron.d entries, and will refuse to load executable files.
if [ -f ${TMP_CRON} ]; then
	chmod 644 ${TMP_CRON}
fi
%endif

# launch rudder agent check script, it will generate an UUID on first install or repair it if needed
/opt/rudder/bin/check-rudder-agent

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
%{cp_a_command} -f /var/rudder/cfengine-community/ppkeys/ /var/backups/rudder/ppkeys-$(date +%Y%m%d)
echo "INFO: A back up copy of the /var/rudder/cfengine-community/ppkeys has been created in /var/backups/rudder"


%postun -n rudder-agent
#=================================================
# Post Uninstallation
#=================================================

%if "%{?_os}" == "aix"
# AIX doesn't have a pidof command, let's define it
function pidof {
  # Yeah, "grep -v grep" is ugly, but we can't use the [u]nique trick on a variable
  ps -A | grep "$1" | grep -v grep | awk '{print $1}';
}
%endif

# Do it only during uninstallation
if [ $1 -eq 0 ]; then
  # Make sure that CFEngine is not running anymore
  for component in cf-agent cf-serverd cf-execd cf-monitord; do
    if pid=`pidof ${component}`; then
      kill -9 ${pid}
    fi
  done

%if "%{?_os}" != "aix"
  # Remove the cron script we create at installation to prevent mail
  # flooding, re-installation surprises, and general system garbage.
  rm -f /etc/cron.d/rudder-agent

  # Make sure that Rudder agent specific files have been removed
  rm -f /etc/init.d/rudder-agent
  rm -f /etc/default/rudder-agent
%endif

  # Remove UUID in any case
  rm -f /opt/rudder/etc/uuid.hive
fi

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}
rm -f %{_builddir}/file.list.%{name}

#=================================================
# Files
#=================================================
# Files from %{rudderdir} and %{ruddervardir} are automatically added via the -f option
%files -n rudder-agent -f %{_builddir}/file.list.%{name}
%defattr(-, root, root, 0755)
%config(noreplace) %{rudderdir}/etc/uuid.hive
%if "%{?_os}" != "aix"
/etc/profile.d/rudder-agent.sh
/etc/init.d/rudder-agent
/etc/default/rudder-agent
/etc/cron.d/rudder-agent
%endif
%attr(0600, -, -) %dir %{ruddervardir}/cfengine-community/ppkeys
%dir %{ruddervardir}/cfengine-community/bin
%dir %{ruddervardir}/cfengine-community/inputs
%dir %{ruddervardir}/tmp
%dir %{ruddervardir}/tools
%if "%{is_tokyocabinet_here}" != "true" && 0%{?rhel} != 3
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
