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

# This Makefile contains a call to prepare source dependencies (localdepends)
# Everything else dedicated to building RPM packages
# Building debian packages is done in the $(TOOLS_DIR)/build-package.makefile file

include $(TOOLS_DIR)/build-package.makefile

ARCHI := $(shell uname -m)
OS := $(shell . ../detect_os.sh && echo $${OS})
OSSP := $(shell . ../detect_os.sh && echo $${OSSP})
OSVERSION := $(shell . ../detect_os.sh && echo $${OSVERSION})

BUILDREQUIRESSLES := $(shell grep -s "SLES${OSVERSION}:" SOURCES/.dependencies | cut -d ':' -f2)
BUILDREQUIRESSLESSP := $(shell grep -s "SLES${OSVERSION}SP${OSSP}:" SOURCES/.dependencies | cut -d ':' -f2)
BUILDREQUIRESRHEL := $(shell grep -s "RHEL${OSVERSION}" SOURCES/.dependencies | cut -d ':' -f2)

JAVAREQUIRES := $(shell grep -s "JAVA" SOURCES/.dependencies | cut -d ':' -f2)

# Original URL: http://www.oracle.com/technetwork/java/javase/downloads/index-jsp-138363.html#javasejdk
JDKURL := https://repository.rudder.io/build-dependencies/java/jdk-8u101-linux-i586.rpm
JDKPACKAGE := jdk1.8.0_101
ifeq ($(ARCHI),x86_64)
JDKURL := https://repository.rudder.io/build-dependencies/java/jdk-8u101-linux-x86_64.rpm
endif

buildpackage-rpm-common-prep-suse:
	# Accept expired GPG Key for zypper on old SLES versions
	if [ "${OS}" = "SLES" -a "${OSVERSION}" = "10" ];then echo -e "y\ny" | zypper ref || true;fi
	if [ ! -z "${BUILDREQUIRESSLES}" ];then zypper -n install ${BUILDREQUIRESSLES};fi
	if [ ! -z "${BUILDREQUIRESSLESSP}" ];then zypper -n install ${BUILDREQUIRESSLESSP};fi
	# alternatives doesn't exist on sles11 but it is a rewrite of update-alternatives so this works
	ln -s /usr/sbin/update-alternatives /usr/sbin/alternatives || true
	if [ "$(JAVAREQUIRES)" = "jdk" ] && [ $$(rpm -qa $(JDKPACKAGE)|wc -l) -eq 0 ]; then wget -q -O /tmp/jdk.rpm $(JDKURL); rpm -ivh /tmp/jdk.rpm; fi

buildpackage-rpm-common-prep-rhel:
	# Add basic package to have macros for rpm and be able to know which part of .spec file concerns rhel 5
	if [ "${OS}" = "RHEL" -a "${OSVERSION}" = "5" ];then yum -y install buildsys-macros;fi
	if [ ! -z "${BUILDREQUIRESRHEL}" ];then yum -y install ${BUILDREQUIRESRHEL};fi

buildpackage-rpm-common-prep-aix:
	# Dependencies on AIX are currently not managed automatically but installed manually
	:

buildpackage-rpm-build-plainrpm:
	mkdir -p $(PWD)/tmp
	cp -f /root/.rpmmacros-orig /$(HOME)/.rpmmacros
	echo "%_topdir $(PWD)" >> /$(HOME)/.rpmmacros
	echo "%_tmppath $(PWD)/tmp" >> /$(HOME)/.rpmmacros
	echo "%real_version $(RUDDER_VERSION_RPM)" >> /$(HOME)/.rpmmacros
	rpm -ba SPECS/*.spec

buildpackage-rpm-build-rpmbuild:
	rpmbuild --define "_topdir $(PWD)" --define "real_version $(RUDDER_VERSION_RPM)" -ba SPECS/*.spec

buildpackage-rpm-aix:    buildpackage-rpm-common-prep-aix  buildpackage-rpm-build-plainrpm
buildpackage-rpm-suse:   buildpackage-rpm-common-prep-suse buildpackage-rpm-build-rpmbuild
buildpackage-rpm-rhel:   buildpackage-rpm-common-prep-rhel buildpackage-rpm-build-rpmbuild

buildpackage-slackware:
	cd slackware && VERSION=$(RUDDER_VERSION_SLACKWARE) TMP=$(pwd) ./rudder-agent.SlackBuild

.PHONY: buildpackage-rpm-suse buildpackage-rpm-rhel buildpackage-rpm-aix
