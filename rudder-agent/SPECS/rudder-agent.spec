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
# Variables
#=================================================
%define real_name            rudder-agent
%define real_epoch           1398866025

%define rudderdir            /opt/rudder
%define ruddervardir         /var/rudder
%define rudderlogdir         /var/log/rudder
%define bindir               /usr/bin

# use_system_lmdb checks if to build CFEngine we will need to build LMDB or if
# a package already exists on the system.
# Default value is false sine no rpm based target provides it
%define use_system_lmdb false

# Same goes for the use of the local OpenSSL install vs. a bundled one
%define use_system_openssl true

# Same goes for the use of the local PCRE install vs. a bundled one
%define use_system_pcre true

# Same goes for the use of the local Curl install vs. a bundled one
%define use_system_curl true

# Same goes for the use of the local libyaml install vs. a bundled one
%define use_system_yaml true

# Same goes for the use of the local libxml2 install vs. a bundled one
%define use_system_xml true

# Same goes for the use of the local zlib install vs. a bundled one
%define use_system_zlib true

# Same goes for the use of the local perl install vs. a bundled one
%define use_system_perl true

# Default to using systemd for service management
%define use_systemd true

# Default to use PIE code if possible
%define use_pie true

# Default to build with posix acl support
%define use_acl true

%if "%{real_name}" == "rudder-agent"
# default different on agent thin and agent
%define use_system_fusion false
%else
%define use_system_fusion true
%endif

# 1- AIX
%if "%{?_os}" == "aix"
# no system anything on aix
%define use_system_perl false
%define use_system_openssl false
%define use_system_pcre false
%define use_system_curl false
%define use_system_zlib false
%define use_system_yaml false
%define use_system_xml false
%define use_pie false
%define use_acl false
%endif

# 2 - RHEL
%if 0%{?rhel} && 0%{?rhel} == 3
# no PCRE on RHEL3
%define use_system_pcre false
%define use_system_zlib false
%endif
%if 0%{?rhel} && 0%{?rhel} <= 5
# system perl too old on rhel3 and rhel5
%define use_system_perl false
%define use_system_openssl false
%define use_system_curl false
%define use_system_yaml false
#libxml too old
%define use_system_xml false
%endif
%if 0%{?rhel} && 0%{?rhel} <= 6
# PIE and PIC incompatible on old gcc
%define use_pie false
%endif

# 3 - SUSE
# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version} && 0%{?suse_version} < 1200
# system perl and openssl too old on sles 10 and 11
%define use_system_perl false
%define use_system_openssl false
%define use_system_curl false
# no yaml on sles 10 and 11
%define use_system_yaml false
#libxml too old
%define use_system_xml false
# PIE and PIC incompatible on old gcc
%define use_pie false
%endif

#=================================================
# Header
#=================================================
Summary: Configuration management and audit tool - agent
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: %{real_epoch}
License: GPLv3
URL: http://www.rudder-project.org

Group: Applications/System

Source1: Makefile
Source2: filter-reqs.pl

%if "%{use_system_perl}" == "false"
# Prevent dependency auto-generation, that tries to be helpful by detecting Perl dependencies from
# FusionInventory. We handle that with the perl standalone installation already.
AutoReq: 0
AutoProv: 0
%else
Requires: perl
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Generic requirements
BuildRequires: gcc bison flex autoconf automake libtool
%if "%{real_name}" == "rudder-agent"
Conflicts: rudder-agent-thin
%else
Provides: rudder-agent = %{real_epoch}:%{real_version}
Conflicts: rudder-agent
%endif

# Specific requirements

%if "%{use_system_fusion}" == "true"
Requires: fusioninventory-agent fusioninventory-agent-task-inventory
%endif

## For Linux
%if "%{?_os}" != "aix"
BuildRequires: pam-devel
%endif

## Requirement for cpanminus
# rh 6,7
%if 0%{?rhel} && 0%{?rhel} >= 6
BuildRequires: perl-IPC-Cmd
%endif

# rhel perl core is too minimal, we try to not add too much here
%if 0%{?rhel} && 0%{?rhel} >= 7
Requires: perl-Digest 
BuildRequires: perl-Digest
%endif

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

