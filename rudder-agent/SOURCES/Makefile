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

.DEFAULT_GOAL := build

# Versions to use
RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>
CFENGINE_RELEASE = 3.7.1
FUSION_RELEASE = 2.3.6
LMDB_RELEASE = 0.9.16
OPENSSL_RELEASE = 1.0.1p
PERL_VERSION = 5.22.0

# Defauth PATHs
RUDDER_DIR = /opt/rudder
DESTDIR = $(CURDIR)/target
INSTALL_DIR = $(DESTDIR)$(RUDDER_DIR)
TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX)

TRY_LDFLAGS=-pie -Wl,-z,relro -Wl,-z,now
TRY_CFLAGS=-fPIE -fstack-protector

# Autodetect wget or curl or curl usage and proxy configuration
PROXY_ENV = $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY))
WGET = wget -q -O
CURL = curl -s -o
FETCH = fetch -q -o
ifneq (,$(wildcard /usr/bin/curl))
GET = $(PROXY_ENV) $(CURL)
GET_OPT = --curl
else
ifneq (,$(wildcard /usr/bin/fetch))
GET = $(PROXY_ENV) $(FETCH)
else
GET = $(PROXY_ENV) $(WGET)
GET_OPT = --wget
endif
endif

# Autodtect presence of gnu tools
TAR := $(shell type gtar >/dev/null 2>&1 && echo gtar || echo tar)
PATCH := $(shell type gpatch >/dev/null 2>&1 && echo gpatch || echo patch)
SED := $(shell type gsed >/dev/null 2>&1 && echo gsed || echo sed)
INSTALL := $(shell type ginstall >/dev/null 2>&1 && echo ginstall || echo install)
CP_A := cp -rp
FIND := find

# Use parameters to guess what should be packaged
BUILD_DEPS :=
INSTALL_DEPS :=
# default: build openssl
ifneq (true,$(USE_SYSTEM_OPENSSL))
BUILD_DEPS := $(BUILD_DEPS) build-ssl
INSTALL_DEPS := $(INSTALL_DEPS) install-ssl
OPENSSL_ARG := --with-openssl=$(CURDIR)/build-ssl/opt/rudder
endif
# default: build lmdb
ifneq (true,$(USE_SYSTEM_LMDB))
BUILD_DEPS := $(BUILD_DEPS) build-lmdb
INSTALL_DEPS := $(INSTALL_DEPS) install-lmdb
LMDB_ARG := --with-lmdb=$(CURDIR)/build-lmdb/opt/rudder
endif
# default: build perl
ifneq (true,$(USE_SYSTEM_PERL))
BUILD_DEPS := $(BUILD_DEPS) build-perl
FUSION_DEPS := install-perl
PERL:=$(INSTALL_DIR)/bin/perl
else
FUSION_DEPS := cpan-source
PERL := /usr/bin/perl
endif

# Hack needed because openssl is not guessing correctly the architecture on solaris 32bits
ifeq (i386-pc-solaris2.10,$(shell ./config.guess))
SSL_CONFIGURE:=./Configure solaris-x86-gcc
else
SSL_CONFIGURE:=./config
endif

# download dependencies
depend: localdepends
localdepends: initial-promises rudder-agent-utilities perl-$(PERL_VERSION) fusioninventory-agent cfengine-source openssl-source lmdb-source rudder-agent.cron
	rm -rf $(TMP_DIR)

# build binaries
build: build-cfengine

# install to DESTDIR
install: build $(INSTALL_DEPS) install-fusion install-cfengine initial-promises rudder-agent-utilities rudder-agent.cron
	# Directories
	mkdir -p $(INSTALL_DIR)/etc
	mkdir -p $(INSTALL_DIR)/bin
	mkdir -p $(INSTALL_DIR)/share/commands
	mkdir -p $(DESTDIR)/var/rudder/cfengine-community/bin
	mkdir -p $(DESTDIR)/var/rudder/cfengine-community/inputs
	mkdir -p $(DESTDIR)/var/rudder/tmp
	mkdir -p $(DESTDIR)/var/rudder/tools
	mkdir -p $(DESTDIR)/var/log/rudder/install
	mkdir -p $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/etc/cron.d

	# Init files
