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

CFENGINE_RELEASE = 3.6.0
FUSION_RELEASE = 2.3.6
LMDB_RELEASE = 0.9.11
OPENSSL_RELEASE = 1.0.1i

TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX)
WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget -q
PATCH := /usr/bin/patch
FIND := /usr/bin/find

localdepends: ./initial-promises ./detect_os.sh ./files ./fusioninventory-agent ./cfengine-source ./openssl-source ./lmdb-source ../debian/rudder-agent.init ../debian/rudder-agent.default ./rudder-agent.cron ../debian/rudder-agent.cron.d
	rm -rf $(TMP_DIR)

./cfengine-source: /usr/bin/wget
	# Original URL: https://s3.amazonaws.com/cfengine.package-repos/tarballs/cfengine-$(CFENGINE_RELEASE).tar.gz
	$(WGET) -O $(TMP_DIR)/cfengine.tgz http://www.normation.com/tarball/cfengine/cfengine-$(CFENGINE_RELEASE).tar.gz
	tar xzf $(TMP_DIR)/cfengine.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/cfengine-$(CFENGINE_RELEASE) ./cfengine-source
	# Apply patches
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0001-fix-unsupported-openssl-options.patch
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0002-explicitely-use-pthreads-during-lmdb-presence-detection.patch
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0003-fix-fprintf-usage-on-old-gcc-versions.patch
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0004-fix-zero-sized-files-from-template-when-nolocks.patch
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0005-fix-readstringarrayidx-duplicate-lines.patch
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0006-openvz-support.patch
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0007-no-runlog.patch
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0008-fix-promise-evaluation.patch
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0009-dont-duplicate-text-blocks.patch
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0010-support-large-int.patch
	$(PATCH) -d ./cfengine-source -p1 < ./patches/cfengine/0011-cfserverd_understands_SIGHUP.patch

	# Bootstrap the package using autogen before compilation
	cd cfengine-source && NO_CONFIGURE=1 ./autogen.sh

./openssl-source: /usr/bin/wget
	# Original URL: https://www.openssl.org/source/openssl-$(OPENSSL_RELEASE).tar.gz
	$(WGET) -O $(TMP_DIR)/openssl.tgz http://www.normation.com/tarball/openssl/openssl-$(OPENSSL_RELEASE).tar.gz
	tar xzf $(TMP_DIR)/openssl.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/openssl-$(OPENSSL_RELEASE) ./openssl-source

./lmdb-source: /usr/bin/wget
	# Original URL: http://ftp.fr.debian.org/debian/pool/main/l/lmdb/lmdb_$(LMDB_RELEASE).orig.tar.xz
	$(WGET) -O $(TMP_DIR)/lmdb.tgz http://www.normation.com/tarball/lmdb-$(LMDB_RELEASE).tar.gz
	tar xzf $(TMP_DIR)/lmdb.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/lmdb-$(LMDB_RELEASE) ./lmdb-source

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-$(RUDDER_VERSION_TO_PACKAGE).tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./initial-promises: ./rudder-sources
	rm -rf ./initial-promises/
	cp -a ./rudder-sources/rudder-techniques/initial-promises/node-server/ ./initial-promises

# Needed for perl-prepare.sh
./detect_os.sh: ./rudder-sources
	cp ./rudder-sources/rudder-packages/detect_os.sh ./detect_os.sh

