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

.DEFAULT_GOAL := localdepends

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>
CFENGINE_RELEASE = 3.2.0
FUSION_RELEASE = 2.1.9
TMP_DIR := $(shell mktemp -dq)
WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget
PATCH := /usr/bin/patch

localdepends: ./initial-promises ./files ./fusioninventory-agent ./cfengine-source ../debian/rudder-agent.init ../debian/rudder-agent.default
	rm -rf $(TMP_DIR)

./cfengine-source: /usr/bin/wget
	# Original URL: http://cfengine.com/source-code/download?file=cfengine-$(CFENGINE_RELEASE).tar.gz
	$(WGET) -O $(TMP_DIR)/cfengine.tgz http://www.normation.com/tarball/cfengine-$(CFENGINE_RELEASE).tar.gz
	tar xvzf $(TMP_DIR)/cfengine.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/cfengine-$(CFENGINE_RELEASE) ./cfengine-source

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./initial-promises: ./rudder-sources
	cp -a ./rudder-sources/rudder-techniques/initial-promises/nodeInitialPromises/ ./initial-promises

./fusioninventory-agent: /usr/bin/wget
	#Original URL: http://search.cpan.org/CPAN/authors/id/F/FU/FUSINV/FusionInventory-Agent-$(FUSION_RELEASE).tar.gz
	$(WGET) -O $(TMP_DIR)/fusion.tgz http://www.normation.com/tarball/FusionInventory-Agent-$(FUSION_RELEASE).tar.gz
	tar zvxf $(TMP_DIR)/fusion.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/FusionInventory-Agent-$(FUSION_RELEASE) ./fusioninventory-agent
	$(PATCH) -d ./fusioninventory-agent -p1 < ./fusioninventory-os-section.patch
	$(PATCH) -d ./fusioninventory-agent -p1 < ./fusioninventory-centos-nolsb.patch

./files: /usr/bin/wget
	mkdir ./files
	#Original URL: http://www.cpan.org/modules/by-module/App/App-cpanminus-1.0004.tar.gz
	$(WGET) -O ./files/App-cpanminus-1.0004.tar.gz http://www.normation.com/tarball/App-cpanminus-1.0004.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/Archive/Archive-Extract-0.42.tar.gz
	$(WGET) -O ./files/Archive-Extract-0.42.tar.gz http://www.normation.com/tarball/Archive-Extract-0.42.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/Compress/Compress-Raw-Bzip2-2.027.tar.gz
	$(WGET) -O ./files/Compress-Raw-Bzip2-2.027.tar.gz http://www.normation.com/tarball/Compress-Raw-Bzip2-2.027.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/Compress/Compress-Raw-Zlib-2.027.tar.gz
	$(WGET) -O ./files/Compress-Raw-Zlib-2.027.tar.gz http://www.normation.com/tarball/Compress-Raw-Zlib-2.027.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/Crypt/Crypt-SSLeay-0.57.tar.gz
	$(WGET) -O ./files/Crypt-SSLeay-0.57.tar.gz http://www.normation.com/tarball/Crypt-SSLeay-0.57.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/Digest/Digest-MD5-2.39.tar.gz
	$(WGET) -O ./files/Digest-MD5-2.39.tar.gz http://www.normation.com/tarball/Digest-MD5-2.39.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/HTML/HTML-Parser-3.65.tar.gz
	$(WGET) -O ./files/HTML-Parser-3.65.tar.gz http://www.normation.com/tarball/HTML-Parser-3.65.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/HTML/HTML-Tagset-3.20.tar.gz
	$(WGET) -O ./files/HTML-Tagset-3.20.tar.gz http://www.normation.com/tarball/HTML-Tagset-3.20.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/IO/IO-Compress-2.027.tar.gz
	$(WGET) -O ./files/IO-Compress-2.027.tar.gz http://www.normation.com/tarball/IO-Compress-2.027.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/IO/IO-Socket-SSL-1.33.tar.gz
	$(WGET) -O ./files/IO-Socket-SSL-1.33.tar.gz http://www.normation.com/tarball/IO-Socket-SSL-1.33.tar.gz
	#Original URL: http://search.cpan.org/CPAN/authors/id/G/GA/GAAS/libwww-perl-5.836.tar.gz
	$(WGET) -O ./files/libwww-perl-5.836.tar.gz http://www.normation.com/tarball/libwww-perl-5.836.tar.gz
	#Orignal URL: http://www.cpan.org/modules/by-module/Net/Net-IP-1.25.tar.gz
	$(WGET) -O ./files/Net-IP-1.25.tar.gz http://www.normation.com/tarball/Net-IP-1.25.tar.gz
	#Original URL: http://www.cpan.org/src/5.0/perl-5.12.4.tar.gz
	$(WGET) -O ./files/perl-5.12.4.tar.gz http://www.normation.com/tarball/perl-5.12.4.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/UNIVERSAL/UNIVERSAL-require-0.13.tar.gz
	$(WGET) -O ./files/UNIVERSAL-require-0.13.tar.gz http://www.normation.com/tarball/UNIVERSAL-require-0.13.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/URI/URI-1.56.tar.gz
	$(WGET) -O ./files/URI-1.56.tar.gz http://www.normation.com/tarball/URI-1.56.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/XML/XML-SAX-0.96.tar.gz
	$(WGET) -O ./files/XML-SAX-0.96.tar.gz http://www.normation.com/tarball/XML-SAX-0.96.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/XML/XML-Simple-2.18.tar.gz
	$(WGET) -O ./files/XML-Simple-2.18.tar.gz http://www.normation.com/tarball/XML-Simple-2.18.tar.gz

../debian/rudder-agent.init:
	cp ./rudder-agent.init ../debian/

../debian/rudder-agent.default:
	cp ./rudder-agent.default ../debian/

/usr/bin/wget:
	sudo apt-get --assume-yes install wget

localclean:
	rm -rf ./cfengine-source
	rm -rf ./initial-promises
	rm -f ../debian/rudder-agent.init
	rm -f ../debian/rudder-agent.default
	rm -rf ./FusionInventory-Agent-$(FUSION_RELEASE)
	rm -f ./FusionInventory-Agent-$(FUSION_RELEASE).tar.gz
	rm -rf ./fusioninventory-agent
	rm -rf ./tmp
	rm -rf ./perl-custom
	rm -rf ./files
	rm -rf ./rudder-sources

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: localclean localdepends veryclean