ifneq (true,$(NO_INIT))
	mkdir -p $(DESTDIR)/etc/init.d
	mkdir -p $(DESTDIR)/etc/default
	$(INSTALL) -m 755 rudder-agent.init $(DESTDIR)/etc/init.d/rudder-agent
	$(INSTALL) -m 755 rudder.init $(DESTDIR)/etc/init.d/rudder
endif

	# cron files
ifneq (true,$(NO_CRON))
	$(INSTALL) -m 644 rudder-agent.cron $(DESTDIR)/etc/cron.d/rudder-agent
endif

	# Wrapper script
	$(INSTALL) -m 755 run-inventory $(INSTALL_DIR)/bin/

	# Signature script
	$(INSTALL) -m 755 signature.sh $(INSTALL_DIR)/bin/

	# Install an empty uuid.hive file before generating an uuid
	$(INSTALL) -m 644 uuid.hive $(INSTALL_DIR)/etc/

	# Install /etc/ld.so.conf.d/rudder.conf in order to use libraries
	# contained in /opt/rudder/lib like LMDB or OpenSSL
	# (ld.so.conf.d is not supported on RHEL/CentOS 3 and aix)
	mkdir -p $(DESTDIR)/etc/ld.so.conf.d
	$(INSTALL) -m 644 rudder.conf $(DESTDIR)/etc/ld.so.conf.d/

	mkdir -p $(DESTDIR)/opt/rudder/share/package-scripts
	$(INSTALL) -m 755 rudder-agent-postinst $(DESTDIR)/opt/rudder/share/package-scripts/
	$(INSTALL) -m 755 check-rudder-agent $(DESTDIR)/opt/rudder/bin/
	$(INSTALL) -m 755 vzps.py $(DESTDIR)/opt/rudder/bin/
	$(INSTALL) -m 755 rudder-perl $(DESTDIR)/opt/rudder/bin/

	# Rudder agent utilities
	$(INSTALL) -m 755 rudder-agent-utilities/bin/rudder $(INSTALL_DIR)/bin/
	$(INSTALL) -m 755 rudder-agent-utilities/share/commands/* $(INSTALL_DIR)/share/commands/

	# Create a symlink to make "rudder" available as part of the default PATH
	ln -sf $(RUDDER_DIR)/bin/rudder $(DESTDIR)/usr/bin/rudder

	# Install a profile script to make cf-* part of the PATH
ifneq (true,$(NO_PROFILE))
	mkdir -p $(DESTDIR)/etc/profile.d
	$(INSTALL) -m 644 rudder-agent.sh $(DESTDIR)/etc/profile.d/
endif

	# Install a uuidgen script just in case the original one doesn't exist
	$(INSTALL) -m 755 uuidgen $(INSTALL_DIR)/bin/

	cp -r initial-promises/ $(INSTALL_DIR)/share/

# clean 
clean: localclean
localclean:
	rm -rf $(DESTDIR)
	rm -rf build-ssl build-lmdb build-cfengine build-perl fusion-modules
	[ -d cfengine-source ] && cd cfengine-source && $(MAKE) clean 2>/dev/null || true
	[ -d lmdb-source ] && cd lmdb-source && $(MAKE) clean 2>/dev/null || true
	[ -d openssl-source ] && cd openssl-source && $(MAKE) clean 2>/dev/null || true
	[ -d perl-$(PERL_VERSION) ] && cd perl-$(PERL_VERSION) && $(MAKE) distclean 2>/dev/null || true
	rm -rf ./$(TMP_DIR)

# standard name is mrproper
mrproper: veryclean
veryclean:
	rm -f rudder-agent.cron
	rm -f ./rudder-sources.tar.bz2
	rm -rf rudder-sources
	rm -rf initial-promises rudder-agent-utilities fusioninventory-agent
	rm -rf cfengine-source lmdb-source openssl-source perl-$(PERL_VERSION)
	rm -rf ./$(TMP_DIR)

##########################################
# Dependencies separated into components #
##########################################

cfengine-source:
ifeq ($(shell ../../build-caching get --force-config ./cfengine-source/ name=cfengine-src version=$(CFENGINE_RELEASE) >/dev/null 2>&1 || echo KO), KO)
	# Original URL: https://cfengine-package-repos.s3.amazonaws.com/tarballs/cfengine-3.7.1.tar.gz
	$(GET) $(TMP_DIR)/cfengine.tgz http://www.normation.com/tarball/cfengine/cfengine-$(CFENGINE_RELEASE).tar.gz
	gunzip < $(TMP_DIR)/cfengine.tgz | $(TAR) xf -
	mv ./cfengine-$(CFENGINE_RELEASE) ./cfengine-source
	../../build-caching put --force-config ./cfengine-source/ name=cfengine-src version=$(CFENGINE_RELEASE)
endif

	# Apply patches
	for PATCHNAME in patches/cfengine/*.patch; do echo "Applying $$PATCHNAME..."; $(PATCH) -d ./cfengine-source -p1 < $$PATCHNAME; echo ""; done
	# Make sure there were no rejects
	test `$(FIND) ./cfengine-source -name \*.rej | wc -l` = 0

openssl-source:
ifeq ($(shell ../../build-caching get --force-config ./openssl-source/ name=openssl-src version=$(OPENSSL_RELEASE) >/dev/null 2>&1 || echo KO), KO)
	# Original URL: https://www.openssl.org/source/openssl-$(OPENSSL_RELEASE).tar.gz
	$(GET) $(TMP_DIR)/openssl.tgz http://www.normation.com/tarball/openssl/openssl-$(OPENSSL_RELEASE).tar.gz
	gunzip < $(TMP_DIR)/openssl.tgz | $(TAR) xf -
	mv ./openssl-$(OPENSSL_RELEASE) ./openssl-source
	../../build-caching put --force-config ./openssl-source/ name=openssl-src version=$(OPENSSL_RELEASE)
endif

lmdb-source:
ifeq ($(shell ../../build-caching get --force-config ./lmdb-source/ name=lmdb-src version=$(LMDB_RELEASE) >/dev/null 2>&1 || echo KO), KO)
	# Original URL: http://ftp.fr.debian.org/debian/pool/main/l/lmdb/lmdb_$(LMDB_RELEASE).orig.tar.xz
	$(GET) $(TMP_DIR)/lmdb.tgz http://www.normation.com/tarball/lmdb/lmdb-$(LMDB_RELEASE).tar.gz
	gunzip < $(TMP_DIR)/lmdb.tgz | $(TAR) xf -
	mv ./lmdb-$(LMDB_RELEASE) ./lmdb-source
	../../build-caching put --force-config ./lmdb-source/ name=lmdb-src version=$(LMDB_RELEASE)
endif

rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-$(RUDDER_VERSION_TO_PACKAGE).tar.bz2

rudder-sources: rudder-sources.tar.bz2
	bunzip2 < rudder-sources.tar.bz2 | $(TAR) xf -
	mv rudder-sources-$(RUDDER_VERSION_TO_PACKAGE)*/ rudder-sources/ # the '*' is needed for nightly release
	touch rudder-sources # to make it younger than the bzip source file