./fusioninventory-agent: /usr/bin/wget
	#Original URL: http://search.cpan.org/CPAN/authors/id/G/GR/GROUSSE/FusionInventory-Agent-$(FUSION_RELEASE).tar.gz
	$(WGET) -O $(TMP_DIR)/fusion.tgz http://www.normation.com/tarball/FusionInventory-Agent-$(FUSION_RELEASE).tar.gz
	tar zxf $(TMP_DIR)/fusion.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/FusionInventory-Agent-$(FUSION_RELEASE) ./fusioninventory-agent
	$(PATCH) -d ./fusioninventory-agent -p1 < ./patches/fusioninventory/0001-4096-char-line-truncation.patch
	$(PATCH) -d ./fusioninventory-agent -p1 < ./patches/fusioninventory/0002-install-d-mkdir-p.patch
	$(PATCH) -d ./fusioninventory-agent -p1 < ./patches/fusioninventory/0003-unix-ps-etime-usage.patch
	$(PATCH) -d ./fusioninventory-agent -p1 < ./patches/fusioninventory/0004-aix-microcode-version-retrieval.patch
	$(PATCH) -d ./fusioninventory-agent -p1 < ./patches/fusioninventory/0005-aix-duplicated-network-interfaces.patch
	$(PATCH) -d ./fusioninventory-agent -p1 < ./patches/fusioninventory/0006-fixes-oracle-linux-os-name.patch
	$(PATCH) -d ./fusioninventory-agent -p1 < ./patches/fusioninventory/0007-correct-storage-size-detection.patch
	$(PATCH) -d ./fusioninventory-agent -p1 < ./patches/fusioninventory/0008-detect-docker-containers.patch
	# Fix a lsusb invocation that crashes some SLES machines
	$(FIND) ./fusioninventory-agent -iname "USB.pm" -exec rm "{}" \;

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
	#Original URL: http://www.cpan.org/modules/by-module/File/File-Which-1.09.tar.gz
	$(WGET) -O ./files/File-Which-1.09.tar.gz http://www.normation.com/tarball/File-Which-1.09.tar.gz
	#Original URL: http://www.cpan.org/modules/by-module/XML/XML-TreePP-0.41.tar.gz
	$(WGET) -O ./files/XML-TreePP-0.41.tar.gz http://www.normation.com/tarball/XML-TreePP-0.41.tar.gz
	#Original URL: http://search.cpan.org/CPAN/authors/id/P/PE/PERIGRIN/XML-NamespaceSupport-1.11.tar.gz
	$(WGET) -O ./files/XML-NamespaceSupport-1.11.tar.gz http://www.normation.com/tarball/XML-NamespaceSupport-1.11.tar.gz
	#Original URL: http://search.cpan.org/CPAN/authors/id/A/AD/ADAMK/Test-Script-1.07.tar.gz
	$(WGET) -O ./files/Test-Script-1.07.tar.gz http://www.normation.com/tarball/Test-Script-1.07.tar.gz
	#Original URL: http://search.cpan.org/CPAN/authors/id/K/KW/KWILLIAMS/Probe-Perl-0.03.tar.gz
	$(WGET) -O ./files/Probe-Perl-0.03.tar.gz http://www.normation.com/tarball/Probe-Perl-0.03.tar.gz
	#Original URL: http://search.cpan.org/CPAN/authors/id/R/RJ/RJBS/IPC-Run3-0.048.tar.gz
	$(WGET) -O ./files/IPC-Run3-0.048.tar.gz http://www.normation.com/tarball/IPC-Run3-0.048.tar.gz

../debian/rudder-agent.init:
	cp ./rudder-agent.init ../debian/

../debian/rudder-agent.default:
	cp ./rudder-agent.default ../debian/

./rudder-agent.cron: ./rudder-sources
	cp ./rudder-sources/rudder-techniques/techniques/system/common/1.0/rudder_agent_community_cron.st ./rudder-agent.cron
	# Set unexpanded variables of the cron file
	sed 's@\$${sys.workdir}@/var/rudder/cfengine-community@g' -i rudder-agent.cron
	sed 's@\$${g.rudder_base}@/opt/rudder@g' -i rudder-agent.cron
	sed  's@\\&\\&@\&\&@g' -i rudder-agent.cron
	sed  's@\\&1@\&1@g' -i rudder-agent.cron

../debian/rudder-agent.cron.d: ./rudder-agent.cron
	cp ./rudder-agent.cron ../debian/rudder-agent.cron.d

/usr/bin/wget:
	sudo apt-get --assume-yes install wget

localclean:
	rm -rf ./cfengine-source
	rm -rf ./lmdb-source
	rm -rf ./initial-promises
	rm -rf ./detect_os.sh
	rm -f ../debian/rudder-agent.init
	rm -f ../debian/rudder-agent.default
	rm -rf ./fusioninventory-agent
	rm -rf ./tmp
	rm -rf ./perl-custom
	rm -rf ./files
	rm -rf ./rudder-sources
	rm -f ./rudder-agent.cron ../debian/rudder-agent.cron.d

veryclean:
	rm -f ./rudder-sources.tar.bz2

.PHONY: localclean localdepends veryclean
