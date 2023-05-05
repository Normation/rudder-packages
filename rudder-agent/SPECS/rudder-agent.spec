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

# Defaults
%define with_zlib false
%define with_lmdb true
%define with_pcre false
%define with_openssl false
%define with_libyaml false
%define with_libxml2 false
%define with_libcurl false
%define with_augeas false
%define with_jq false
%define with_perl false
# replicate defaults from configure : all features
%define enable_https true
%define enable_pie true
%define enable_systemd true
%define enable_libacl true
%define enable_pam true

%if 0%{?rhel} >= 8
# https://pagure.io/packaging-committee/issue/738
%define __brp_mangle_shebangs /usr/bin/true
%endif

%if 0%{?fedora}
# https://pagure.io/packaging-committee/issue/738
%define __brp_mangle_shebangs /usr/bin/true
%endif

# 1- AIX
%if "%{?aix}"
%define with_zlib true
%define with_pcre true
%define with_openssl true
%define with_libyaml true
%define with_libxml2 true
%define with_libcurl true
%define with_augeas true
%define with_jq true
%define with_perl true
%define enable_https false
%define enable_systemd false
%endif

# 2 - RHEL & Fedora
%if 0%{?rhel} && 0%{?rhel} <= 5
# system perl too old on RHEL5
%define with_perl true
%define with_libyaml true
#libxml too old
%define with_libxml2 true
%endif
%if 0%{?rhel} && 0%{?rhel} <= 6
# PIE and PIC incompatible on old gcc
%define enable_pie false
# no augeas or augeas too old
%define with_augeas true
%endif
%if 0%{?rhel} && 0%{?rhel} < 8
# no jq before RHEL8
%define with_jq true
%define with_libcurl true
%define with_openssl true
%endif
%if 0%{?rhel} && 0%{?rhel} >= 9
# we embed openssl as system is too recent (openssl3) in this case
%define with_openssl true
%endif
%if 0%{?fedora} && 0%{?fedora} >= 34
# we embed openssl as system is too recent (openssl3) in this case
%define with_openssl true
%endif

# 3 - SUSE
# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version} && 0%{?suse_version} < 1200
# system perl and openssl too old on sles 10 and 11
%define with_perl true
# no yaml on sles 10 and 11
%define with_libyaml true
#libxml too old
%define with_libxml2 true
# PIE and PIC incompatible on old gcc
%define enable_pie false
%endif
%if 0%{?suse_version} && 0%{?suse_version} < 1500
# augeas too old on suse < 15
%define with_augeas true
%endif
%if 0%{?suse_version} && !0%{?is_opensuse}
# no jq on sles, only on opensuse
%define with_jq true
%define with_libcurl true
%define with_openssl true
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

%if "%{with_perl}" == "false" && 0%{?rhel}
BuildRequires: perl-CPAN
%endif

%if "%{with_perl}" == "false" && 0%{?fedora}
Requires: perl-interpreter perl-lib perl-English perl-Memoize perl-Sys-Hostname perl-File-Find
%endif
%if "%{with_perl}" == "false" && 0%{?rhel} >= 9
Requires: perl-interpreter perl-lib perl-English perl-Memoize perl-Sys-Hostname perl-File-Find
%endif
%if "%{with_perl}" == "false" && 0%{?rhel} == 8
Requires: perl-interpreter perl-Memoize
%endif
%if "%{with_perl}" == "false" && 0%{?rhel} && 0%{?rhel} < 8
Requires: perl
%endif
%if "%{with_perl}" == "false" && 0%{?suse_version}
Requires: perl
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Generic requirements
BuildRequires: gcc bison flex autoconf automake libtool
Conflicts: rudder-agent-thin

# Specific requirements

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

%if 0%{?fedora}
Requires: dmidecode
%endif

# dmiecode is provided by kernel-utils on RHEL3
%if 0%{?rhel} && 0%{?rhel} < 4
Requires: kernel-utils
%endif

