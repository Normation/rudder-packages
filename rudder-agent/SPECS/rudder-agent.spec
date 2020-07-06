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
# Default value is false since no rpm based target provides it
%define use_system_lmdb false

# We want openssl 1.1.1 which is currently provided by noone
%define use_system_openssl false

# Same goes for the use of the local PCRE install vs. a bundled one
%define use_system_pcre true

# We need to build curl since we embed openssl
%define use_system_curl false

# Same goes for the use of the local jq install vs. a bundled one
%define use_system_jq true

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

# Default to use ACL library in th agent
%define use_acl true

%if 0%{?rhel} == 8
# https://pagure.io/packaging-committee/issue/738
%define __brp_mangle_shebangs /usr/bin/true
%endif

%if 0%{?fedora}
# https://pagure.io/packaging-committee/issue/738
%define __brp_mangle_shebangs /usr/bin/true
%endif

# Default to embed fusion
%define use_system_fusion false

# 1- AIX
%if "%{?aix}"
# no system anything on aix
%define use_system_perl false
%define use_system_jq false
%define use_system_pcre false
%define use_system_zlib false
%define use_system_yaml false
%define use_system_xml false
%define use_pie false
%define use_acl false
%endif

# 2 - RHEL & Fedora
%if 0%{?rhel} && 0%{?rhel} == 3
# no PCRE on RHEL3
%define use_system_pcre false
%endif
%if 0%{?rhel} && 0%{?rhel} <= 5
# system perl too old on RHEL3 and RHEL5
%define use_system_perl false
%define use_system_yaml false
#libxml too old
%define use_system_xml false
%endif
%if 0%{?rhel} && 0%{?rhel} <= 6
# PIE and PIC incompatible on old gcc
%define use_pie false
%endif
%if 0%{?rhel} && 0%{?rhel} < 8
# no jq before RHEL8
%define use_system_jq false
%endif

%if 0%{?fedora}
%define use_system_curl true
%define use_system_jq false
%define use_system_openssl true
%endif

%if 0%{?rhel} && 0%{?rhel} >= 8
%define use_system_curl true
%define use_system_openssl true
%endif

# 3 - SUSE
# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version} && 0%{?suse_version} < 1200
# system perl and openssl too old on sles 10 and 11
%define use_system_perl false
# no yaml on sles 10 and 11
%define use_system_yaml false
#libxml too old
%define use_system_xml false
# PIE and PIC incompatible on old gcc
%define use_pie false
%endif
%if 0%{?suse_version} && !0%{?is_opensuse}
# no jq on sles, only on opensuse
%define use_system_jq false
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
URL: https://www.rudder.io/

Group: Applications/System

Source1: Makefile

AutoReq: 0
AutoProv: 0

%if "%{use_system_perl}" == "true"
Requires: perl
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Generic requirements
BuildRequires: gcc bison flex autoconf automake libtool
Conflicts: rudder-agent-thin

# Specific requirements

%if "%{use_system_fusion}" == "true"
Requires: fusioninventory-agent fusioninventory-agent-task-inventory
%endif

## For Linux
%if "%{?aix}" ==""
BuildRequires: pam-devel
Requires: syslog
%endif

## Requirement for cpanminus
# RHEL >= 6 and Fedora (no OR for Fedora, not supported by old rpm, used in aix)
%if 0%{?rhel} && 0%{?rhel} >= 6
BuildRequires: perl-IPC-Cmd
%endif

%if 0%{?fedora}
BuildRequires: perl-IPC-Cmd
%endif


# RHEL perl core is too minimal, we try to not add too much here
# RHEL >= 7 and Fedora (no OR for Fedora, not supported by old rpm, used in aix)
%if 0%{?rhel} && 0%{?rhel} >= 7
Requires: perl-Digest
BuildRequires: perl-Digest
%endif

%if 0%{?fedora}
Requires: perl-Digest
BuildRequires: perl-Digest
%endif

## For RHEL and Fedora
%if 0%{?rhel}
BuildRequires: make byacc
Requires: crontabs net-tools diffutils
%endif

%if 0%{?fedora}
BuildRequires: make byacc
Requires: crontabs net-tools diffutils
%endif


## For SLES
%if 0%{?suse_version}
Requires: cron net-tools diffutils
%endif

# dmiecode package on RHEL4+ and fedora
%if 0%{?rhel} && 0%{?rhel} >= 4
Requires: dmidecode
%endif

%%if 0%{?fedora}
Requires: dmidecode
%endif

# dmiecode is provided by kernel-utils on RHEL3
%if 0%{?rhel} && 0%{?rhel} < 4
Requires: kernel-utils
%endif

