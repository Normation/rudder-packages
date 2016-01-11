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
%define bindir               /usr/bin

# use_system_lmdb checks if to build CFEngine we will need to build LMDB or if
# a package already exists on the system.
# Default value is true in order to handle cases which are not caught below.
%define use_system_lmdb true

# Same goes for the use of the local OpenSSL install vs. a bundled one
%define use_system_openssl true

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
# find there all necessary libraries for LMDB.
Source6: rudder.conf
Source7: check-rudder-agent
Source8: vzps.py
Source9: rudder-agent.sh
Source10: detect_os.sh
Source11: rudder-perl
Source12: rudder-agent-utilities
Source13: rudder.init
Source14: signature.sh
Source15: rudder.8.gz

# uuidgen doesn't exist on AIX, so we provide a simple shell compatible version
%if "%{?_os}" == "aix"
Source100: uuidgen
%endif

# Prevent dependency auto-generation, that tries to be helpful by detecting Perl dependencies from
# FusionInventory. We handle that with the perl standalone installation already.
AutoReq: 0
AutoProv: 0

%if 0%{?rhel} && 0%{?rhel} == 4
Patch1: fix-missing-headers
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Generic requirements
BuildRequires: gcc bison flex pcre-devel autoconf automake libtool
Requires: pcre
Provides: rudder-agent
Conflicts: rudder-agent-thin

# Specific requirements

## For EL and Fedora
%if 0%{?rhel} || 0%{?fedora}
BuildRequires: make byacc
Requires: crontabs net-tools
%endif

## For SLES
%if 0%{?suse_version}
Requires: cron net-tools
%endif

# dmiecode is provided in the "dmidecode" package on EL4+ and on kernel-utils
# on EL3
%if 0%{?rhel} && 0%{?rhel} >= 4
Requires: dmidecode
%endif

%if 0%{?rhel} && 0%{?rhel} < 4
Requires: kernel-utils
%endif

# dmidecode is provided by "dmidecode" too on Fedora platforms, but I'm adding
# another if block to prevent cluttering the conditions on the >= el4 one and
# prevent possible unwanted non-matches.
%if 0%{?fedora}
Requires: dmidecode
%endif

# LMDB handling (builtin or OS-provided)

## 1 - RHEL: No LMDB yet
%if 0%{?rhel}
%define use_system_lmdb false
%endif

## 2 - Fedora: No LMDB yet
%if 0%{?fedora}
%define use_system_lmdb false
%endif

## 3 - SLES: No LMDB yet
%if 0%{?suse_version} && 0%{?suse_version} < 1315
Requires: pmtools
%define use_system_lmdb false
%endif

%if 0%{?suse_version} && 0%{?suse_version} >= 1315
Requires: dmidecode
%define use_system_lmdb false
%endif

## 4 - AIX: No LMDB yet
%if "%{?_os}" == "aix"
%define use_system_lmdb false
%endif

# OpenSSL handling (builtin or OS-provided)
#
# We build and use a bundled version of OpenSSL
# on OSes which are not maintained anymore as part
# of their "main" support phase.
#
# See. http://www.rudder-project.org/redmine/issues/5147

## 1 - RHEL: Bundled for pre-el5 oses
##
### Pre el5 have reached the end of production phase,
### and are thus in Extended Life phase.
### See. https://access.redhat.com/support/policy/updates/errata/
##
%if 0%{?rhel} && 0%{?rhel} < 5
%define use_system_openssl false
%endif

## 2 - Fedora: Use the system one
##
### We work with Fedora 18 onwards, it
### comes with OpenSSL 1.0.1e, which is
### recent enough.
##

## 3 - SLES: Bundled for pre-sles11 oses
##
### SLES 11 OSes come with OpenSSL 0.9.8h,
### which is recent enough.
### SLES12 has no sles_version defined, but openssl is ok too
##
%if 0%{?sles_version} && 0%{?sles_version} < 11
%define use_system_openssl false
%endif

## 4 - AIX: Bundled
##
### We do not want to rely on external
### implementations of OpenSSL on AIX to
### reduce dependencies on the base system.
##
%if "%{?_os}" == "aix"
%define use_system_openssl false
%endif

## 5 - Resulting dependencies
%if "%{use_system_openssl}" == "true"
BuildRequires: openssl-devel
Requires: openssl
%endif

# Common commands

%define install_command        install
%define cp_a_command           cp -a