# https fails on old distro because they don't support modern certificates (namely RHEL3, aix5, sles10 and sles11)
%if 0%{?rhel} && 0%{?rhel} < 6
%define enable_https false
%endif
%if 0%{?suse_version} && 0%{?suse_version} < 1200
%define enable_https false
%endif

# Reference for suse_version : https://en.opensuse.org/openSUSE:Build_Service_cross_distribution_howto
%if 0%{?suse_version} && 0%{?suse_version} < 1140
Requires: pmtools
%endif

%if 0%{?suse_version} && 0%{?suse_version} >= 1140
Requires: dmidecode
%endif

# We need the ps command for scripts

%if 0%{?rhel} && 0%{?rhel} >= 8
Requires: procps-ng
%endif

%if 0%{?fedora}
Requires: procps-ng
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

%if "%{with_jq}" == "false"
Requires: jq
%endif

## YAML dependencies
%if "%{with_libyaml}" == "false"
BuildRequires: libyaml-devel
%endif
%if "%{with_libyaml}" == "false" && 0%{?suse_version} && 0%{?suse_version} >= 1200
Requires: libyaml-0-2
%endif
# no yaml on sles other than 12
%if "%{with_libyaml}" == "false" && 0%{?suse_version} == 0
Requires: libyaml
%endif

## XML dependencies
%if "%{with_libxml2}" == "false"
BuildRequires: libxml2-devel
Requires: libxml2
%endif

## CURL dependencies
%if "%{with_libcurl}" == "false"
BuildRequires: curl-devel
Requires: curl
%endif

## Augeas dependencies
%if "%{with_augeas}" == "false"
Requires: augeas
%endif
%if "%{with_augeas}" == "true" && "%{?aix}" ==""
BuildRequires: readline-devel
%endif

## Openssl dependencies
%if "%{with_openssl}" == "false"
BuildRequires: openssl-devel
Requires: openssl
%endif

## PCRE dependencies
%if "%{with_pcre}" == "false"
BuildRequires: pcre-devel
Requires: pcre
%endif

#### Use systemd everywhere except on: AIX, RHEL<7, SLES<12, Fedora<15
%if "%{?aix}"
%define enable_systemd false
%endif

%if 0%{?rhel} && 0%{?rhel} < 7
%define enable_systemd false
%endif

%if 0%{?suse_version} && 0%{?suse_version} < 1315
%define enable_systemd false
%endif

%if 0%{?fedora} && 0%{?fedora} < 15
%define enable_systemd false
%endif
####


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

opt=""

# Default is to not embed anything
%if "%{with_zlib}" == "true"
opt="${opt} --with-zlib"
%endif
%if "%{with_lmdb}" == "true"
opt="${opt} --with-lmdb"
%endif
%if "%{with_pcre}" == "true"
opt="${opt} --with-pcre"
%endif
%if "%{with_openssl}" == "true"
opt="${opt} --with-openssl"
%endif
%if "%{with_libyaml}" == "true"
opt="${opt} --with-libyaml"
%endif
%if "%{with_libxml2}" == "true"
opt="${opt} --with-libxml2"
%endif
%if "%{with_libcurl}" == "true"
opt="${opt} --with-libcurl"
%endif
%if "%{with_augeas}" == "true"
opt="${opt} --with-augeas"
# augeas on aix depends on readline
%if "%{?aix}"
opt="${opt} --with-readline"
%endif
%endif
%if "%{with_libcurl}" == "true"
opt="${opt} --with-libcurl"
%endif
%if "%{with_jq}" == "true"
opt="${opt} --with-jq"
%endif

# Defaults is to enable all features
%if "%{enable_https}" == "false"
opt="${opt} --disable-https"
%endif
%if "%{enable_pie}" == "false"
opt="${opt} --disable-pie"
%endif
%if "%{enable_systemd}" == "false"
opt="${opt} --disable-systemd"
%endif
%if "%{enable_libacl}" == "false"
opt="${opt} --disable-libacl"
%endif
%if "%{enable_pam}" == "false"
opt="${opt} --disable-pam"
%endif

