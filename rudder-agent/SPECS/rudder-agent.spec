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

Source1: Makefile
Source2: check-rudder-agent
Source3: filter-reqs.pl
Source4: perl-prepare.sh
Source5: rudder-agent.default
Source6: rudder-agent.init
Source7: rudder-agent.sh
Source8: rudder-perl
Source9: rudder.conf
Source10: rudder.init
Source11: run-inventory
Source12: signature.sh
Source13: uuid.hive
Source14: uuidgen
Source15: vzps.py

# Prevent dependency auto-generation, that tries to be helpful by detecting Perl dependencies from
# FusionInventory. We handle that with the perl standalone installation already.
AutoReq: 0
AutoProv: 0

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

#=================================================
# Building
#=================================================
%build

cd %{_sourcedir}

# Ensure an appropriate environment for the compiler
export CFLAGS="${RPM_OPT_FLAGS}"
export CXXFLAGS="${RPM_OPT_FLAGS}"

make %{?_smp_mflags} USE_SYSTEM_OPENSSL=%{use_system_openssl} USE_SYSTEM_LMDB=%{use_system_lmdb}

# there was a slibclean here on aix
# TODO, check that it is not necessary anymore since we no more do a make install

#=================================================
# Installation
#=================================================
%install

cd %{_sourcedir}

%if "%{?_os}" != "aix"
%define no_init true
%define no_cron true
%define no_ld true
%define no_profile true
%endif

make install DESTDIR=%{buildroot} USE_SYSTEM_OPENSSL=%{use_system_openssl} USE_SYSTEM_LMDB=%{use_system_lmdb} NO_INIT=%{no_init} NO_CRON=%{no_cron} NO_LD=%{no_ld} NO_PROFILE=%{no_profile} 

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

# Do this at first install
CFRUDDER_FIRST_INSTALL=0
if [ $1 -eq 1 ]
then
  # Set rudder-agent as service
%if "%{?_os}" == "aix"
  /usr/bin/mkssys -s rudder-agent -p %{ruddervardir}/cfengine-community/bin/cf-execd -a "-F" -u root -S -n15 -f9 -R
  /usr/sbin/mkitab "rudder-agent:23456789:once:/usr/bin/startsrc -s rudder-agent"
  # No need to tell init to re-read /etc/inittab, it does it automatically every 60 seconds
%else
  RUDDER_AGENT_INIT_ENABLED=$(LANG=C chkconfig | grep -Ec "rudder-agent.*on")

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

%if "%{?rhel}" == "3"
# Update and reload ld.so configuration if needed, RHEL/CentOS 3 style.
if ! grep -q "/opt/rudder/lib" /etc/ld.so.conf; then
  echo "/opt/rudder/lib" >> /etc/ld.so.conf
  ldconfig
fi
%endif


%if "%{?_os}" == "aix"
service_stop_cmd="/usr/bin/stopsrc -s rudder-agent"
service_start_cmd="/usr/bin/startsrc -s rudder-agent"
%else
service_stop_cmd="service rudder-agent stop || service rudder-agent forcestop"
service_start_cmd="service rudder-agent start"
%fi

/opt/rudder/share/package-scripts/rudder-agent-postinst "${CFRUDDER_FIRST_INSTALL}" "${service_stop_cmd}" "${service_start_cmd}"

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
