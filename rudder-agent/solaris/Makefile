#####################################################################################
# Copyright 2015 Normation SAS
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

# run with LC_ALL=C gmake build RUDDER_VERSION_TO_PACKAGE=3.2.0.alpha1.git201507221630 [ARCH=...]
# build dependencies : pkgutil -i -y gcc4core findutils gtar pcre libpcre_dev
#     and gsed gmake ginstall gpatch wget or curl commands

ARCH=i386
RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>
ROOTPATH = $(shell dirname $(CURDIR))
SOURCES = $(ROOTPATH)/SOURCES
BUILDROOT = $(ROOTPATH)/tmp
PKGROOT = $(BUILDROOT)/rudder-agent
PACKAGE = RudderAgent.$(RUDDER_VERSION_TO_PACKAGE).$(ARCH).pkg.tar.gz

build: package

package: build-rudder
	# Create prototype file that contains included files lis# Create prototype file that contains included files list
	cd $(BUILDROOT) && find rudder-agent | grep -v '^rudder-agent$$' | pkgproto | sed 's/ rudder-agent/ /' > Prototype.tmp
	sed '/none \/\(etc|etc\/cron.d|etc\/default|etc\/init.d|opt|usr|usr\/bin|var|var\/log\) /d' $(BUILDROOT)/Prototype.tmp > $(BUILDROOT)/Prototype.tmp2
	cat $(CURDIR)/Prototype.base $(BUILDROOT)/Prototype.tmp2 > $(BUILDROOT)/Prototype
	rm $(BUILDROOT)/Prototype.tmp

	# Create package information file
	pkgdata=`cat $(CURDIR)/pkginfo` date=`date '+%m%d%Y'` arch=$(ARCH) version=$(RUDDER_VERSION_TO_PACKAGE) && eval "echo \"$$pkgdata\"" > $(BUILDROOT)/pkginfo 

	# Retreive postinst et al scripts
	cp $(CURDIR)/checkinstall $(BUILDROOT)/
	cp $(CURDIR)/preremove $(BUILDROOT)/
	cp $(CURDIR)/postinstall $(BUILDROOT)/
	cp $(CURDIR)/postremove $(BUILDROOT)/

	# Create the package content description file
	pkgmk -o -r $(PKGROOT) -d $(BUILDROOT) -f $(BUILDROOT)/Prototype

	# create the final package file as a tgz
	cd $(BUILDROOT) && tar -cf - RudderAgent | gzip -9 -c > $(PACKAGE)
	mv $(BUILDROOT)/$(PACKAGE) $(ROOTPATH)/

	# create the final package file as a pkg
	pkgtrans -s $(BUILDROOT) $(ROOTPATH)/RudderAgent.pkg RudderAgent


build-rudder:
	rm -rf $(BUILDROOT)
	mkdir $(BUILDROOT)

	# Build rudder agent and install to a temporary destination
	cd $(SOURCES) && $(MAKE) install DESTDIR=$(PKGROOT) RUDDER_VERSION_TO_PACKAGE=$(RUDDER_VERSION_TO_PACKAGE)
	rm -rf $(PKGROOT)/etc/ld.so.conf.d/