%if "%{?_os}" == "aix"
%define install_command        installbsd -c
%define cp_a_command           cp -hpPr
%endif

# Replaces rudder-cfengine-community since 2.4.0~beta3
Provides: rudder-cfengine-community
Obsoletes: rudder-cfengine-community

# Use our own dependency generator
%global _use_internal_dependency_generator 0
%global __find_requires_orig %{__find_requires}
%define __find_requires %{_sourcedir}/filter-reqs.pl %{use_system_lmdb} %{__find_requires_orig}
%global __find_provides_orig %{__find_provides}
%define __find_provides %{_sourcedir}/filter-reqs.pl %{use_system_lmdb} %{__find_provides_orig}

%description
Rudder is an open source configuration management and audit solution.

This package contains the agent that must be installed on all nodes to be
managed by Rudder. It is based on two main components: CFEngine Community 3 and
FusionInventory.

#=================================================
# Source preparation
#=================================================
%prep
%if 0%{?rhel} && 0%{?rhel} == 4
%patch1 -p1
%endif

#=================================================
# Building
#=================================================
%build

cd %{_sourcedir}

%{_sourcedir}/perl-prepare.sh %{_sourcedir}/fusioninventory-agent

# Ensure an appropriate environment for the compiler
export CFLAGS="${RPM_OPT_FLAGS}"
export CXXFLAGS="${RPM_OPT_FLAGS}"

%if "%{use_system_openssl}" != "true"
# Compile and install OpenSSL
cd %{_sourcedir}/openssl-source
./config -fPIC --prefix=%{rudderdir} --openssldir=%{rudderdir}/openssl shared
make %{?_smp_mflags}
%if "%{?_os}" == "aix"
slibclean
%endif
make install
%endif

%if "%{use_system_lmdb}" != "true"
# Remove all remaining files from the temporary build folder before compiling LMDB
rm -rf %{buildroot}

# Compile LMDB library and install it in /opt/rudder/lib

# LMDB's Makefile does not know how to create destination files, do it ourselves
for i in bin lib include man/man1; do mkdir -p %{rudderdir}/$i; done

cd %{_sourcedir}/lmdb-source/libraries/liblmdb

make %{?_smp_mflags}

# First install goes to the local %{rudderdir} to prevent linking issues during
# CFEngine build
make install prefix=%{rudderdir}
%endif

# Prepare CFEngine build
cd %{_sourcedir}/cfengine-source

%if "%{use_system_openssl}" != "true"
## Define path of OpenSSL if built before instead of being provided by the system.
%define openssl_arg "--with-openssl=%{rudderdir}"
%else
%define openssl_arg ""
%endif

%if "%{use_system_lmdb}" != "true"
## Define path of LMDB if built before instead of being provided by the system.
%define lmdb_arg "--with-lmdb=%{rudderdir}"
%else
%define lmdb_arg ""
%endif

# If there is no configure, bootstrap with autogen.sh first
if [ ! -x ./configure ]; then
  NO_CONFIGURE=1 ./autogen.sh
fi

# Test if compiler support hardening flags
TRY_LDFLAGS="-pie -Wl,-z,relro -Wl,-z,now"
TRY_CFLAGS="-fPIE -fstack-protector"

FLAG_TEST_FILE=`mktemp /tmp/hardening.XXXXXX`
echo "void main() {}" > "${FLAG_TEST_FILE}.c"
if gcc ${TRY_CFLAGS} ${TRY_LDFLAGS} -o "${FLAG_TEST_FILE}" "${FLAG_TEST_FILE}.c" >/dev/null 2>&1
then
  SECURE_CFLAGS="${TRY_CFLAGS}"
  SECURE_LDFLAGS="${TRY_LDFLAGS}"
fi
rm -f "${FLAG_TEST_FILE}" "${FLAG_TEST_FILE}.c"

./configure --build=%_target --prefix=%{rudderdir} --with-workdir=%{ruddervardir}/cfengine-community --enable-static=yes --enable-shared=no %{openssl_arg} %{lmdb_arg} CFLAGS="${CFLAGS} ${SECURE_CFLAGS}" LDFLAGS="${SECURE_LDFLAGS}"

make %{?_smp_mflags}

#=================================================
# Installation
#=================================================
%install
%if "%{use_system_lmdb}" == "true"
# Remove all remaining files from temporary build folder since no actions should
# have been made before in this directory (if LMDB has not been built).
# Besides, all actions should not have been made before macro 'install', so removing all 
# the files from %{buildroot} should be made at the begining of macro 'install'.
# Build of and embedded library (here, LMDB) is an exception.
rm -rf %{buildroot}
%else