# https fails on old distro because they don't support modern certificates (namely RHEL3, aix5, sles10 and sles11)
%define use_https true
%if 0%{?rhel} && 0%{?rhel} < 6
%define use_https false
%endif
%if 0%{?suse_version} && 0%{?suse_version} < 1200
%define use_https false
%endif
%if "%{?aix}"
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
%if "%{?aix}" == ""
BuildRequires: libacl-devel
Requires: libacl
%endif
%if 0%{?rhel} && 0%{?rhel} < 4
# libattr-devel should be a dependency of libacl-devel on RHEL3 but it's not declared
BuildRequires: libattr-devel
%endif

%if "%{use_system_jq}" == "true"
Requires: jq
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

%description
Rudder is an open source configuration management and audit solution.

This package contains the agent that must be installed on all nodes to be
managed by Rudder. It is based on two main components: CFEngine Community 3 and
FusionInventory.

#=================================================
# Building
#=================================================
%build

cd %{_sourcedir}

# libattr libtool file is looked for in /lib64 but put in /usr/lib64 on RHEL3
%if 0%{?rhel} && 0%{?rhel} < 4
cp /usr/lib64/libattr.a /usr/lib64/libattr.la /lib64 || cp /usr/lib/libattr.a /usr/lib/libattr.la /lib
%endif

make BUILD_CFLAGS="${RPM_OPT_FLAGS}" USE_SYSTEM_OPENSSL=%{use_system_openssl} USE_SYSTEM_LMDB=%{use_system_lmdb} USE_SYSTEM_PCRE=%{use_system_pcre} USE_SYSTEM_FUSION=%{use_system_fusion} USE_SYSTEM_PERL=%{use_system_perl} USE_SYSTEM_JQ=%{use_system_jq} USE_HTTPS=%{use_https} USE_SYSTEM_ZLIB=%{use_system_zlib} USE_SYSTEM_CURL=%{use_system_curl} USE_SYSTEM_YAML=%{use_system_yaml} USE_SYSTEM_XML=%{use_system_xml} USE_PIE=%{use_pie} USE_ACL=%{use_acl}

# rhel7 doesn't have python 3 so we force python2 instead
%if 0%{?rhel} == 7
find . -type f | xargs sed -i '1,1s|#!/usr/bin/python3|#!/usr/bin/python2|'
%endif
%if 0%{?suse_version} && 0%{?suse_version} < 1500
find . -type f | xargs sed -i '1,1s|#!/usr/bin/python3|#!/usr/bin/python2|'
%endif

#=================================================
# Installation
#=================================================
%install

cd %{_sourcedir}

#### Use systemd everywhere except on: AIX, RHEL<7, SLES<12, Fedora<15
%if "%{?aix}"
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

make install DESTDIR=%{buildroot} USE_SYSTEM_OPENSSL=%{use_system_openssl} USE_SYSTEM_LMDB=%{use_system_lmdb} USE_SYSTEM_JQ=%{use_system_jq} USE_SYSTEM_PCRE=%{use_system_pcre} USE_SYSTEM_ZLIB=%{use_system_zlib} USE_SYSTEM_CURL=%{use_system_curl} USE_SYSTEMD=%{use_systemd} USE_SYSTEM_FUSION=%{use_system_fusion} USE_SYSTEM_PERL=%{use_system_perl} USE_HTTPS=%{use_https}  USE_SYSTEM_YAML=%{use_system_yaml} USE_SYSTEM_XML=%{use_system_xml} USE_PIE=%{use_pie} USE_ACL=%{use_acl}

# remove perl doc
rm -rf %{buildroot}/opt/rudder/man %{buildroot}/opt/rudder/lib/perl5/5.22.0/pod

# rhel8 do not have vzps
%if 0%{?rhel} == 8
rm -f %{buildroot}/opt/rudder/bin/vzps.py
%endif

# strip binaries
%if "%{?aix}" == ""
# already doen in makefile and file -i on aix has a different meaning
find %{buildroot}/opt/rudder/bin -type f | xargs file -i | grep -E "application/x-sharedlib|application/x-executable|application/x-pie-executable" | awk -F: '{print $1}' | xargs strip
%endif

# Build a list of files to include in this package for use in the %files section below
find %{buildroot} -type f -o -type l | sed "s,%{buildroot},," | sed "s,\.py$,\.py*," | grep -v "%{rudderdir}/etc/uuid.hive" | grep -v "/etc/bash_completion.d" | grep -v "%{ruddervardir}/cfengine-community/ppkeys" > %{_builddir}/file.list.%{name}

%pre
#=================================================
# Pre Installation
#=================================================

set -e