initial-promises: ./rudder-sources
	rm -rf ./initial-promises/
	cp -r ./rudder-sources/rudder-techniques/initial-promises/node-server/ ./initial-promises

rudder-agent-utilities: rudder-sources
	rm -rf ./rudder-agent-utilities/
	cp -r ./rudder-sources/rudder-agent/ ./rudder-agent-utilities

fusioninventory-agent:
ifeq ($(shell ../../build-caching get --force-config ./fusioninventory-agent/ name=fusioninventory-agent version=$(FUSION_RELEASE) >/dev/null 2>&1 || echo KO), KO)
	#Original URL: http://search.cpan.org/CPAN/authors/id/G/GR/GROUSSE/FusionInventory-Agent-$(FUSION_RELEASE).tar.gz
	$(GET) $(TMP_DIR)/fusion.tgz http://www.normation.com/tarball/FusionInventory-Agent-$(FUSION_RELEASE).tar.gz
	gunzip < $(TMP_DIR)/fusion.tgz | $(TAR) xf -
	mv ./FusionInventory-Agent-$(FUSION_RELEASE) ./fusioninventory-agent
	../../build-caching put --force-config ./fusioninventory-agent/ name=fusioninventory-agent version=$(FUSION_RELEASE)
endif

	# Apply patches
	for PATCHNAME in patches/fusioninventory/*.patch; do echo "Applying $$PATCHNAME... on FusionInventory"; $(PATCH) -d ./fusioninventory-agent -p1 < $$PATCHNAME; done
	# Make sure there were no rejects
	test `$(FIND) ./fusioninventory-agent -name \*.rej | wc -l` = 0

	# Fix a lsusb invocation that crashes some SLES machines
	$(FIND) ./fusioninventory-agent -name "USB.pm" -exec rm "{}" \;

# WARNING: Increment perl_source when changing one of the URLs (perl or cpanminus)
perl_source=002
perl-source: perl-$(PERL_VERSION)
perl-$(PERL_VERSION):
ifeq ($(shell ../../build-caching get --force-config ./perl-$(PERL_VERSION)/ name=perl-source versions=$(perl_source) >/dev/null 2>&1 || echo KO), KO)
	# Original URL: http://www.cpan.org/src/5.0/perl-5.22.0.tar.gz
	$(GET) $(TMP_DIR)/perl.tar.gz http://www.normation.com/tarball/perl/perl-$(PERL_VERSION).tar.gz
	gunzip < $(TMP_DIR)/perl.tar.gz | $(TAR) xf -
	# Original URL: http://www.cpan.org/modules/by-module/App/App-cpanminus-1.7036.tar.gz
	$(GET) ./perl-$(PERL_VERSION)/App-cpanminus.tar.gz http://www.normation.com/tarball/cpan/App-cpanminus-1.7036.tar.gz
	cd perl-$(PERL_VERSION) && gunzip < App-cpanminus.tar.gz | $(TAR) xf -
	mv ./perl-$(PERL_VERSION)/App-cpanminus-1.7036 ./perl-$(PERL_VERSION)/App-cpanminus
	../../build-caching put --force-config ./perl-$(PERL_VERSION)/ name=perl-source versions=$(perl_source)
endif

cpan-source: perl-$(PERL_VERSION)/App-cpanminus
perl-$(PERL_VERSION)/App-cpanminus:
	mkdir -p ./perl-$(PERL_VERSION)
	# Original URL: http://www.cpan.org/modules/by-module/App/App-cpanminus-1.7036.tar.gz
	$(GET) $(TMP_DIR)/App-cpanminus.tar.gz http://www.normation.com/tarball/cpan/App-cpanminus-1.7036.tar.gz
	cd perl-$(PERL_VERSION) && gunzip < $(TMP_DIR)/App-cpanminus.tar.gz | $(TAR) xf -
	mv ./perl-$(PERL_VERSION)/App-cpanminus-1.7036 ./perl-$(PERL_VERSION)/App-cpanminus

rudder-agent.cron: rudder-sources
	cp ./rudder-sources/rudder-techniques/techniques/system/common/1.0/rudder_agent_community_cron.st ./rudder-agent.cron
	# Set unexpanded variables of the cron file
	$(SED) 's@\$${sys.workdir}@/var/rudder/cfengine-community@g' rudder-agent.cron | $(SED) 's@\$${g.rudder_base}@/opt/rudder@g' | $(SED) 's@\\&\\&@\&\&@g' | $(SED) 's@\\&1@\&1@g' > rudder-agent.cron.new
	mv rudder-agent.cron.new rudder-agent.cron

####################################
# Builds separated into components #
####################################

# TODO generalize install in build-* to allow caching
build-ssl: openssl-source
	cd openssl-source && $(SSL_CONFIGURE) -fPIC --prefix=$(RUDDER_DIR) --openssldir=$(RUDDER_DIR)/openssl shared
	cd openssl-source && $(MAKE)
	slibclean >/dev/null 2>&1 || true
	cd openssl-source && $(MAKE) install INSTALL_PREFIX=$(CURDIR)/build-ssl

build-lmdb: lmdb-source
	cd lmdb-source/libraries/liblmdb && $(MAKE)
	# need a temporary install for cfengine
	mkdir -p build-lmdb/opt/rudder
	# LMDB's Makefile does not know how to create destination files, do it ourselves
	cd build-lmdb/opt/rudder && mkdir -p bin lib include man/man1
	cd lmdb-source/libraries/liblmdb && $(MAKE) install prefix=$(RUDDER_DIR) DESTDIR=$(CURDIR)/build-lmdb

build-cfengine: get-flags $(BUILD_DEPS) cfengine-source build-cfengine-stamp
build-cfengine-stamp:
	# If there is no configure, bootstrap with autogen.sh first
	cd cfengine-source && [ -x ./configure ] || NO_CONFIGURE=1 ./autogen.sh
	# remove temporary rpath added by configure to build options
	cd cfengine-source && $(SED) 's/[A-Z]*_LDFLAGS="$[A-Z]*_LDFLAGS -R$with_[a-z]*\/lib"/true/' configure > configure.new && mv configure.new configure && chmod +x configure
	cd cfengine-source && ./configure --prefix=$(RUDDER_DIR) --with-workdir=/var/rudder/cfengine-community --enable-static=yes --enable-shared=no --without-postgresql $(LMDB_ARG) $(OPENSSL_ARG) CFLAGS="$(BUILD_CFLAGS) $(SECURE_CFLAGS)" LDFLAGS="-Wl,-R/opt/rudder/lib $(BUILD_LDFLAGS) $(SECURE_LDFLAGS)"
	cd cfengine-source && $(MAKE)
	touch $@

# Test if compiler supporte hardening flags
get-flags:
	$(eval BUILD_CFLAGS:=$(shell [ -x /usr/bin/dpkg-buildflags ] && /usr/bin/dpkg-buildflags --get CFLAGS ))
	$(eval BUILD_LDFLAGS:=$(shell [ -x /usr/bin/dpkg-buildflags ] && /usr/bin/dpkg-buildflags --get LDFLAGS ))
	$(eval HAVE_PROTECTION:=$(shell \
	FLAG_TEST_FILE=`mktemp /tmp/hardening.XXXXXX` ;\
	echo "void main() {}" > "$${FLAG_TEST_FILE}.c" ;\
	gcc $(TRY_CFLAGS) $(TRY_LDFLAGS) -o "$${FLAG_TEST_FILE}" "$${FLAG_TEST_FILE}.c" 2>/dev/null && echo "OK";\
	rm -f "$${FLAG_TEST_FILE}" "$${FLAG_TEST_FILE}".c ))
	
	$(eval SECURE_CFLAGS:=$(if $(HAVE_PROTECTION),$(TRY_CFLAGS)))
	$(eval SECURE_LDFLAGS:=$(if $(HAVE_PROTECTION),$(TRY_LDFLAGS)))

build-perl: perl-$(PERL_VERSION)
	cd perl-$(PERL_VERSION) && $(MAKE) distclean 2>/dev/null || true # Or this can fail on an already used source
	cd perl-$(PERL_VERSION) && ./Configure -Dnoextensions=ODBM_File -Duserelocatableinc -Dusethreads -des -Dcc="gcc" -Dinstallprefix=$(RUDDER_DIR) -Dsiteprefix=$(RUDDER_DIR) -Dprefix=$(RUDDER_DIR)
	cd perl-$(PERL_VERSION) && $(MAKE)
	touch $@

#####################################
# Install separated into components #
#####################################

install-ssl: build-ssl
	mkdir -p $(DESTDIR)
	# TODO cleanup a bit, we don't need everything here
	$(CP_A) $(CURDIR)/build-ssl/* $(DESTDIR)

install-lmdb: build-lmdb
	mkdir -p $(DESTDIR)
	$(CP_A) $(CURDIR)/build-lmdb/* $(DESTDIR)

install-cfengine: build-cfengine $(INSTALL_DEPS)
	cd cfengine-source && $(MAKE) install DESTDIR=$(DESTDIR) STRIP=""
	mkdir -p $(INSTALL_DIR)/share/man/man8
	cd cfengine-source && for binary in cf-agent cf-promises cf-key cf-execd cf-serverd cf-monitord cf-runagent; do \
		LD_LIBRARY_PATH="$(INSTALL_DIR)/lib" $${binary}/$${binary} -M | gzip > $(INSTALL_DIR)/share/man/man8/$${binary}.8.gz; \
	done

install-perl: build-perl
	cd perl-$(PERL_VERSION) && $(MAKE) install DESTDIR=$(DESTDIR)
	touch build-perl # because perl-$(PERL_VERSION) is touched by make install

CPANM:=$(CURDIR)/perl-$(PERL_VERSION)/App-cpanminus/bin/cpanm $(GET_OPT)
MODULE_INSTALL:=MAKEFLAGS= $(PERL) $(CPANM) -l $(INSTALL_DIR) --skip-installed
MODULE_TEST:=$(PERL) -I $(INSTALL_DIR)/lib/perl5 -e1

fusion-modules: $(FUSION_DEPS)
	mkdir -p $(INSTALL_DIR)/lib/perl5
# Fusion dependencies :
# * Text::Template -> server only
# * LWP
# * Net::IP
# * XML::TreePP
# * UNIVERSAL::require
# * File::Which

# Socket::GetAddrInfo: 0 -> network

# Archive::Extract: 0
# Compress::Zlib: 0
# Crypt::DES: 0
# Digest::MD5: 0
# Digest::SHA: 0
# File::Copy::Recursive: 0
# HTTP::Daemon: 0
# IO::Socket::SSL: 0
# JSON: 0
# LWP::Protocol::https: 0
# Net::CUPS: 0.6
# Net::NBName: 0
# Net::SNMP: 0
# Net::Write::Layer2: 0
# POE::Component::Client::Ping: 0
# Parse::EDID: 0
# Proc::Daemon: 0
# Proc::PID::File: 0
# URI::Escape: 0
#

# TODO rework these dependencies, they are not the right ones 
# CPAN Modules installation
	# Original URL: http://www.cpan.org/modules/by-module/URI/URI-1.67.tar.gz
	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/URI-1.67.tar.gz
	$(MODULE_TEST) -MURI
#	# Original URL: http://www.cpan.org/modules/by-module/HTML/HTML-Tagset-3.20.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/HTML-Tagset-3.20.tar.gz
#	$(MODULE_TEST) -MHTML::Tagset
#	# Original URL: http://www.cpan.org/modules/by-module/HTML/HTML-Parser-3.71.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/HTML-Parser-3.71.tar.gz
#	$(MODULE_TEST) -MHTML::Parser
	# Original URL: http://www.cpan.org/modules/by-module/LWP/libwww-perl-6.13.tar.gz
	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/libwww-perl-6.13.tar.gz
	$(MODULE_TEST) -MLWP
#	# Original URL: http://www.cpan.org/modules/by-module/Compress/Compress-Raw-Bzip2-2.068.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/Compress-Raw-Bzip2-2.068.tar.gz
#	$(MODULE_TEST) -MCompress::Raw::Bzip2
#	# Original URL: http://www.cpan.org/modules/by-module/Compress/Compress-Raw-Zlib-2.068.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/Compress-Raw-Zlib-2.068.tar.gz
#	$(MODULE_TEST) -MCompress::Raw::Zlib
#	# Original URL: http://www.cpan.org/modules/by-module/IO/IO-Compress-2.068.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/IO-Compress-2.068.tar.gz
#	#No test: IO::Compress cannot be called directly
	# Original URL: http://www.cpan.org/modules/by-module/Digest/Digest-MD5-2.54.tar.gz
	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/Digest-MD5-2.54.tar.gz
	$(MODULE_TEST) -MDigest::MD5
	# Orignal URL: http://www.cpan.org/modules/by-module/Net/Net-IP-1.26.tar.gz
	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/Net-IP-1.26.tar.gz
	$(MODULE_TEST) -MNet::IP
#	# Original URL: http://www.cpan.org/modules/by-module/XML/XML-NamespaceSupport-1.11.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/XML-NamespaceSupport-1.11.tar.gz
#	$(MODULE_TEST) -MXML::NamespaceSupport
#	# Original URL: http://www.cpan.org/modules/by-module/XML/XML-SAX-0.99.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/XML-SAX-0.99.tar.gz
#	$(MODULE_TEST) -MXML::SAX
#	# Original URL: http://www.cpan.org/modules/by-module/XML/XML-Simple-2.20.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/XML-Simple-2.20.tar.gz
#	$(MODULE_TEST) -MXML::Simple
	# Original URL: http://www.cpan.org/modules/by-module/XML/XML-TreePP-0.43.tar.gz
	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/XML-TreePP-0.43.tar.gz
	$(MODULE_TEST) -MXML::TreePP
	# Original URL: http://www.cpan.org/modules/by-module/UNIVERSAL/UNIVERSAL-require-0.18.tar.gz
	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/UNIVERSAL-require-0.18.tar.gz
	$(MODULE_TEST) -MUNIVERSAL::require
#	# Original URL: http://search.cpan.org/CPAN/authors/id/K/KW/KWILLIAMS/Probe-Perl-0.03.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/Probe-Perl-0.03.tar.gz
#	$(MODULE_TEST) -MProbe::Perl
#	# Original URL: http://www.cpan.org/modules/by-module/IPC/IPC-Run3-0.048.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/IPC-Run3-0.048.tar.gz
#	$(MODULE_TEST) -MIPC::Run3
#	# Original URL: http://www.cpan.org/modules/by-module/Test/Test-Script-1.10.tar.gz
#	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/Test-Script-1.10.tar.gz
#	$(MODULE_TEST) -MTest::Script
	# Original URL: http://www.cpan.org/modules/by-module/File/File-Which-1.18.tar.gz
	$(MODULE_INSTALL) http://www.normation.com/tarball/cpan/File-Which-1.18.tar.gz
	$(MODULE_TEST) -MFile::Which
	touch $@

install-fusion: fusioninventory-agent fusion-modules
# Fusion installation
	mkdir -p $(INSTALL_DIR)/share/fusion-utils
	cp -r fusioninventory-agent/share/* $(INSTALL_DIR)/share/fusion-utils/
ifeq ($(INSTALL),ginstall)
	# fusion doesn't know how to make install without gnu tools in the path
	$(SED) 's/\([^g]\)install -m/\1ginstall -m/' fusioninventory-agent/Makefile.PL > fusioninventory-agent/Makefile.PL.new
	mv fusioninventory-agent/Makefile.PL.new fusioninventory-agent/Makefile.PL
endif
	cd fusioninventory-agent && PERL_MM_USE_DEFAULT=1 $(PERL) Makefile.PL --default PREFIX=$(RUDDER_DIR)
	cd fusioninventory-agent && $(MAKE) install DESTDIR=$(DESTDIR)
	# bug in fusion installer that doesn't set the right owner to some files
	chown root $(DESTDIR)/opt/rudder/share/fusioninventory
	chown root $(DESTDIR)/opt/rudder/share/fusioninventory/html
	chown root $(DESTDIR)/opt/rudder/etc/fusioninventory
	cp -r fusioninventory-agent/lib/FusionInventory $(INSTALL_DIR)/lib/perl5/

.PHONY: localclean localdepends veryclean depend build install clean mrproper install-ssl install-lmdb install-cfengine install-perl install-fusion get-flags