# Reinstall LMDB because RPM rm -rf %{buildroot} for a reason I don't understand
# TODO: Fix this nasty hack!

# LMDB's Makefile does not know how to create destination files, do it ourselves
for i in bin lib include man/man1; do mkdir -p %{buildroot}%{rudderdir}/$i; done
cd %{_sourcedir}/lmdb-source/libraries/liblmdb

# Now, we install lmdb in %{buildroot} to package it
make install prefix=%{rudderdir} DESTDIR=%{buildroot}
%endif

%if "%{use_system_openssl}" != "true"
cd %{_sourcedir}/openssl-source
make install INSTALL_PREFIX=%{buildroot}
%endif

# Directories
mkdir -p %{buildroot}%{rudderdir}
mkdir -p %{buildroot}%{rudderdir}/share/man/man8
mkdir -p %{buildroot}%{rudderdir}/etc
mkdir -p %{buildroot}%{rudderdir}/share
mkdir -p %{buildroot}%{rudderdir}/share/commands
mkdir -p %{buildroot}%{ruddervardir}/cfengine-community/bin
mkdir -p %{buildroot}%{ruddervardir}/cfengine-community/inputs
mkdir -p %{buildroot}%{ruddervardir}/tmp
mkdir -p %{buildroot}%{ruddervardir}/tools
mkdir -p %{buildroot}%{rudderlogdir}/install
mkdir -p %{buildroot}%{bindir}

cd %{_sourcedir}/cfengine-source

# CFEngine installation
make install DESTDIR=%{buildroot} STRIP=""

# CFEngine man pages
for binary in cf-agent cf-promises cf-key cf-execd cf-serverd cf-monitord cf-runagent
do
  LD_LIBRARY_PATH="%{buildroot}%{rudderdir}/lib" ${binary}/${binary} -M | gzip > %{buildroot}%{rudderdir}/share/man/man8/${binary}.8.gz
done

# Init script
# AIX does not use init scripts, instead we set up a subsystem in the post scriptlet below
%if "%{?_os}" != "aix"
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
%{install_command} -m 755 %{SOURCE1} %{buildroot}/etc/init.d/rudder-agent
%{install_command} -m 644 %{SOURCE2} %{buildroot}/etc/default/rudder-agent
%{install_command} -m 755 %{SOURCE13} %{buildroot}/etc/init.d/rudder
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

# Signature script
%{install_command} -m 755 %{SOURCE14} %{buildroot}/opt/rudder/bin/signature.sh

# Install an empty uuid.hive file before generating an uuid
cp %{SOURCE4} %{buildroot}%{rudderdir}/etc/

%if 0%{?rhel} != 3 && "%{?_os}" != "aix"
# Install /etc/ld.so.conf.d/rudder.conf in order to use libraries
# contained in /opt/rudder/lib like LMDB or OpenSSL
# (ld.so.conf.d is not supported on RHEL/CentOS 3 and aix)
mkdir -p %{buildroot}/etc/ld.so.conf.d
%{install_command} -m 644 %{SOURCE6} %{buildroot}/etc/ld.so.conf.d/rudder.conf

%endif

%{install_command} -m 755 %{SOURCE7} %{buildroot}/opt/rudder/bin/check-rudder-agent

%{install_command} -m 755 %{SOURCE8} %{buildroot}/opt/rudder/bin/vzps.py

%{install_command} -m 755 %{SOURCE11} %{buildroot}/opt/rudder/bin/rudder-perl

