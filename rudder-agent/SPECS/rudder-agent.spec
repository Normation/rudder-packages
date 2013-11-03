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
%define real_name        rudder-agent

%define rudderdir        /opt/rudder
%define ruddervardir     /var/rudder
%define rudderlogdir     /var/log/rudder

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
Source5: check-rudder-agent

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

#Specific requirements
%if 0%{?sles_version} == 11
BuildRequires: db43-devel
Requires: db43 pmtools
%endif

%if 0%{?sles_version} == 10
BuildRequires: db42-devel
Requires: db42 pmtools
%endif

%if 0%{?sles_version}
Requires: cron
%endif

%if 0%{?rhel}
BuildRequires: make db4-devel byacc
Requires: db4 dmidecode crontabs
%endif

# Replaces rudder-cfengine-community since 2.4.0~beta3
Provides: rudder-cfengine-community
Obsoletes: rudder-cfengine-community

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

cd %{_sourcedir}/cfengine-source

# Ensure an appropriate environment for the compiler
export CFLAGS="$RPM_OPT_FLAGS"
export CXXFLAGS="$RPM_OPT_FLAGS"
%if 0%{?sles_version} == 10
export BERKELEYDB_LIBS=-ldb-4.2
export BERKELEYDB_CFLAGS=-I/usr/include/db42
%endif
%if 0%{?sles_version} == 11
export BERKELEYDB_LIBS=-ldb-4.3
export BERKELEYDB_CFLAGS=-I/usr/include/db43
%endif

./configure --build=%_target --prefix=%{rudderdir} --with-workdir=%{ruddervardir}/cfengine-community --enable-static=yes --enable-shared=no

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
mkdir -p %{buildroot}%{ruddervardir}/tmp
mkdir -p %{buildroot}%{ruddervardir}/tools

# Init script
mkdir -p %{buildroot}/etc/init.d
mkdir -p %{buildroot}/etc/default
install -m 755 %{SOURCE1} %{buildroot}/etc/init.d/rudder-agent
install -m 644 %{SOURCE2} %{buildroot}/etc/default/rudder-agent

# Initial promises
cp -a %{_sourcedir}/initial-promises %{buildroot}%{rudderdir}/share/

# Fusion
cp -a %{_sourcedir}/perl-custom/opt/rudder/* %{buildroot}%{rudderdir}

# Wrapper script
install -m 755 %{SOURCE3} %{buildroot}/opt/rudder/bin/run-inventory

# Install an empty uuid.hive file before generating an uuid
cp %{SOURCE4} %{buildroot}%{rudderdir}/etc/

install -m 755 %{SOURCE5} %{buildroot}/opt/rudder/bin/check-rudder-agent

%pre -n rudder-agent
#=================================================
# Pre Installation
#=================================================

# Do this only during upgrade process
if [ $1 -eq 2 ];then
	# Keep a backup copy of Rudder agent init and cron files to prevent http://www.rudder-project.org/redmine/issues/3995
	mkdir -p /var/backups/rudder
	cp -af /etc/init.d/rudder-agent /var/backups/rudder/rudder-agent.init-$(date +%Y%m%d)
	echo "INFO: A back up copy of the /etc/init.d/rudder-agent has been created in /var/backups/rudder"
	cp -af /etc/default/rudder-agent /var/backups/rudder/rudder-agent.default-$(date +%Y%m%d)
	echo "INFO: A back up copy of the /etc/default/rudder-agent has been created in /var/backups/rudder"
fi

%post -n rudder-agent
#=================================================
# Post Installation
#=================================================

CFRUDDER_FIRST_INSTALL=0

# Do this at first install
if [ $1 -eq 1 ]
then
	# Set rudder-agent as service
	/sbin/chkconfig --add rudder-agent

	CFRUDDER_FIRST_INSTALL=1
fi

# Always do this

# Copy new binaries to workdir, make sure daemons are stopped first

# Set a "lock" to avoid CFEngine being restarted during the upgrade process
I_SET_THE_LOCK=0
if [ ! -e /opt/rudder/etc/disable-agent ]; then
	I_SET_THE_LOCK=1
	touch /opt/rudder/etc/disable-agent
fi

if [ ${CFRUDDER_FIRST_INSTALL} -ne 1 -a -x /etc/init.d/rudder-agent ]; then /etc/init.d/rudder-agent stop; fi

# Copy CFEngine binaries
cp -a -f /opt/rudder/sbin/cf-* /var/rudder/cfengine-community/bin/
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
	# Check if agent is disabled
	if [ ! -f /opt/rudder/etc/disable-agent ]
	then
		if [ -r /var/rudder/cfengine-community/inputs/failsafe.cf -o -r /var/rudder/cfengine-community/inputs/promises.cf ]
		then
			/sbin/service rudder-agent start
		fi
	else
		echo "********************************************************************************"
		echo "rudder-agent has been updated, but was not started as it is disabled."
		echo "To enable rudder agent, you have to remove disable file, and start rudder-agent:"
		echo "# rm -f /opt/rudder/etc/disable-agent"
		echo "# /sbin/service rudder-agent start"
		echo "********************************************************************************"
	fi
else
	echo "********************************************************************************"
	echo "rudder-agent has been installed (not started). This host can be a Rudder node."
	echo "To get started, configure your Rudder server's hostname and launch the agent:"
	echo "# echo 'rudder.server' > /var/rudder/cfengine-community/policy_server.dat"
	echo "# /etc/init.d/rudder-agent start"
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
%{ruddervardir}

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