# https fails on old distro because they don't support modern certificates (namely rhel3, aix5, sles10 and sles11)
%define use_https true
%if 0%{?rhel} && 0%{?rhel} < 4
%define use_https false
%endif
%if 0%{?suse_version} && 0%{?suse_version} < 1200
%define use_https false
%endif
%if "%{?_os}" == "aix"
%define use_https false
%endif

# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version} && 0%{?suse_version} < 1140
Requires: pmtools
%endif

%if 0%{?suse_version} && 0%{?suse_version} >= 1140
Requires: dmidecode
%endif

## ACL dependencies
%if "%{?_os}" != "aix"
BuildRequires: libacl-devel
Requires: libacl
%endif
%if 0%{?rhel} && 0%{?rhel} < 4
# libattr-devel should be a dependency of libacl-devel on rhel3 but it's not declared
BuildRequires: libattr-devel
%endif

## YAML dependencies
%if "%{use_system_yaml}" == "true"
BuildRequires: libyaml-devel
%endif
%if "%{use_system_yaml}" == "true" && 0%{?suse_version} && 0%{?suse_version} >= 1200
Requires: libyaml-0-2
%endif
# no yaml on sles other than 12
%if "%{use_system_yaml}" == "true" && 0%{?suse_version} == 0
Requires: libyaml
%endif

## XML dependencies
%if "%{use_system_xml}" == "true"
BuildRequires: libxml2-devel
Requires: libxml2
%endif

## CURL dependencies
%if "%{use_system_curl}" == "true"
BuildRequires: curl-devel
Requires: curl
%endif

## Openssl dependencies
%if "%{use_system_openssl}" == "true"
BuildRequires: openssl-devel
Requires: openssl
%endif

## PRE dependencies
%if "%{use_system_pcre}" == "true"
BuildRequires: pcre-devel
Requires: pcre
%endif

# Common commands

%define install_command        install
%define cp_a_command           cp -a

%if "%{?_os}" == "aix"
%define install_command        installbsd -c
%define cp_a_command           cp -hpPr
# -brtl forces libtool to use shared libraries
# -L adds the library path to the produced executables
# -static-libgcc is added because gcc is not provided on aix
%define build_ldflags -static-libgcc -Wl,-brtl -Wl,-L%{rudderdir}/lib
%define build_cflags -static-libgcc
%else
%define build_ldflags -Wl,-R%{rudderdir}/lib
%define build_cflags %{nil}
%endif

%if "%{real_name}" == "rudder-agent"

# Use our own dependency generator
%global _use_internal_dependency_generator 0
%global __find_requires_orig %{__find_requires}
%define __find_requires %{_sourcedir}/filter-reqs.pl %{use_system_lmdb} %{use_system_perl} %{__find_requires_orig}
%global __find_provides_orig %{__find_provides}
%define __find_provides %{_sourcedir}/filter-reqs.pl %{use_system_lmdb} %{use_system_perl} %{__find_provides_orig}
%endif

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

# libattr libtool file is looked for in /lib64 but put in /usr/lib64 on rhel3
%if 0%{?rhel} && 0%{?rhel} < 4
cp /usr/lib64/libattr.a /usr/lib64/libattr.la /lib64 || cp /usr/lib/libattr.a /usr/lib/libattr.la /lib
%endif

make %{?_smp_mflags} BUILD_CFLAGS="${RPM_OPT_FLAGS} %{build_cflags}" BUILD_LDFLAGS="%{build_ldflags}" USE_SYSTEM_OPENSSL=%{use_system_openssl} USE_SYSTEM_LMDB=%{use_system_lmdb} USE_SYSTEM_PCRE=%{use_system_pcre} USE_SYSTEM_FUSION=%{use_system_fusion} USE_SYSTEM_PERL=%{use_system_perl} USE_HTTPS=%{use_https} USE_SYSTEM_ZLIB=%{use_system_zlib} USE_SYSTEM_CURL=%{use_system_curl} USE_SYSTEM_YAML=%{use_system_yaml} USE_SYSTEM_XML=%{use_system_xml} USE_PIE=%{use_pie} USE_ACL=%{use_acl}

# there was a slibclean here on aix
# TODO, check that it is not necessary anymore since we no more do a make install