# Rudder agent utilities
%{install_command} -m 755 %{SOURCE12}/bin/rudder %{buildroot}%{rudderdir}/bin/rudder
%{cp_a_command} %{SOURCE12}/share/commands/* %{buildroot}%{rudderdir}/share/commands/

# Rudder agent command manual
%{install_command} -m 644 %{SOURCE15} %{buildroot}%{rudderdir}/share/man/man8/rudder.8.gz

# Create a symlink to make "rudder" available as part of the
# default PATH
ln -sf %{rudderdir}/bin/rudder %{buildroot}%{bindir}/rudder

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
  # Keep a backup copy of Rudder agent init and cron files to prevent http://www.rudder-project.org/redmine/issues/3995
  for i in init.d default cron.d; do
    if [ -f /etc/${i}/rudder-agent ]; then
      mkdir -p /var/backups/rudder
      if [ "${i}" = "init.d" ]; then mode=755; else mode=644; fi
      %{install_command} -m ${mode} /etc/${i}/rudder-agent /var/backups/rudder/rudder-agent.$(basename ${i} .d)-$(date +%Y%m%d) && echo "INFO: A back up copy of /etc/${i}/rudder-agent has been created in /var/backups/rudder"
    fi
  done
%else
  echo "INFO: No init script / cron script backup necessary on AIX builds yet. Skipping..."
%endif
fi

%post -n rudder-agent
#=================================================
# Post Installation
#=================================================

echo "$(date) - Starting rudder-agent post installation script" >> %{rudderlogdir}/install/rudder-agent.log

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
  RUDDER_AGENT_INIT_ENABLED=$(LANG=C chkconfig --list 2>/dev/null | grep -Ec "rudder-agent.*on")

  if [ "${RUDDER_AGENT_INIT_ENABLED}" -ne 0 ]
  then
    chkconfig --del rudder-agent
  fi
  chkconfig --add rudder
%endif
%if 0%{?rhel} && 0%{?rhel} >= 6
  if [ "${RUDDER_AGENT_INIT_ENABLED}" -ne 0 ]
  then
    chkconfig rudder-agent off
  fi
  chkconfig rudder on
%endif
  CFRUDDER_FIRST_INSTALL=1
fi

%if 0%{?rhel} != 3 && "%{?_os}" != "aix"
# Reload ld.so configuration if rudder.conf is present
if [ -f /etc/ld.so.conf.d/rudder.conf ]; then
  ldconfig
fi
%endif

%if "%{?rhel}" == "3"
# Update and reload ld.so configuration if needed, RHEL/CentOS 3 style.
if ! grep -q "/opt/rudder/lib" /etc/ld.so.conf; then
  echo "/opt/rudder/lib" >> /etc/ld.so.conf
  ldconfig
fi
%endif

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
if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 -a -x /etc/init.d/rudder-agent ]; then service rudder-agent stop || service rudder-agent forcestop; fi
%endif

%if "%{?_os}" == "aix"
# On AIX, trigger slibclean to remove any unused library/binary object from memory
# Will prevent "Text file busy" errors during the following copy
slibclean
%endif

# Copy CFEngine binaries
%{cp_a_command} -f /opt/rudder/bin/cf-* /var/rudder/cfengine-community/bin/
%{cp_a_command} -f /opt/rudder/bin/rpmvercmp /var/rudder/cfengine-community/bin/
NB_COPIED_BINARIES=`ls -1 /var/rudder/cfengine-community/bin/ | wc -l`
if [ ${NB_COPIED_BINARIES} -gt 0 ];then echo "CFEngine binaries copied to workdir"; fi

# Set up initial promises if necessary

# Backup rudder-server-roles.conf
if [ -e /var/rudder/cfengine-community/inputs/rudder-server-roles.conf ]
then
  mkdir -p /var/backups/rudder
  %{cp_a_command} /var/rudder/cfengine-community/inputs/rudder-server-roles.conf /var/backups/rudder/
  RESTORE_SERVER_ROLES_BACKUP=1
fi

# Copy initial promises if there aren't any already or,
# if the cf-promises validation fails, it means we have a broken set of promises (possibly a pre-2.8 set).
# Reset the initial promises so the server is able to send the agent a new set of correct ones.
RUDDER_UUID=$(cat /opt/rudder/etc/uuid.hive 2>/dev/null || true)
if [ ! -e /var/rudder/cfengine-community/inputs/promises.cf ] || ! /var/rudder/cfengine-community/bin/cf-promises >/dev/null 2>&1 && [ "z${RUDDER_UUID}" != "zroot" ]
then
  rm -rf /var/rudder/cfengine-community/inputs/* || true
  %{cp_a_command} /opt/rudder/share/initial-promises/* /var/rudder/cfengine-community/inputs/
fi

# Restore rudder-server-roles.conf if necessary
if [ "z${RESTORE_SERVER_ROLES_BACKUP}" = "z1" ]; then
  %{cp_a_command} /var/backups/rudder/rudder-server-roles.conf /var/rudder/cfengine-community/inputs/rudder-server-roles.conf
fi

# This fix is required for upgrades from 2.6 or earlier. Since we didn't support AIX on those versions,
# we don't need it. And it breaks on AIX because their "sed" doesn't have a "-i" option. Grrr.
%if "%{?_os}" != "aix"
# Migration to CFEngine 3.5: Correct a specific Technique that breaks the most recent CFEngine versions
if [ -f /var/rudder/cfengine-community/inputs/distributePolicy/1.0/passwordCheck.cf ]
then
  sed -i 's%^\(.*ALTER USER rudder WITH PASSWORD.*p.psql_password.*\)"",$%\1""%' /var/rudder/cfengine-community/inputs/distributePolicy/1.0/passwordCheck.cf
fi
%endif

# Remove the lock on CFEngine
if [ ${I_SET_THE_LOCK} -eq 1 ]; then
  rm -f /opt/rudder/etc/disable-agent
fi

# Remove cfengine lock log file : http://www.rudder-project.org/redmine/issues/5488
rm -f /var/rudder/cfengine-community/cf3.*.runlog*

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
      /sbin/service rudder-agent start || true
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
  /var/rudder/cfengine-community/bin/cf-key >> %{rudderlogdir}/install/rudder-agent.log 2>&1
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

# Vixie-cron and cronie (at least) expect specific permissions to be applied
# on /etc/cron.d entries, and will refuse to load executable files.
if [ -f ${TMP_CRON} ]; then
  chmod 644 ${TMP_CRON}
fi
%endif

# Try to send an inventory after upgrade to see the new agent version on the server
if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 ]
then
  echo "INFO: Trigger an inventory..."
  /opt/rudder/bin/rudder agent inventory >> %{rudderlogdir}/install/rudder-agent.log 2>&1
fi

# launch rudder agent check script, it will generate an UUID on first install or repair it if needed
nohup /opt/rudder/bin/check-rudder-agent >/dev/null 2>/dev/null &

%preun -n rudder-agent
#=================================================
# Pre Uninstallation
#=================================================

# Do it during upgrade and uninstall

# Keep a backup copy of uuid.hive
if [ -f /opt/rudder/etc/uuid.hive ]; then
  mkdir -p /var/backups/rudder
  cp -f /opt/rudder/etc/uuid.hive /var/backups/rudder/uuid-$(date +%Y%m%d).hive
  echo "INFO: A back up copy of the /opt/rudder/etc/uuid.hive has been created in /var/backups/rudder"
fi

# Keep a backup copy of CFEngine ppkeys
if [ -d /var/rudder/cfengine-community/ppkeys/ ]; then
  mkdir -p /var/backups/rudder
  %{cp_a_command} -f /var/rudder/cfengine-community/ppkeys/ /var/backups/rudder/ppkeys-$(date +%Y%m%d)
  echo "INFO: A back up copy of the /var/rudder/cfengine-community/ppkeys has been created in /var/backups/rudder"
fi


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
  # Make sure that CFEngine is not running anymore
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
  rm -f /etc/init.d/rudder
  rm -f /etc/init.d/rudder-agent
  rm -f /etc/default/rudder-agent
%else
  # Remove the AIX inittab entry and subsystem definition
  rmssys -s rudder-agent
  rmitab rudder-agent
%endif

  # Remove UUID in any case
  rm -f /opt/rudder/etc/uuid.hive
  rm -f %{ruddervardir}/cfengine-community/policy_server.dat
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

%{bindir}/rudder

# The following file is declared to belong to this package but will not be installed
# This is because it is populated during post-inst scriptlet
# This is not reflected in debian packaging, because dpkg will never replace an
# existing file declared in conffiles
%ghost %{rudderdir}/etc/uuid.hive

%if "%{?_os}" != "aix"
/etc/profile.d/rudder-agent.sh
/etc/init.d/rudder-agent
/etc/default/rudder-agent
/etc/init.d/rudder
/etc/cron.d/rudder-agent
%endif

%attr(0600, -, -) %dir %{ruddervardir}/cfengine-community/ppkeys
%dir %{ruddervardir}/cfengine-community/bin
%dir %{ruddervardir}/cfengine-community/inputs
%dir %{ruddervardir}/tmp
%dir %{ruddervardir}/tools
%dir %{rudderlogdir}/install

%if 0%{?rhel} != 3 && "%{?_os}" != "aix"
%config(noreplace) /etc/ld.so.conf.d/rudder.conf
%endif

#=================================================
# Changelog
#=================================================
%changelog
* Wed Apr  27 2011 - Matthieu CERDA <matthieu.cerda@normation.com> 2.2-beta1-2
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
