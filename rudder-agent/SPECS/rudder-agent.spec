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
%define with_lmdb true
%define with_openssl false
%define with_pcre2 false
%define with_libcurl false
%define with_augeas true
%define with_jq false
# replicate defaults from configure : all features
%define enable_https true
%define enable_pie true
%define enable_systemd true
%define enable_rust true
%define enable_bindgen true


# NOTE: Fedora macros are also used by AL2023

%if 0%{?rhel} >= 8
# https://pagure.io/packaging-committee/issue/738
%define __brp_mangle_shebangs /usr/bin/true
%endif

%if 0%{?fedora}
# https://pagure.io/packaging-committee/issue/738
%define __brp_mangle_shebangs /usr/bin/true
%endif

# 2 - RHEL & Fedora
%if 0%{?rhel} && 0%{?rhel} < 8
# no jq before RHEL8
%define with_jq true
%define with_openssl true
%define enable_bindgen false
%endif
%if 0%{?rhel} && 0%{?rhel} <= 8
# need pcre2 for rhel < 8
%define with_pcre2 true
%endif
%if 0%{?rhel} && 0%{?rhel} <= 9
# need updated curl for RHEL 9
%define with_libcurl true
%endif


# 3 - SUSE
%if 0%{?suse_version} && 0%{?suse_version} < 1500
%define with_openssl true
%define enable_bindgen false
%endif
%if 0%{?suse_version} && !0%{?is_opensuse}
# no jq on sles, only on opensuse
%define with_jq true
%define with_libcurl true
%define with_pcre2 true
%endif

%if "%{force_embed_openssl}" == "true"
%define with_openssl true
%define with_libcurl true
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

# Python dependency, very old os are still to be added
%if 0%{?rhel} >= 9
Requires: python3
%endif
%if 0%{?rhel} == 8
Requires: (python or python3)
%endif
%if 0%{?rhel} && 0%{?rhel} < 8
Requires: python
%endif
%if 0%{?sle_version} >= 150000
Requires: python3-base
%endif

%if 0%{?rhel}
BuildRequires: perl-CPAN
%endif

%if 0%{?rhel} >= 9 || 0%{?fedora}
Requires: perl-interpreter perl-lib perl-English perl-Memoize perl-Sys-Hostname perl-File-Find perl-base perl-Digest-MD5 perl-Math-BigInt perl-Net perl-JSON-PP perl-User-pwent
%endif
%if 0%{?rhel} == 8
Requires: perl-interpreter perl-Memoize perl-JSON-PP perl-Math-BigInt perl-Digest-MD5
%endif
%if 0%{?rhel} && 0%{?rhel} == 8
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version)) perl-Digest-MD5
%endif
%if 0%{?rhel} && 0%{?rhel} < 7
Requires: perl(:MODULE_COMPAT_%(eval "`%{__perl} -V:version`"; echo $version))
%endif
%if 0%{?suse_version}
Requires: perl = %{perl_version}
%endif

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# Generic requirements
BuildRequires: gcc bison flex autoconf automake libtool pam-devel libacl-devel
Requires: libacl
Conflicts: rudder-agent-thin

# Specific requirements

## For RHEL and Fedora
Requires: cron net-tools diffutils dmidecode

%if 0%{?rhel} || 0%{?fedora}
BuildRequires: make byacc

## Requirement for cpanminus
BuildRequires: perl-IPC-Cmd

# RHEL perl core is too minimal, we try to not add too much here
Requires: perl-Digest
BuildRequires: perl-Digest
Requires: crontabs
%endif

## For SLES
%if 0%{?suse_version}
Requires: cron
%endif

# We need the ps command for scripts

%if 0%{?rhel} && 0%{?rhel} >= 8
Requires: procps-ng
%endif

%if 0%{?fedora}
Requires: procps-ng
%endif

%if "%{with_jq}" == "false"
Requires: jq
%endif

# SLES15
%if 0%{?suse_version} && "%{enable_bindgen}" == "true"
BuildRequires: clang7
%endif

# RHEL
%if 0%{?rhel} && "%{enable_bindgen}" == "true"
BuildRequires: clang
%endif

## YAML dependencies
BuildRequires: libyaml-devel
%if 0%{?suse_version} && 0%{?suse_version} >= 1200
Requires: libyaml-0-2
%endif
# no yaml on sles other than 12
%if 0%{?suse_version} == 0
Requires: libyaml
%endif

## XML dependencies
BuildRequires: libxml2-devel
Requires: libxml2