%if "%{with_perl}" == "true"
opt="${opt} --with-perl"
%else
cpan -f -T -i Module::CoreList < /dev/null
cpan -f -T -i YAML::Tiny < /dev/null
cpan -f -T -i Module::Install < /dev/null
%endif

# libattr libtool file is looked for in /lib64 but put in /usr/lib64 on RHEL3
%if 0%{?rhel} && 0%{?rhel} < 4
cp /usr/lib64/libattr.a /usr/lib64/libattr.la /lib64 || cp /usr/lib/libattr.a /usr/lib/libattr.la /lib
%endif


./configure ${opt}
make BUILD_CFLAGS="${RPM_OPT_FLAGS}"

#=================================================
# Installation
#=================================================
%install

cd %{_sourcedir}

make install DESTDIR=%{buildroot}

# rhel7 doesn't have python 3 so we force python2 instead
%if 0%{?rhel} == 7
find %{buildroot} -type f | xargs sed -i '1,1s|#!/usr/bin/python3|#!/usr/bin/python2|'
%endif
%if 0%{?suse_version} && 0%{?suse_version} < 1500
find %{buildroot} -type f | xargs sed -i '1,1s|#!/usr/bin/python3|#!/usr/bin/python2|'
%endif

# remove perl doc
rm -rf %{buildroot}/opt/rudder/man %{buildroot}/opt/rudder/lib/perl5/5.22.0/pod

# rhel8 do not have vzps
%if 0%{?rhel} >= 8
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

/opt/rudder/share/package-scripts/rudder-agent-postinst "${CFRUDDER_FIRST_INSTALL}" "rpm" "%{enable_systemd}" ""

# the conffiles case (aka %config)
# --------------------------------
# 1/ %config files and %config(noreplace) files can become regular files and rpm stays happy
# 2/ when a conffile becomes a regular file, rpm saves it with a .rpmsave extension whether (noreplace) has been provided or not
# since it it not really a conffile we must remove it

# migration from pre 7.0
rm -f /etc/cron.d/rudder-agent.rpmsave

%preun
#=================================================
# Pre Uninstallation
#=================================================

set -e

if [ $1 -eq 0 ]; then
  REMOVE=true
else
  REMOVE=false
fi
# Do it during upgrade and uninstall
/opt/rudder/share/package-scripts/rudder-agent-prerm "${REMOVE}"

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

%if "%{enable_systemd}" == "true"
  systemctl stop rudder-agent || true
  systemctl disable rudder-agent rudder-cf-execd rudder-cf-serverd || true
  rm -f /lib/systemd/system/rudder-agent.service
  rm -f /lib/systemd/system/rudder-cf-execd.service
  rm -f /lib/systemd/system/rudder-cf-serverd.service
  systemctl daemon-reload
%endif

  # Make sure that CFEngine is not running anymore
  for component in cf-agent cf-serverd cf-execd cf-monitord; do
    pidof ${component} | xargs -n 1 kill -9
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
  # Remove the cron entry we created
  sed '/# RUDDER CRON$/d' /var/spool/cron/crontabs/root > /tmp/rudder-installer-cron
  mv /tmp/rudder-installer-cron /var/spool/cron/crontabs/root
  chmod 600 /var/spool/cron/crontabs/root
  chown root:cron /var/spool/cron/crontabs/root
  # signal the change to cron daemon
  EDITOR=/bin/true crontab -e

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
%dir %{ruddervardir}/lib/ssl
%dir %{rudderlogdir}/install
%dir %{rudderlogdir}/agent-check

%if "%{?aix}" == ""
# no init no cron and no profile with aix
%config /etc/profile.d/rudder-agent.sh
%if "%{enable_systemd}" == "false"
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
