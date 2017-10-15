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

ARCHI := $(shell uname -m)
OS := $(shell . ../tools/detect_os.sh && echo $${OS})
OSSP := $(shell . ../tools/detect_os.sh && echo $${OSSP})
OSVERSION := $(shell . ../tools/detect_os.sh && echo $${OSVERSION})

BUILDREQUIRESSLES := $(shell grep -s "SLES${OSVERSION}:" SOURCES/.dependencies | cut -d ':' -f2)
BUILDREQUIRESSLESSP := $(shell grep -s "SLES${OSVERSION}SP${OSSP}:" SOURCES/.dependencies | cut -d ':' -f2)
BUILDREQUIRESRHEL := $(shell grep -s "RHEL${OSVERSION}" SOURCES/.dependencies | cut -d ':' -f2)
BUILDREQUIRESFEDORA := $(shell grep -s "FEDORA${OSVERSION}" SOURCES/.dependencies | cut -d ':' -f2)

JAVAREQUIRES := $(shell grep -s "JAVA" SOURCES/.dependencies | cut -d ':' -f2)

# Original URL: http://www.oracle.com/technetwork/java/javase/downloads/index-jsp-138363.html#javasejdk
JDKURL := http://www.normation.com/tarball/java/jdk-8u101-linux-i586.rpm
JDKPACKAGE := jdk1.8.0_101
ifeq ($(ARCHI),x86_64)
JDKURL := http://www.normation.com/tarball/java/jdk-8u101-linux-x86_64.rpm
endif

# Configuration: change these values as needed
ARCH = amd64
DISTRIBUTION = jessie
WORKDIR = /tmp/work
RESULTDIR = /tmp/result
PROXY = http://filer.interne.normation.com:3128
DEBMIRROR = http://mirrors.online.net/debian/
DEBCOMPONENTS = main
OTHERMIRROR_OPTIONS =
KEYRING = '/usr/share/keyrings/debian-archive-keyring.gpg'

# Other directory paths derived from main configuration above
CCACHEDIR = $(WORKDIR)/ccache
M2REPOSITORY = /tmp/m2-repository
BASETGZ = /srv/cache/pbuilder/base-debian-$(DISTRIBUTION)-$(ARCH).tgz

# This Makefile should be called with variables BUILD_ROOT and TOOLS_DIR defined

# Options to debootstrap a new environment: define mirror, distribution and arch.
PBUILDER_CREATE_OPTIONS = --distribution $(DISTRIBUTION) --mirror $(DEBMIRROR) --debootstrapopts --arch=$(ARCH) --components "$(DEBCOMPONENTS)" $(if $(LOCALDEBMIRROR), --othermirror "$(LOCALDEBMIRROR)")

# Options to use everytime pbuilder is called (including through pdebuild): proxy, and dirs
PBUILDER_OPTIONS = --basetgz "$(BASETGZ)" $(if $(PROXY), --http-proxy $(PROXY)) --buildplace "$(WORKDIR)" --configfile "$(WORKDIR)/pbuilderrc" --hookdir $(TOOLS_DIR)/pbuilder-hooks $(OTHERMIRROR_OPTIONS) --debootstrapopts '--variant=buildd' --debootstrapopts '--keyring' $(KEYRING)
 

# pdebuild specific options: arch for cross-arch-building and dirs
PDEBUILD_OPTIONS = --use-pdebuild-internal --arch $(ARCH) --buildresult "$(RESULTDIR)" --debbuildopts "-i -I"

# Clean up the environment
unexport JAVA_HOME
unexport JDK_HOME
unexport M2_HOME
unexport M2


.DEFAULT_GOAL := localbuild

localbuild: localdepends buildpackage-debian

localdepends: SOURCES/.stamp

depends: /usr/bin/dh_testdir /usr/bin/pdebuild /usr/bin/fakeroot /usr/share/keyrings/debian-archive-keyring.gpg

/usr/bin/dh_testdir:
	sudo apt-get update
	sudo apt-get --assume-yes install debhelper

/usr/bin/pdebuild:
	sudo apt-get update
	sudo apt-get --assume-yes install pbuilder

/usr/bin/fakeroot:
	sudo apt-get update
	sudo apt-get --assume-yes install fakeroot

/usr/share/keyrings/debian-archive-keyring.gpg:
	sudo apt-get update
	sudo apt-get --assume-yes install debian-archive-keyring

/usr/bin/expect:
	sudo apt-get update
	sudo apt-get --assume-yes install expect

init:
	mkdir -p "$(M2REPOSITORY)"
	mkdir -p "$(WORKDIR)"
	mkdir -p "$(RESULTDIR)"
	mkdir -p "$(CCACHEDIR)"
	cp "$(TOOLS_DIR)/pbuilderrc" "$(WORKDIR)/"

$(BASETGZ):
	sudo pbuilder --create $(PBUILDER_OPTIONS) $(PBUILDER_CREATE_OPTIONS) || rm -f "$(BASETGZ)"

buildpackage-debian: init depends $(CONFFILES) $(BASETGZ)
	"$(TOOLS_DIR)/pdebuild" $(PDEBUILD_OPTIONS) -- $(PBUILDER_OPTIONS)


SOURCES/.stamp:
	cd SOURCES && $(MAKE) localdepends
	touch SOURCES/.stamp

buildpackage-rpm-common-prep:

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

buildpackage-rpm-common-prep-fedora:
	if [ ! -z "${BUILDREQUIRESFEDORA}" ];then yum -y install ${BUILDREQUIRESFEDORA};fi

buildpackage-rpm-common-prep-aix:
	# Dependencies on AIX are currently not managed automatically but installed manually
	:

buildpackage-rpm-common-fix-old-epoch:
	# We used to use the epoch field of RPM spec files to manage version comparaisons
	# But we stopped doing this on the day with timestamp 1366900520
	sed -i "s@^%define real_epoch.*@%define real_epoch 1398866025@" SPECS/*.spec

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
	if [ -e debian/control ]; then for package in $$(awk '/^Source: / {print $$2}' debian/control); do rm -f $(BUILD_ROOT)/$${package}*.*; done; fi
	if [ -e debian/control ]; then for package in $$(awk '/^Package: / {print $$2}' debian/control); do rm -f $(BUILD_ROOT)/$${package}*.*; done; fi
	if [ -d BUILD ]; then rm -rf BUILD/*; fi
	if [ -e debian/rules ]; then fakeroot debian/rules clean; fi

localclean:
	cd SOURCES && $(MAKE) localclean
	rm -f SOURCES/.stamp

veryclean:
	cd SOURCES && $(MAKE) veryclean

.PHONY: localclean localbuild localdepends veryclean buildpackage-rpm-suse buildpackage-rpm-rhel buildpackage-rpm-aix buildpackage-rpm-fedora init buildpackage-debian clean depends