## pcre build dependencies
%if "%{with_pcre2}" == "false"
BuildRequires: pcre2-devel
Requires: pcre2
%endif

## CURL dependencies
%if "%{with_libcurl}" == "false"
BuildRequires: curl-devel
Requires: curl
%endif

## Augeas dependencies
%if "%{with_augeas}" == "false"
Requires: augeas
BuildRequires: augeas-devel
%endif
%if "%{with_augeas}" == "true"
BuildRequires: readline-devel
%endif

## Openssl dependencies
%if "%{with_openssl}" == "false"
BuildRequires: openssl-devel
Requires: openssl
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

opt="--disable-apt"

# Default is to not embed anything
%if "%{with_lmdb}" == "true"
opt="${opt} --with-lmdb"
%endif
%if "%{with_openssl}" == "true"
opt="${opt} --with-openssl"
%endif
%if "%{with_libcurl}" == "true"
opt="${opt} --with-libcurl"
%endif
%if "%{with_augeas}" == "true"
opt="${opt} --with-augeas"
%endif
%if "%{with_pcre2}" == "true"
opt="${opt} --with-pcre2"
%endif
%if "%{with_jq}" == "true"
opt="${opt} --with-jq"
%endif
%if "%{with_zlib}" == "true"
opt="${opt} --with-zlib"
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
%if "%{enable_rust}" == "false"
opt="${opt} --disable-rust"
%endif
%if "%{enable_bindgen}" == "false"
opt="${opt} --disable-bindgen"
%endif

perl -MModule::CoreList -e '' || cpan -f -T -i Module::CoreList < /dev/null || true
perl -MYAML::Tiny -e '' || cpan -f -T -i YAML::Tiny < /dev/null
perl -Minc::Module::Install -e '' || cpan -f -T -i Module::Install < /dev/null

./configure ${opt}
make BUILD_CFLAGS="${RPM_OPT_FLAGS}"

#=================================================
# Installation
#=================================================
%install

cd %{_sourcedir}

make install DESTDIR=%{buildroot}

# rhel8 do not have vzps
%if 0%{?rhel} >= 8
rm -f %{buildroot}/opt/rudder/bin/vzps.py
%endif

# strip binaries
find %{buildroot}/opt/rudder/bin -type f | xargs file -i | grep -E "application/x-sharedlib|application/x-executable|application/x-pie-executable" | awk -F: '{print $1}' | xargs strip

# Build a list of files to include in this package for use in the %files section below
find %{buildroot} -type f -o -type l | sed "s,%{buildroot},," | sed "s,\.py$,\.py*," | grep -v "%{rudderdir}/etc/uuid.hive" | grep -v "/etc/bash_completion.d" | grep -v "%{ruddervardir}/cfengine-community/ppkeys" > %{_builddir}/file.list.%{name}

%pre
#=================================================
# Pre Installation
#=================================================

set -e

CFRUDDER_FIRST_INSTALL=$1

LOG_DIR="/var/log/rudder/install/"
LOG_FILE="${LOG_DIR}/rudder-agent-$(date +%%Y%%m%%d).log"

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

# Do it only during uninstallation
if [ $1 -eq 0 ]; then

%if "%{enable_systemd}" == "true"
  systemctl stop rudder-agent >/dev/null 2>&1 || true
  systemctl disable rudder-agent rudder-cf-execd rudder-cf-serverd >/dev/null 2>&1 || true
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

  # Remove the cron script we create at installation to prevent mail
  # flooding, re-installation surprises, and general system garbage.
  rm -f /etc/cron.d/rudder-agent

  # Make sure that Rudder agent specific files have been removed
  rm -f /etc/init.d/rudder-agent
  rm -f /etc/default/rudder-agent
  rm -fr /opt/rudder/var/fusioninventory
  rm -f /opt/rudder/etc/uuid.hive
  rm -f /opt/rudder/etc/ssl/agent.cert
  rm -f /opt/rudder/etc/policy_server.dat
  rm -f /var/rudder/lib/ssl/policy_server_hash
  rm -fr /var/rudder/ncf
  rm -fr /var/rudder/tmp
  rm -fr /var/rudder/cfengine-community
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

%config /etc/profile.d/rudder-agent.sh
%if "%{enable_systemd}" == "false"
%config(noreplace) /etc/default/rudder-agent
%endif
%config /etc/bash_completion.d/rudder.sh

#=================================================
# Changelog
#=================================================
%changelog
* Wed Nov  22 2017 - Rudder Team <dev@rudder.io> %{version}
- See https://docs.rudder.io/changelogs/current/index.html for changelogs