#=================================================
# Installation
#=================================================
%install

cd %{_sourcedir}

%if "%{?_os}" == "aix"
%define no_init true
%define no_cron true
%define no_ld true
%define no_profile true
%define no_ldso true
%endif

#### Use systemd everywhere except on: AIX, RHEL<7, SLES<12, Fedora<15
%if "%{?_os}" == "aix"
%define use_systemd false
%endif

%if 0%{?rhel} && 0%{?rhel} < 7
%define use_systemd false
%endif

%if 0%{?suse_version} && 0%{?suse_version} < 1315
%define use_systemd false
%endif

%if 0%{?fedora} && 0%{?fedora} < 15
%define use_systemd false
%endif
####

%if 0%{?rhel} && 0%{?rhel} == 3
%define no_ldso true
%endif

make install DESTDIR=%{buildroot} BUILD_LDFLAGS="%{build_ldflags}" USE_SYSTEM_OPENSSL=%{use_system_openssl} USE_SYSTEM_LMDB=%{use_system_lmdb} USE_SYSTEM_PCRE=%{use_system_pcre} USE_SYSTEM_ZLIB=%{use_system_zlib} USE_SYSTEM_CURL=%{use_system_curl} USE_SYSTEMD=%{use_systemd} NO_INIT=%{no_init} NO_CRON=%{no_cron} NO_LD=%{no_ld} NO_PROFILE=%{no_profile} USE_SYSTEM_FUSION=%{use_system_fusion} USE_SYSTEM_PERL=%{use_system_perl} NO_LDSO=%{no_ldso} USE_HTTPS=%{use_https}  USE_SYSTEM_YAML=%{use_system_yaml} USE_SYSTEM_XML=%{use_system_xml} USE_PIE=%{use_pie} USE_ACL=%{use_acl}

# remove perl doc
rm -rf %{buildroot}/opt/rudder/man %{buildroot}/opt/rudder/lib/perl5/5.22.0/pod

# strip binaries
find %{buildroot}/opt/rudder/bin -type f | xargs file -i | grep -E "application/x-sharedlib|application/x-executable" | awk -F: '{print $1}' | xargs strip

# Build a list of files to include in this package for use in the %files section below
find %{buildroot} -type f -o -type l | sed "s,%{buildroot},," | sed "s,\.py$,\.py*," | grep -v "%{rudderdir}/etc/uuid.hive" | grep -v "/etc/bash_completion.d" | grep -v "%{ruddervardir}/cfengine-community/ppkeys" > %{_builddir}/file.list.%{name}

%pre
#=================================================
# Pre Installation
#=================================================

CFRUDDER_FIRST_INSTALL=$1

LOG_DIR="/var/log/rudder/install/"
LOG_FILE="${LOG_DIR}/rudder-agent.log"

mkdir -p "${LOG_DIR}"
echo "`date` - Starting rudder-agent pre installation script" >> ${LOG_FILE}

# Restart daemons if we stopped them, otherwise not
if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 ]
then
  # Part of the package now, but create it anyway in case
  # of upgrade from a very old version
  mkdir -p /var/rudder/tmp

%if "%{use_systemd}" == "true"
    if [ -f /etc/init.d/rudder-agent ]
    then
      # we are migrating from sysv to systemd
      touch /var/rudder/tmp/migration-rudder-service-systemd

      if type chkconfig > /dev/null
      then
        # If old rudder-agent service is here and enabled
        if LANG=C chkconfig --list rudder-agent 2>&1 | grep -q -e 3:on -e B:on
        then
          touch /var/rudder/tmp/migration-rudder-service-enabled
          touch /var/rudder/tmp/migration-rudder-service-enabled-server
        fi

        # If old rudder service is here and enabled
        if LANG=C chkconfig --list rudder 2>&1 | grep -q -e 3:on -e B:on
        then
          touch /var/rudder/tmp/migration-rudder-service-enabled
          touch /var/rudder/tmp/migration-rudder-service-enabled-server
        fi
      fi

      # Test if cf-serverd is disabled
      if [ -f /etc/default/rudder-agent ]
      then
        if grep -q '^CFENGINE_COMMUNITY_RUN_1="0"' /etc/default/rudder-agent
        then
          touch /var/rudder/tmp/migration-rudder-cf-serverd-disabled
        fi
      fi
    fi
