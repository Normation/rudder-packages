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
BUILDREQUIRESFEDORA := $(shell grep -s "FEDORA${OSVERSION}" SOURCES/.dependencies | cut -d ':' -f2)

JAVAREQUIRES := $(shell grep -s "JAVA" SOURCES/.dependencies | cut -d ':' -f2)

# Original URL: http://www.oracle.com/technetwork/java/javase/downloads/index-jsp-138363.html#javasejdk
JDKURL := http://www.normation.com/tarball/java/jdk-7u71-linux-i586.rpm

ifeq ($(ARCHI),x86_64)
JDKURL := http://www.normation.com/tarball/java/jdk-7u71-linux-x86_64.rpm
endif


.DEFAULT_GOAL := localbuild

localbuild: localdepends buildpackage-debian

localdepends: SOURCES/.stamp

SOURCES/.stamp:
	cd SOURCES && $(MAKE) localdepends
	touch SOURCES/.stamp

buildpackage-rpm-common-prep:
	# As of now, only SLES requires this, the other OSes provide a recent enough JDK.
	if [ "z$(JAVAREQUIRES)" = "zjdk" ] && [ $$(rpm -qa jdk|wc -l) -eq 0 ]; then wget -q -O /tmp/jdk.rpm $(JDKURL); rpm -ivh /tmp/jdk.rpm; fi

buildpackage-rpm-common-prep-suse:
	# Accept expired GPG Key for zypper on old SLES versions
	if [ "z${OS}" = "zSLES" -a "z${OSVERSION}" = "z10" ];then echo -e "y\ny" | zypper ref || true;fi
	if [ ! -z "${BUILDREQUIRESSLES}" ];then zypper -n install ${BUILDREQUIRESSLES};fi
	if [ ! -z "${BUILDREQUIRESSLESSP}" ];then zypper -n install ${BUILDREQUIRESSLESSP};fi

buildpackage-rpm-common-prep-rhel:
	# Add basic package to have macros for rpm and be able to know which part of .spec file concerns rhel 5
	if [ "z${OS}" = "zRHEL" -a "z${OSVERSION}" = "z5" ];then yum -y install buildsys-macros;fi
	if [ ! -z "${BUILDREQUIRESRHEL}" ];then yum -y install ${BUILDREQUIRESRHEL};fi

buildpackage-rpm-common-prep-fedora:
	if [ ! -z "${BUILDREQUIRESFEDORA}" ];then yum -y install ${BUILDREQUIRESFEDORA};fi

buildpackage-rpm-common-prep-aix:
	# Dependencies on AIX are currently not managed automatically but installed manually
	:

buildpackage-rpm-common-fix-old-epoch:
	# We used to use the epoch field of RPM spec files to manage version comparaisons
	# But we stopped doing this on the day with timestamp 1366900520
	sed -i "s@^Epoch.*@Epoch: 1398866025@" SPECS/*.spec

buildpackage-rpm-build-plainrpm:
	mkdir -p $(PWD)/tmp
	cp -f /root/.rpmmacros-orig /$(HOME)/.rpmmacros
	echo "%_topdir $(PWD)" >> /$(HOME)/.rpmmacros
	echo "%_tmppath $(PWD)/tmp" >> /$(HOME)/.rpmmacros
	echo "%real_version $(RUDDER_VERSION_RPM)" >> /$(HOME)/.rpmmacros
	rpm -ba SPECS/*.spec

buildpackage-rpm-build-rpmbuild:
	rpmbuild --define "_topdir $(PWD)" --define "real_version $(RUDDER_VERSION_RPM)" -ba SPECS/*.spec

buildpackage-rpm-aix:  localdepends buildpackage-rpm-common-prep buildpackage-rpm-common-prep-aix  buildpackage-rpm-build-plainrpm
buildpackage-rpm-suse: localdepends buildpackage-rpm-common-prep buildpackage-rpm-common-prep-suse buildpackage-rpm-common-fix-old-epoch buildpackage-rpm-build-rpmbuild
buildpackage-rpm-rhel: localdepends buildpackage-rpm-common-prep buildpackage-rpm-common-prep-rhel buildpackage-rpm-common-fix-old-epoch buildpackage-rpm-build-rpmbuild
buildpackage-rpm-fedora: localdepends buildpackage-rpm-common-prep buildpackage-rpm-common-prep-fedora buildpackage-rpm-common-fix-old-epoch buildpackage-rpm-build-rpmbuild

clean: localclean
localclean:
	cd SOURCES && $(MAKE) localclean
	rm -f SOURCES/.stamp

veryclean:
	cd SOURCES && $(MAKE) veryclean

.PHONY: localclean localbuild localdepends veryclean buildpackage-rpm-suse buildpackage-rpm-rhel buildpackage-rpm-aix buildpackage-rpm-fedora