CFRUDDER_FIRST_INSTALL=$1

LOG_DIR="/var/log/rudder/install/"
LOG_FILE="${LOG_DIR}/rudder-agent.log"

mkdir -p "${LOG_DIR}"
echo "`date` - Starting rudder-agent pre installation script" >> ${LOG_FILE}

%post
#=================================================
# Post Installation
#=================================================

set -e

CFRUDDER_FIRST_INSTALL="false"

if [ $1 -eq 1 ]
then
  CFRUDDER_FIRST_INSTALL="true"
fi

/opt/rudder/share/package-scripts/rudder-agent-postinst "${CFRUDDER_FIRST_INSTALL}" "rpm" "%{use_systemd}" ""

%preun
#=================================================
# Pre Uninstallation
#=================================================

set -e

# Do it during upgrade and uninstall

# Keep a backup copy of uuid.hive
if [ -f /opt/rudder/etc/uuid.hive ]; then
  mkdir -p /var/backups/rudder
  cp -f /opt/rudder/etc/uuid.hive /var/backups/rudder/uuid.hive-$(date +%Y%m%d)
  echo "INFO: A back up copy of the /opt/rudder/etc/uuid.hive has been created in /var/backups/rudder"
fi

# Keep a backup copy of policy_server.dat
if [ -f /var/rudder/cfengine-community/policy_server.dat ]; then
  mkdir -p /var/backups/rudder
  cp -f /var/rudder/cfengine-community/policy_server.dat /var/backups/rudder/policy_server.dat-$(date +%Y%m%d)
  echo "INFO: A back up copy of the /var/rudder/cfengine-community/policy_server.dat has been created in /var/backups/rudder"
fi

# Keep a backup copy of ppkeys
if [ -d /var/rudder/cfengine-community/ppkeys/ ]; then
  mkdir -p /var/backups/rudder
  cp -rf /var/rudder/cfengine-community/ppkeys/ /var/backups/rudder/ppkeys-$(date +%Y%m%d)
  echo "INFO: A back up copy of the /var/rudder/cfengine-community/ppkeys has been created in /var/backups/rudder"
fi

# Keep a backup copy of agent certificate
if [ -f /opt/rudder/etc/ssl/agent.cert ]; then
  mkdir -p /var/backups/rudder
  cp -f /opt/rudder/etc/ssl/agent.cert /var/backups/rudder/agent.cert-$(date +%Y%m%d)
  echo "INFO: A back up copy of the /opt/rudder/etc/ssl/agent.cert has been created in /var/backups/rudder"
fi


%postun
#=================================================
# Post Uninstallation
#=================================================

set -e

%if "%{?aix}"
# AIX doesn't have a pidof command, let's define it
function pidof {
  # Yeah, "grep -v grep" is ugly, but we can't use the [u]nique trick on a variable
  ps -A | grep "$1" | grep -v grep | awk '{print $1}';
}
%endif

# Do it only during uninstallation
if [ $1 -eq 0 ]; then

%if "%{use_systemd}" == "true"
  systemctl stop rudder-agent || true
  systemctl disable rudder-agent rudder-cf-execd rudder-cf-serverd || true
  rm -f /lib/systemd/system/rudder-agent.service
  rm -f /lib/systemd/system/rudder-cf-execd.service
  rm -f /lib/systemd/system/rudder-cf-serverd.service
  systemctl daemon-reload
%endif

  # Make sure that CFEngine is not running anymore
  for component in cf-agent cf-serverd cf-execd cf-monitord; do
    if pid=`pidof ${component}`; then
      kill -9 ${pid}
    fi
  done

%if "%{?aix}" == ""
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

%attr(0700, -, -) %dir %{ruddervardir}/cfengine-community/ppkeys
%dir %{ruddervardir}/cfengine-community/bin
%dir %{ruddervardir}/cfengine-community/inputs
%dir %{ruddervardir}/tmp
%dir %{ruddervardir}/ncf/common
%dir %{ruddervardir}/ncf/local
%dir %{ruddervardir}/inventories
%dir %{ruddervardir}/tools
%dir %{ruddervardir}/reports/ready
%dir %{rudderlogdir}/install
%dir %{rudderlogdir}/agent-check

%if "%{?aix}" == ""
# no init no cron and no profile with aix
%config /etc/cron.d/rudder-agent
%config /etc/profile.d/rudder-agent.sh
%if "%{use_systemd}" == "false"
%config(noreplace) /etc/default/rudder-agent
%endif
%endif
%config /etc/bash_completion.d/rudder.sh

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <dev@rudder.io> %{version}
- See https://docs.rudder.io/changelogs/current/index.html for changelogs