%else
    if [ -f /etc/init.d/rudder ]
    then
      # We are migrating from a pre-4.3 to 4.3
      touch /var/rudder/tmp/migration-rudder-service-rename

      # If old rudder service is here and enabled
      if type chkconfig > /dev/null
      then 
        if LANG=C chkconfig --list rudder 2>&1 | grep -q -e 3:on -e B:on
        then
          touch /var/rudder/tmp/migration-rudder-service-enabled
          touch /var/rudder/tmp/migration-rudder-service-enabled-server
        fi
      fi
    fi
%endif
fi

%post
#=================================================
# Post Installation
#=================================================

CFRUDDER_FIRST_INSTALL="false"

if [ $1 -eq 1 ]
then
  CFRUDDER_FIRST_INSTALL="true"
fi

# mandatory with systemd wrapper for old init
%if 0%{?suse_version} && 0%{?suse_version} >= 1315
systemctl daemon-reload
%endif

%if "%{?rhel}" == "3"
# Update and reload ld.so configuration if needed, RHEL/CentOS 3 style.
if ! grep -q "/opt/rudder/lib" /etc/ld.so.conf; then
  echo "/opt/rudder/lib" >> /etc/ld.so.conf
  ldconfig
fi
%endif

/opt/rudder/share/package-scripts/rudder-agent-postinst "${CFRUDDER_FIRST_INSTALL}" "%{?_os}" "%{use_systemd}" ""

%preun
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

# Keep a backup copy of policy_server.dat
if [ -f /var/rudder/cfengine-community/policy_server.dat ]; then
  mkdir -p /var/backups/rudder
  cp -f /var/rudder/cfengine-community/policy_server.dat /var/backups/rudder/policy_server.dat-$(date +%Y%m%d)
  echo "INFO: A back up copy of the /var/rudder/cfengine-community/policy_server.dat has been created in /var/backups/rudder"
fi

# Keep a backup copy of CFEngine policy_server.dat
if [ -f /var/cfengine/policy_server.dat ]; then
  mkdir -p /var/backups/rudder
  cp -f /var/cfengine/policy_server.dat /var/backups/rudder/cfengine_policy_server.dat-$(date +%Y%m%d)
  echo "INFO: A back up copy of the /var/cfengine/policy_server.dat has been created in /var/backups/rudder"
fi

# Keep a backup copy of CFEngine ppkeys
if [ -d /var/rudder/cfengine-community/ppkeys/ ]; then
  mkdir -p /var/backups/rudder
  %{cp_a_command} -f /var/rudder/cfengine-community/ppkeys/ /var/backups/rudder/ppkeys-$(date +%Y%m%d)
  echo "INFO: A back up copy of the /var/rudder/cfengine-community/ppkeys has been created in /var/backups/rudder"
fi


%postun
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
%files -f %{_builddir}/file.list.%{name}
%defattr(-, root, root, 0755)

# The following file is declared to belong to this package but will not be installed
# This is because it is populated during post-inst scriptlet
# This is not reflected in debian packaging, because dpkg will never replace an
# existing file declared in conffiles
%ghost %{rudderdir}/etc/uuid.hive

%attr(0700, -, -) %dir %{ruddervardir}/cfengine-community/ppkeys
%dir %{ruddervardir}/cfengine-community/bin
%dir %{ruddervardir}/cfengine-community/inputs
%dir %{ruddervardir}/tmp
%dir %{ruddervardir}/ncf/common
%dir %{ruddervardir}/ncf/local
%dir %{ruddervardir}/tools
%dir %{rudderlogdir}/install
%dir %{rudderlogdir}/agent-check

%if "%{?_os}" != "aix"
# no init no cron and no profile with aix
%config /etc/cron.d/rudder-agent
%config /etc/profile.d/rudder-agent.sh
%if "${use_systemd}" == "false"
%config(noreplace) /etc/default/rudder-agent
%endif
%endif
%config /etc/bash_completion.d/rudder.sh

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <rudder-dev@rudder-project.org> %{version}
- See https://www.rudder-project.org/site/documentation/user-manual/ for changelogs
