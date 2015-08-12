#####################################################################################
# Copyright 2014 Normation SAS
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
# Specification file for ncf-api-virtualenv
#
# Install the ncf framework API Python virtual
# environment
#
# Copyright (C) 2014 Normation
#=================================================

#=================================================
# Variables
#=================================================

# What is the package name
%define real_name        ncf-api-virtualenv

# Where should the package contents be installed
%define installdir       /usr/share/%{real_name}

# The username to create
%define user_name        ncf-api-venv

# Define Apache virtualhost directory

## RHEL / Fedora
%if 0%{?rhel} || 0%{?fedora}
%define apache_vhost_dir    /etc/httpd/conf.d
%endif

## SLES
%if 0%{?sles_version}
%define apache_vhost_dir    /etc/apache2/conf.d
%endif

#=================================================
# Header
#=================================================

Summary: ncf API Virtualenv - ncf API Python virtual environment
Name: %{real_name}
Version: %{real_version}
Release: 1%{?dist}
Epoch: 0
License: GPLv3
URL: http://www.ncf.io

Group: Applications/System

Source1: ncf_api_flask_app.wsgi
Source2: ncf-api-virtualenv.conf
Source3: ncf-api-virtualenv.te

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch

# Disable dependency auto-generation, to prevent Python requirements
# autodetection, which is not desired here.
AutoReq: 0
AutoProv: 0

# Add Requires here - order is important
BuildRequires: python
Requires: python ncf

# We need mod_wsgi to use ncf builder

## RHEL & Fedora
%if 0%{?rhel} || 0%{?fedora}
Requires: httpd mod_wsgi shadow-utils
%endif

## SLES
%if 0%{?sles_version}
Requires: apache2 apache2-mod_wsgi pwdutils
%endif

## 1 - RHEL
%if 0%{?rhel} && 0%{?rhel} == 6
BuildRequires: selinux-policy
%endif

%if 0%{?rhel} && 0%{?rhel} >= 7
BuildRequires: selinux-policy-devel
%endif

## 2 - Fedora
%if 0%{?fedora}
BuildRequires: selinux-policy-devel
%endif

%description
ncf is a CFEngine framework aimed at helping newcomers on CFEngine
to be more quickly operationnal and old timers to spend less time
focusing on low level details and have more time for fun things.

This package provides a Python virtual environment to make the use
of the ncf API easier.

#=================================================
# Source preparation
#=================================================
%prep

# Copy the required source files to the build directory
cp -f %{SOURCE3} %{_builddir}

#=================================================
# Building
#=================================================
%build

# Go into SOURCES
cd %{_sourcedir}

# Build Virtualenv
%if 0%{?sles_version}
# SLES specific exception, see http://www.rudder-project.org/redmine/issues/6365
python virtualenv-1.10.1/virtualenv.py %{real_name}

# Using a recent pip on SLES is not possible due to
# bad interaction between pip and an old OpenSSL.
# See http://stackoverflow.com/questions/17416938/pip-can-not-install-anything
%{real_name}/bin/easy_install pip==1.2.1
%else
python virtualenv/virtualenv.py %{real_name}
%endif

# Get all requirements via pip
%{real_name}/bin/pip install -r %{_sourcedir}/rudder-sources/ncf/api/requirements.txt

# Clean up unwanted binaries
if [ "z%{real_name}" != "" ]; then
  for i in easy_install python pip; do
      rm -f %{real_name}/bin/${i}*
  done
else
  echo "WARNING: Skipping Virtualenv cleanup, as it"
  echo "WARNING: would operate on /bin ..."
  echo "WARNING: Please make sure the real_name macro"
  echo "WARNING: is defined"
fi

%if 0%{?rhel} || 0%{?fedora}
# Build SELinux policy package
cd %{_builddir} && make -f /usr/share/selinux/devel/Makefile
%endif

#=================================================
# Installation
#=================================================
%install

rm -rf %{buildroot}

# Directories

mkdir -p %{buildroot}%{installdir}/
mkdir -p %{buildroot}%{installdir}/share/selinux/
mkdir -p %{buildroot}%{apache_vhost_dir}/
mkdir -p %{buildroot}/var/lib/%{user_name}/

# Files

cp -r %{_sourcedir}/%{real_name}/* %{buildroot}%{installdir}/

install -m 644 %{SOURCE1} %{buildroot}%{installdir}/
install -m 644 %{SOURCE2} %{buildroot}%{apache_vhost_dir}/

%if 0%{?rhel} || 0%{?fedora}
# Install SELinux policy
install -m 644  %{_builddir}/ncf-api-virtualenv.pp %{buildroot}%{installdir}/share/selinux/
%endif

%post -n ncf-api-virtualenv
#=================================================
# Post Installation
#=================================================

# Create the package user
if ! getent passwd %{user_name} >/dev/null; then
  echo -n "INFO: Creating the %{user_name} user..."
  useradd -r -d /var/lib/%{user_name} -c "ncf API,,," %{user_name} >/dev/null 2>&1
  chown %{user_name}:%{user_name} /var/lib/%{user_name}/
  echo " Done"
fi

%if 0%{?rhel} || 0%{?fedora}
# SELinux support
# Check "sestatus" presence, and if here tweak our installation to be
# SELinux compliant
if type sestatus >/dev/null 2>&1
then
  # Add/Update the ncf-api-virtualenv SELinux policy
  semodule -i %{installdir}/share/selinux/ncf-api-virtualenv.pp 2>/dev/null
fi
%endif

%if 0%{?rhel} || 0%{?fedora}
# EL-based systems enable the WSGI module for apache
# automatically, nothing to do here :)
%endif

%if 0%{?sles_version}
# Enable mod_wsgi using a2enmod
a2enmod wsgi >/dev/null 2>&1

echo -n "INFO: Restarting Apache HTTPd..."
service apache2 restart >/dev/null 2>&1
echo " Done"
%endif

%postun -n ncf-api-virtualenv
#=================================================
# Post Uninstallation
#=================================================

# Do it only during uninstallation
if [ $1 -eq 0 ]; then
  # Remove the package user
  if getent passwd %{user_name} >/dev/null; then
    echo -n "INFO: Removing the %{user_name} user..."
    userdel %{user_name} >/dev/null 2>&1
    echo " Done"
  fi
fi

%if 0%{?rhel} || 0%{?fedora}
  # Do it only during uninstallation
  if [ $1 -eq 0 ]; then
    if type sestatus >/dev/null 2>&1
    then
      if [ $(semodule -l | grep -c ncf-api-virtualenv) -eq 0 ]
      then
        # Remove the ncf-api-virtualenv SELinux policy
        semodule -r ncf-api-virtualenv 2>/dev/null
      fi
    fi
  fi
%endif

#=================================================
# Cleaning
#=================================================
%clean
rm -rf %{buildroot}

#=================================================
# Files
#=================================================
%files -n ncf-api-virtualenv
%defattr(-, root, root, 0755)
%{installdir}/
%config(noreplace) %{apache_vhost_dir}/ncf-api-virtualenv.conf

#=================================================
# Changelog
#=================================================
%changelog
* Mon Jun 16 2014 - Matthieu CERDA <matthieu.cerda@normation.com> 0.2014160600-1
- Initial release
