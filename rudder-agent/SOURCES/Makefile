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
RUDDER_VERSION_TO_PACKAGE =
RUDDER_MAJOR_VERSION := $(shell echo ${RUDDER_VERSION_TO_PACKAGE} | cut -d'.' -f 1-2)

FUSION_RELEASE = 2.4.3
FUSION_SHA1 = 66d6e699575e98a6c050b39ca27c72a20f5569c3
CFENGINE_RELEASE = 3.12.2
CFENGINE_SHA1 = 199b06a52ead0e9ef9d1dc304746d8e575b04ace
LMDB_RELEASE = 0.9.22
LMDB_SHA1 = 5d62d4c7527f3474f60a0d87db2bfd539e6493eb
# Default openssl version to use
OPENSSL_RELEASE = 1.1.1b
OPENSSL_SHA1 = e9710abf5e95c48ebf47991b10cbb48c09dae102
# Variable INSTALL_PREFIX name has changed with openssl 1.1.0 https://www.openssl.org/news/cl110.txt
OPENSSL_DESTDIR_VAR_NAME = DESTDIR
# open ssl version to use on older systems
OLD_OPENSSL_RELEASE = 1.0.2r
OLD_OPENSSL_SHA1 = b9aec1fa5cedcfa433aed37c8fe06b0ab0ce748d
OLD_OPENSSL_DESTDIR_VAR_NAME = INSTALL_PREFIX
PERL_RELEASE = 5.22.4
PERL_SHA1 = fd79af20e6454d1bb5e5e6ac4774a1e295d4d794
PCRE_RELEASE = 8.38
PCRE_SHA1 = 3ab418d0026c2a4e693ec783bd60660debc32b8f
CPANMINUS_RELEASE = 1.7036
CPANMINUS_SHA1 = a12043498ab54d9abdc58d1ebb4988da3bd515db
#CPAN_URL = https://www.cpan.org
CPAN_URL = $(HTTPS)://repository.rudder.io/build-dependencies/cpan/$(RUDDER_MAJOR_VERSION)
CURL_RELEASE = 7.61.0
CURL_SHA1 = 34c0f89e01c27070fe3b6f86371791390f464602
YAML_RELEASE = 0.2.1
YAML_SHA1 = 125a3113681f06320dcdfde48bab47cba9031263
XML_RELEASE = 2.9.7
XML_SHA1 = ab3325e6cdda50ab2382fdfe0bdb6f7d1b9224a6
ZLIB_RELEASE = 1.2.11
ZLIB_SHA1 = e6d119755acdf9104d7ba236b1242696940ed6dd

MAKE_J=-j3

# Default PATHs
RUDDER_DIR = /opt/rudder
DESTDIR = $(CURDIR)/target

# Default OS to build for
OS_FAMILY=linux

# default build with pie if possible
TRY_CFLAGS=-fstack-protector
ifeq (false,$(USE_PIE))
PIE_CFLAGS=
TRY_LDFLAGS=-Wl,-z,relro -Wl,-z,now
else
PIE_CFLAGS=-fPIE
TRY_LDFLAGS=-pie -Wl,-z,relro -Wl,-z,now
endif

# GENERIC_GET: do not remove this line
# This is a generic get code that is common to many of our Makefiles.
# The tag is here to find them.
# If you change this code, change all the places where you can find this tag too.
# It is duplicated because it is the code that is used to manage dependency
# to other repositories, hence allowing deduplication of other code.
# Autodetect wget, curl or fetch usage and proxy configuration
# Usage: $(GET) <destination_file> <url> <hash>
PROXY_ENV = $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY))
# No accept encoding to prevent the webserver form altering the distributed file
WGET = wget -q --header="accept-encoding:" -O
FETCH = fetch -q -o
CURL = curl -s -L -f -o
ifneq (,$(wildcard /usr/bin/curl))
_GET = $(PROXY_ENV) $(CURL)
GET_OPT = --curl
CPAN_OPT = --curl --no-wget
else
ifneq (,$(wildcard /usr/bin/fetch))
_GET = $(PROXY_ENV) $(FETCH)
else
_GET = $(PROXY_ENV) $(WGET)
GET_OPT = --wget
CPAN_OPT = --wget
endif
endif
# We are using sha1 as sha256 is not supported on RHEL3
# Not using the sha1sum command as it is not available on AIX
# Pass an empty string to skip hash check
GET=get() { $(_GET) "$$1.part" "$$2" && { openssl dgst -sha1 "$$1.part" | grep -q "$$3" || { echo "Wrong checksum, aborting"; exit 1; }; } && mv "$$1.part" "$$1"; }; get

# Autodetect presence of gnu tools
TAR := $(shell type gtar >/dev/null 2>&1 && echo gtar || echo tar)
PATCH := $(shell type gpatch >/dev/null 2>&1 && echo gpatch || echo patch)
SED := $(shell type gsed >/dev/null 2>&1 && echo gsed || echo sed)
INSTALL := $(shell type ginstall >/dev/null 2>&1 && echo ginstall || echo install)

# Use parameters to guess what should be packaged
BUILD_DEPS :=
INSTALL_DEPS :=
# default: use https for urls
ifeq (false,$(USE_HTTPS))
HTTPS:=http
else
HTTPS:=https
endif
# default: do not embed zlib
ifeq (false,$(USE_SYSTEM_ZLIB))
BUILD_DEPS := $(BUILD_DEPS) build-zlib
ZLIB_ARG := --with-zlib=$(CURDIR)/dependencies$(RUDDER_DIR)
else
ZLIB_ARG := --with-zlib
endif
# default: do not build openssl
ifeq (false,$(USE_SYSTEM_OPENSSL))
ifeq (true,$(BUILD_OLD_OPENSSL))
OPENSSL_RELEASE = $(OLD_OPENSSL_RELEASE)
OPENSSL_SHA1 = $(OLD_OPENSSL_SHA1)
OPENSSL_DESTDIR_VAR_NAME = $(OLD_OPENSSL_DESTDIR_VAR_NAME)
endif
BUILD_DEPS := $(BUILD_DEPS) build-ssl
OPENSSL_ARG := --with-openssl=$(CURDIR)/dependencies$(RUDDER_DIR)
endif
# default: build lmdb
ifneq (true,$(USE_SYSTEM_LMDB))
BUILD_DEPS := $(BUILD_DEPS) build-lmdb
LMDB_ARG := --with-lmdb=$(CURDIR)/dependencies$(RUDDER_DIR)
endif
# default: do not build pcre
ifeq (false,$(USE_SYSTEM_PCRE))
BUILD_DEPS := $(BUILD_DEPS) build-pcre
PCRE_ARG := --with-pcre=$(CURDIR)/dependencies$(RUDDER_DIR)
endif
# default: build perl
ifneq (true,$(USE_SYSTEM_PERL))
BUILD_DEPS := $(BUILD_DEPS) build-perl
PERL:=$(CURDIR)/dependencies/opt/rudder/bin/perl
else
PERL := perl
endif
# default: embed fusion
ifneq (true,$(USE_SYSTEM_FUSION))
INSTALL_DEPS := $(INSTALL_DEPS) install-fusion
endif
# default: do not embed curl
ifeq (false,$(USE_SYSTEM_CURL))
BUILD_DEPS := $(BUILD_DEPS) build-curl
CURL_ARG := --with-libcurl=$(CURDIR)/dependencies$(RUDDER_DIR)
else
CURL_ARG := --with-libcurl
endif
# default: do not embed libyaml
ifeq (false,$(USE_SYSTEM_YAML))
BUILD_DEPS := $(BUILD_DEPS) build-yaml
YAML_ARG := --with-libyaml=$(CURDIR)/dependencies$(RUDDER_DIR)
else
YAML_ARG := --with-libyaml
endif
# default: do not embed libxml2
ifeq (false,$(USE_SYSTEM_XML))
BUILD_DEPS := $(BUILD_DEPS) build-xml
XML_ARG := --with-libxml2=$(CURDIR)/dependencies$(RUDDER_DIR)
else
XML_ARG := --with-libxml2
endif

# AIX do not support posix acl
# AIX does nor have the same form of rpath
ifeq (aix,$(OS_FAMILY))
SYSTEM_LDFLAGS := -static-libgcc -Wl,-bsvr4 -Wl,-R/opt/rudder/lib
else
ACL_ARG := --with-libacl
SYSTEM_LDFLAGS := -Wl,-R/opt/rudder/lib
endif

# In case we do not want pam
# default : use PAM
ifeq (false, $(USE_PAM))
PAM_ARG := --without-pam
endif

# Hack needed because openssl is not guessing correctly the architecture on solaris 32bits
ifeq (i386-pc-solaris2.10,$(shell ./config.guess))
SSL_CONFIGURE:=./Configure solaris-x86-gcc
# Hack needed because openssl is not guessing correctly the architecture on debian 32 bits chroot
else
ifeq (i386,$(shell [ -x /usr/bin/dpkg ] && dpkg --print-architecture))
SSL_CONFIGURE:=./Configure linux-generic32
else
SSL_CONFIGURE:=./config
endif
endif

# download dependencies
depend: localdepends
localdepends: rudder-agent-utilities perl-$(PERL_RELEASE) fusioninventory-agent cfengine-source openssl-source lmdb-source pcre-source curl-source xml-source yaml-source zlib-source rudder-agent.cron rudder.8.gz

# build binaries
build: get-flags build-cfengine

# install to DESTDIR
install: build $(INSTALL_DEPS) install-cfengine rudder-agent-utilities rudder-agent.cron debug-script/rudder-debug-info
	# Directories
	mkdir -p $(DESTDIR)/opt/rudder/etc
	mkdir -p $(DESTDIR)/opt/rudder/etc/ssl
	mkdir -p $(DESTDIR)/opt/rudder/bin
	mkdir -p $(DESTDIR)/opt/rudder/share/commands
	mkdir -p $(DESTDIR)/opt/rudder/share/lib
	ln -s ../../../opt/rudder/bin $(DESTDIR)/var/rudder/cfengine-community/bin
	mkdir -p $(DESTDIR)/var/rudder/cfengine-community/inputs
	mkdir -p $(DESTDIR)/var/rudder/cfengine-community/ppkeys
	chmod 700 $(DESTDIR)/var/rudder/cfengine-community/ppkeys
	mkdir -p $(DESTDIR)/var/rudder/tmp
	mkdir -p $(DESTDIR)/var/rudder/tools
	mkdir -p $(DESTDIR)/var/rudder/inventories
	mkdir -p $(DESTDIR)/var/rudder/ncf/local
	mkdir -p $(DESTDIR)/var/rudder/ncf/common
	mkdir -p $(DESTDIR)/var/log/rudder/install
	mkdir -p $(DESTDIR)/var/log/rudder/agent-check
	mkdir -p $(DESTDIR)/usr/bin
	mkdir -p $(DESTDIR)/etc/cron.d
# AIX needs .a files
ifneq (aix,$(OS_FAMILY))
	cd $(DESTDIR)/opt/rudder && rm -rf include lib/*.a lib/*.la
endif
	# 2Mb manuals of C functions
	find $(DESTDIR)/opt/rudder/share/man/man3 -name "*.3" -exec rm {} \; || true
	# Compress man pages
	find $(DESTDIR)/opt/rudder/share/man -type f ! -name '*.gz' -exec gzip -9 {} \;
	# for all old links towards non-compress man page, create a new equivalent link towards the .gz and remove the old one.
	# As readlink does not exists on AIX, we need to hack with ls -l and awk.
	find $(DESTDIR)/opt/rudder/share/man -type l ! -name *.gz -exec sh -c 'ln -s -f $$(ls -al $$0 | awk -F"-> " "{print \$$2}").gz $$0.gz; rm $$0' {} \;


# Systemd files
ifeq (true,$(USE_SYSTEMD))
	mkdir -p $(DESTDIR)/lib/systemd/system
	$(INSTALL) -m 644 systemd/rudder-agent.service $(DESTDIR)/lib/systemd/system/rudder-agent.service
	$(INSTALL) -m 644 systemd/rudder-cf-execd.service $(DESTDIR)/lib/systemd/system/rudder-cf-execd.service
	$(INSTALL) -m 644 systemd/rudder-cf-serverd.service $(DESTDIR)/lib/systemd/system/rudder-cf-serverd.service
endif

	# Init files
ifneq (true,$(USE_SYSTEMD))
ifneq (aix,$(OS_FAMILY))
	mkdir -p $(DESTDIR)/etc/init.d
	mkdir -p $(DESTDIR)/etc/default
	$(INSTALL) -m 755 rudder-agent.init $(DESTDIR)/etc/init.d/rudder-agent
	$(INSTALL) -m 644 rudder-agent.default $(DESTDIR)/etc/default/rudder-agent
endif
endif

	# cron files
ifneq (aix,$(OS_FAMILY))
	$(INSTALL) -m 644 rudder-agent.cron $(DESTDIR)/etc/cron.d/rudder-agent
endif

	# Wrapper script
	$(INSTALL) -m 755 run-inventory $(DESTDIR)/opt/rudder/bin/

	# Openssl configuration
	$(INSTALL) -m 640 openssl.cnf $(DESTDIR)/opt/rudder/etc/ssl/openssl-agent.cnf

	# Signature script
	$(INSTALL) -m 755 rudder-sign $(DESTDIR)/opt/rudder/bin/
	$(INSTALL) -m 755 rudder-signature-check $(DESTDIR)/opt/rudder/bin/
	$(INSTALL) -m 755 signature.sh $(DESTDIR)/opt/rudder/bin/ # for backwards compatibility, remove in the next major version after the next LTS after 3.1 is announced

	mkdir -p $(DESTDIR)/opt/rudder/share/package-scripts
	$(INSTALL) -m 755 rudder-agent-postinst $(DESTDIR)/opt/rudder/share/package-scripts/
	$(INSTALL) -m 755 check-rudder-agent $(DESTDIR)/opt/rudder/bin/
	$(INSTALL) -m 755 vzps.py $(DESTDIR)/opt/rudder/bin/
	$(INSTALL) -m 755 rudder-perl $(DESTDIR)/opt/rudder/bin/
	$(INSTALL) -m 755 rudder-uuidgen $(DESTDIR)/opt/rudder/bin/
	$(INSTALL) -m 755 debug-script/rudder-debug-info $(DESTDIR)/opt/rudder/bin/

	# Rudder agent utilities
	$(INSTALL) -m 755 rudder-agent-utilities/bin/rudder $(DESTDIR)/opt/rudder/bin/
	$(INSTALL) -m 755 rudder-agent-utilities/share/commands/* $(DESTDIR)/opt/rudder/share/commands/
	$(INSTALL) -m 644 rudder-agent-utilities/share/lib/* $(DESTDIR)/opt/rudder/share/lib/
	chmod 755 $(DESTDIR)/opt/rudder/share/lib/timestamp
	$(INSTALL) -m 644 rudder-agent-utilities/agent-capabilities $(DESTDIR)/opt/rudder/etc/

	# Bootstrap promises
	mkdir -p $(DESTDIR)/opt/rudder/share/bootstrap-promises/
	$(INSTALL) -m 644 ./rudder-sources/rudder-techniques/bootstrap-promises/* $(DESTDIR)/opt/rudder/share/bootstrap-promises/

	# Install /etc/bash_completion.d/rudder.sh in order to autocomplete rudder commands
	mkdir -p $(DESTDIR)/etc/bash_completion.d
	$(INSTALL) -m 644 rudder-agent-utilities/etc/bash_completion.d/rudder.sh $(DESTDIR)/etc/bash_completion.d/

	# Install rudder man page
	mkdir -p $(DESTDIR)/opt/rudder/share/man/man8/
	$(INSTALL) -m 644 rudder.8.gz $(DESTDIR)/opt/rudder/share/man/man8/

	# Create a symlink to make "rudder" available as part of the default PATH
	ln -sf $(RUDDER_DIR)/bin/rudder $(DESTDIR)/usr/bin/rudder

	# Install a profile script to make cf-* part of the PATH
ifneq (aix,$(OS_FAMILY))
	mkdir -p $(DESTDIR)/etc/profile.d
	$(INSTALL) -m 644 rudder-agent.sh $(DESTDIR)/etc/profile.d/
endif

# Strip binaries
ifeq (aix,$(OS_FAMILY))
	cp /opt/freeware/lib/gcc/powerpc-ibm-aix5.3.0.0/4.8.2/libgcc* $(DESTDIR)/opt/rudder/lib/
	./absolute-aix-path $(DESTDIR)/opt/rudder
	find $(DESTDIR) -type f | xargs file | grep -E "executable|shared object" | cut -f 1 -d : | xargs strip 2> /dev/null || true
	echo done
else
	find $(DESTDIR) -type f -print0 | xargs -0 file | grep -E "executable|shared object" | cut -f 1 -d : | xargs strip --strip-unneeded 2> /dev/null || true
endif

clean:
	rm -rf dependencies build-cfengine build-perl fusion-modules build-cfengine-stamp
	rm -rf rudder-sources
	rm -f rudder.8.gz
	[ -d cfengine-source ] && cd cfengine-source && $(MAKE) clean 2>/dev/null || true
	[ -d lmdb-source ] && cd lmdb-source && $(MAKE) clean 2>/dev/null || true
	[ -d openssl-source ] && cd openssl-source && $(MAKE) clean 2>/dev/null || true
	[ -d perl-$(PERL_RELEASE) ] && cd perl-$(PERL_RELEASE) && $(MAKE) distclean 2>/dev/null || true
	cd debug-script && $(MAKE) clean 2>/dev/null || true

# distclean should remove everything except rudder-sources.tar.bz2 since it can be brought by by external means
distclean: clean
	rm -f rudder-agent.cron
	rm -rf rudder-agent-utilities fusioninventory-agent
	for sourcedir in cfengine lmdb openssl curl pcre zlib yaml xml; do \
	  rm -rf $${sourcedir}-source; \
	done
	rm -rf perl-$(PERL_RELEASE)

# standard name is mrproper
mrproper: distclean
	rm -f rudder-sources.tar.bz2

##########################################
# Dependencies separated into components #
##########################################

cfengine-source:
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	# Original URL: https://cfengine-package-repos.s3.amazonaws.com/tarballs/cfengine-$(CFENGINE_RELEASE).tar.gz
	$(GET) $(TMP_DIR)/cfengine.tgz $(HTTPS)://repository.rudder.io/build-dependencies/cfengine/cfengine-$(CFENGINE_RELEASE).tar.gz $(CFENGINE_SHA1)
	gunzip < $(TMP_DIR)/cfengine.tgz | $(TAR) xf -
	mv ./cfengine-$(CFENGINE_RELEASE) ./cfengine-source
	rm -rf $(TMP_DIR)

	# Apply patches
	for PATCHNAME in patches/cfengine/*.patch; do echo "Applying $$PATCHNAME..."; $(PATCH) -d ./cfengine-source -p1 < $$PATCHNAME; echo ""; done
	# Make sure there were no rejects
	test `find ./cfengine-source -name \*.rej | wc -l` = 0

openssl-source:
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	# Original URL: https://www.openssl.org/source/openssl-$(OPENSSL_RELEASE).tar.gz
	$(GET) $(TMP_DIR)/openssl.tgz $(HTTPS)://repository.rudder.io/build-dependencies/openssl/openssl-$(OPENSSL_RELEASE).tar.gz $(OPENSSL_SHA1)
	gunzip < $(TMP_DIR)/openssl.tgz | $(TAR) xf -
	mv ./openssl-$(OPENSSL_RELEASE) ./openssl-source
	rm -rf $(TMP_DIR)

lmdb-source:
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	# Original URL: http://ftp.fr.debian.org/debian/pool/main/l/lmdb/lmdb_$(LMDB_RELEASE).orig.tar.xz
	$(GET) $(TMP_DIR)/lmdb.tgz $(HTTPS)://repository.rudder.io/build-dependencies/lmdb/lmdb-$(LMDB_RELEASE).tar.gz $(LMDB_SHA1)
	gunzip < $(TMP_DIR)/lmdb.tgz | $(TAR) xf -
	mv ./lmdb-LMDB_$(LMDB_RELEASE) ./lmdb-source
	rm -rf $(TMP_DIR)

pcre-source:
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	# Original URL: http://vorboss.dl.sourceforge.net/project/pcre/pcre/8.38/pcre-8.38.tar.gz
	$(GET) $(TMP_DIR)/pcre.tgz $(HTTPS)://repository.rudder.io/build-dependencies/pcre/pcre-$(PCRE_RELEASE).tar.gz $(PCRE_SHA1)
	gunzip < $(TMP_DIR)/pcre.tgz | $(TAR) xf -
	mv ./pcre-$(PCRE_RELEASE) ./pcre-source
	rm -rf $(TMP_DIR)

zlib-source:
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	# Original URL: http://zlib.net/zlib-$(ZLIB_RELEASE).tar.gz
	$(GET) $(TMP_DIR)/zlib.tgz $(HTTPS)://repository.rudder.io/build-dependencies/zlib/zlib-$(ZLIB_RELEASE).tar.gz $(ZLIB_SHA1)
	gunzip < $(TMP_DIR)/zlib.tgz | $(TAR) xf -
	mv ./zlib-$(ZLIB_RELEASE) ./zlib-source
	rm -rf $(TMP_DIR)

curl-source:
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	# Original URL: https://curl.haxx.se/download/curl-7.58.0.tar.gz
	$(GET) $(TMP_DIR)/curl.tgz $(HTTPS)://repository.rudder.io/build-dependencies/curl/curl-$(CURL_RELEASE).tar.gz $(CURL_SHA1)
	gunzip < $(TMP_DIR)/curl.tgz | $(TAR) xf -
	mv ./curl-$(CURL_RELEASE) ./curl-source
	rm -rf $(TMP_DIR)

yaml-source:
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	# Original URL: http://pyyaml.org/download/libyaml/yaml-0.1.7.tar.gz
	$(GET) $(TMP_DIR)/yaml.tgz $(HTTPS)://repository.rudder.io/build-dependencies/yaml/yaml-$(YAML_RELEASE).tar.gz $(YAML_SHA1)
	gunzip < $(TMP_DIR)/yaml.tgz | $(TAR) xf -
	mv ./yaml-$(YAML_RELEASE) ./yaml-source
	rm -rf $(TMP_DIR)

xml-source:
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	# Original URL: ftp://xmlsoft.org/libxml2/libxml2-2.9.7.tar.gz
	$(GET) $(TMP_DIR)/libxml2.tgz $(HTTPS)://repository.rudder.io/build-dependencies/xml/libxml2-$(XML_RELEASE).tar.gz $(XML_SHA1)
	gunzip < $(TMP_DIR)/libxml2.tgz | $(TAR) xf -
	mv ./libxml2-$(XML_RELEASE) ./xml-source
	# patch libxml source to work with very old gcc
	cd ./xml-source && $(SED) 's/#ifdef __GNUC__/#if __GNUC__ > 3/' ./timsort.h > ./timsort.h.new && mv ./timsort.h.new ./timsort.h
	cd ./xml-source && $(SED) 's/-Wextra//' configure > configure.new && mv configure.new configure
	cd ./xml-source && $(SED) 's/-Wno-array-bounds//' configure > configure.new && mv configure.new configure && chmod +x configure
	rm -rf $(TMP_DIR)

rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2 $(HTTPS)://repository.rudder.io/sources/$(RUDDER_VERSION_TO_PACKAGE)/rudder-sources-$(RUDDER_VERSION_TO_PACKAGE).tar.bz2 ""

rudder-sources: rudder-sources.tar.bz2
	bunzip2 < rudder-sources.tar.bz2 | $(TAR) xf -
	mv rudder-sources-$(RUDDER_VERSION_TO_PACKAGE)*/ rudder-sources/ # the '*' is needed for nightly release
	touch rudder-sources # to make it younger than the bzip source file

rudder.8.gz:
	# Get man page from rudder-project.org
	$(GET) rudder.8 $(HTTPS)://docs.rudder.io/man/${RUDDER_MAJOR_VERSION}/rudder.8 ""
	gzip -f rudder.8

rudder-agent-utilities: rudder-sources
	rm -rf ./rudder-agent-utilities/
	cp -r ./rudder-sources/rudder-agent/ ./rudder-agent-utilities
	# Add capabilities
	echo cfengine >> ./rudder-agent-utilities/agent-capabilities
	echo dumpdatastate >> ./rudder-agent-utilities/agent-capabilities
	echo bodydefault >> ./rudder-agent-utilities/agent-capabilities
	echo yaml >> ./rudder-agent-utilities/agent-capabilities
	echo xml >> ./rudder-agent-utilities/agent-capabilities
	echo curl >> ./rudder-agent-utilities/agent-capabilities
ifneq (false,$(USE_ACL))
	echo acl >> ./rudder-agent-utilities/agent-capabilities
endif

fusioninventory-agent:
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	#Original URL: https://github.com/fusioninventory/fusioninventory-agent/releases/download/2.3.19/FusionInventory-Agent-$(FUSION_RELEASE).tar.gz
	$(GET) $(TMP_DIR)/fusion.tgz $(HTTPS)://repository.rudder.io/build-dependencies/fusioninventory/FusionInventory-Agent-$(FUSION_RELEASE).tar.gz $(FUSION_SHA1)
	gunzip < $(TMP_DIR)/fusion.tgz | $(TAR) xf -
	mv ./FusionInventory-Agent-$(FUSION_RELEASE) ./fusioninventory-agent
	rm -rf $(TMP_DIR)

	# Apply patches
	for PATCHNAME in patches/fusioninventory/*.patch; do echo "Applying $$PATCHNAME... on FusionInventory"; $(PATCH) -d ./fusioninventory-agent -p1 < $$PATCHNAME; done
	# Make sure there were no rejects
	test `find ./fusioninventory-agent -name \*.rej | wc -l` = 0

	# Fix a lsusb invocation that crashes some SLES machines
	find ./fusioninventory-agent -name "USB.pm" -exec rm "{}" \;

perl-source: perl-$(PERL_RELEASE)
perl-$(PERL_RELEASE):
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	# Original URL: http://www.cpan.org/src/5.0/perl-5.22.4.tar.gz
	$(GET) $(TMP_DIR)/perl.tar.gz $(HTTPS)://repository.rudder.io/build-dependencies/perl/perl-$(PERL_RELEASE).tar.gz $(PERL_SHA1)
	gunzip < $(TMP_DIR)/perl.tar.gz | $(TAR) xf -
	rm -rf $(TMP_DIR)

App-cpanminus:
	$(eval TMP_DIR := $(shell mktemp -dq /tmp/rudder.XXXXXX))
	# Original URL: http://www.cpan.org/modules/by-module/App/App-cpanminus-1.7036.tar.gz
	$(GET) $(TMP_DIR)/App-cpanminus.tar.gz $(HTTPS)://repository.rudder.io/build-dependencies/cpan/App-cpanminus-$(CPANMINUS_RELEASE).tar.gz $(CPANMINUS_SHA1)
	gunzip < $(TMP_DIR)/App-cpanminus.tar.gz | $(TAR) xf -
	mv App-cpanminus-$(CPANMINUS_RELEASE) App-cpanminus
	# cpanminus+curl have a bug on rhel3+64bits, this is the workaround, see http://www.rudder-project.org/redmine/issues/8533
	sed -i -e "s/'-#',//" App-cpanminus/bin/cpanm
	rm -rf $(TMP_DIR)

rudder-agent.cron: rudder-sources
	cp ./rudder-sources/rudder-techniques/techniques/system/common/1.0/rudder-agent-community-cron ./rudder-agent.cron
	# Set unexpanded variables of the cron file
	$(SED) 's@\$${sys.workdir}@/var/rudder/cfengine-community@g' rudder-agent.cron | $(SED) 's@\$${g.rudder_base}@/opt/rudder@g' | $(SED) 's@\\&\\&@\&\&@g' | $(SED) 's@\\&1@\&1@g' > rudder-agent.cron.new
	mv rudder-agent.cron.new rudder-agent.cron

debug-script/rudder-debug-info:
	cd debug-script && ${MAKE}

####################################
# Builds separated into components #
####################################

# build flags should be used everywhere
LDFLAGS=$(BUILD_LDFLAGS) $(SECURE_LDFLAGS) $(SYSTEM_LDFLAGS)
CFLAGS=$(BUILD_CFLAGS) $(SECURE_CFLAGS)
BUILD_FLAGS=CFLAGS="$(CFLAGS)" LDFLAGS="$(LDFLAGS)"

build-ssl: openssl-source
	# openssl doesn't support CFLAGS (it overrides its own) so we must pass them in batch to configure
	# openssl doesn't work with pie
	cd openssl-source && RELEASE="" $(SSL_CONFIGURE) -fPIC $(CFLAGS) $(LDFLAGS) --prefix=$(RUDDER_DIR) --openssldir=$(RUDDER_DIR)/openssl shared no-idea no-rc5 no-ssl3 no-dtls no-psk no-srp no-engine
# we need aix libpath in ssl library
ifeq (aix,$(OS_FAMILY))
	cd openssl-source && sed '/link_a.aix:/,/link_app.aix:/s/-bnolibpath,//' Makefile.shared > Makefile.shared.tmp && mv Makefile.shared.tmp Makefile.shared
endif
	cd openssl-source && $(MAKE) depend
	cd openssl-source && $(MAKE) $(MAKE_J)
	slibclean >/dev/null 2>&1 || true
	# install to a temporary location is needed to build cfengine
	cd openssl-source && $(MAKE) install $(OPENSSL_DESTDIR_VAR_NAME)=$(CURDIR)/dependencies

build-lmdb: lmdb-source
	# lmdb doesn't support CFLAGS (it overrides its own) so we pass XCFLAGS instead, that is appended to the original ones
	# we need to add -fPIE to be able to build static lib (which we do not use)
	cd lmdb-source/libraries/liblmdb && $(MAKE) $(MAKE_J) XCFLAGS="$(CFLAGS) $(PIE_CFLAGS)" LDFLAGS="$(LDFLAGS)"
	# need a temporary install for cfengine
	mkdir -p dependencies$(RUDDER_DIR)
	# LMDB's Makefile does not know how to create destination files, do it ourselves
	cd dependencies$(RUDDER_DIR) && mkdir -p bin lib include man/man1
	# install to a temporary location is needed to build cfengine
	cd lmdb-source/libraries/liblmdb && $(MAKE) install prefix=$(RUDDER_DIR) DESTDIR=$(CURDIR)/dependencies

build-pcre: pcre-source
	cd pcre-source && ./configure --disable-cpp --enable-utf8 --enable-unicode-properties --disable-cpp --prefix=$(RUDDER_DIR) $(BUILD_FLAGS)
	cd pcre-source && $(MAKE) $(MAKE_J)
	# install to a temporary location is needed to build cfengine
	cd pcre-source && $(MAKE) install DESTDIR=$(CURDIR)/dependencies

build-zlib: zlib-source
	cd zlib-source && $(BUILD_FLAGS) ./configure --prefix=$(RUDDER_DIR)
	cd zlib-source && $(MAKE) $(MAKE_J)
	# install to a temporary location is needed to build cfengine
	cd zlib-source && $(MAKE) install DESTDIR=$(CURDIR)/dependencies

build-curl: curl-source
	# pkcconfig give openssl build configuration, but it point to final installation path (/opt/rudder)
	# since we need the temporary path during build we need to add -I and -L
	# since we also need to link it during cfengine build we add -R (--rpath)
	# we may want to remove rpath using patchelf at the end, but this is mostly cosmetic
	cd curl-source && ./configure --prefix=$(RUDDER_DIR) --without-libpsl --with-ssl $(ZLIB_ARG) --disable-rtsp --enable-ipv6 --without-librtmp --without-ldap-lib CPPFLAGS="-I$(CURDIR)/dependencies$(RUDDER_DIR)/include" CFLAGS="$(CFLAGS) $(PIE_CFLAGS)" LDFLAGS="$(LDFLAGS) -Wl,-R$(CURDIR)/dependencies$(RUDDER_DIR)/lib -L$(CURDIR)/dependencies$(RUDDER_DIR)/lib -Wl,-R$(CURDIR)/dependencies$(RUDDER_DIR)/lib" PKG_CONFIG_PATH="$(CURDIR)/dependencies$(RUDDER_DIR)/lib/pkgconfig"
	cd curl-source && $(MAKE) $(MAKE_J)
	# install to a temporary location is needed to build cfengine
	cd curl-source && $(MAKE) install DESTDIR=$(CURDIR)/dependencies

build-yaml: yaml-source
	cd yaml-source && ./configure --prefix=$(RUDDER_DIR) --enable-gettext=no $(BUILD_FLAGS)
	cd yaml-source && $(MAKE) $(MAKE_J)
	# install to a temporary location is needed to build cfengine
	cd yaml-source && $(MAKE) install DESTDIR=$(CURDIR)/dependencies

build-xml: xml-source
	cd xml-source && ./configure --prefix=$(RUDDER_DIR) $(ZLIB_ARG) --with-xpath --with-c14n --without-catalog --without-debug --without-docbook --without-ftp --without-http --without-html --without-iconv --without-python --enable-shared --disable-static $(BUILD_FLAGS)
	cd xml-source && $(MAKE) $(MAKE_J)
	# install to a temporary location is needed to build cfengine
	cd xml-source && $(MAKE) install DESTDIR=$(CURDIR)/dependencies

build-perl: perl-$(PERL_RELEASE)
	cd perl-$(PERL_RELEASE) && $(MAKE) distclean 2>/dev/null || true # Or this can fail on an already used source
	cd perl-$(PERL_RELEASE) && ./Configure -Dnoextensions=ODBM_File -Duserelocatableinc -Dusethreads -des -Dcc="gcc" -Dinstallprefix=$(RUDDER_DIR) -Dsiteprefix=$(RUDDER_DIR) -Dprefix=$(RUDDER_DIR)
	cd perl-$(PERL_RELEASE) && $(MAKE) $(MAKE_J)
	cd perl-$(PERL_RELEASE) && $(MAKE) install DESTDIR=$(CURDIR)/dependencies
	# 8Mb of perldoc
	rm -rf $(CURDIR)/dependencies/opt/rudder/lib/perl5/$(PERL_RELEASE)/pod
	# 20Mb of perl manual
	find $(CURDIR)/dependencies/opt/rudder/share/man -name 'perl' -exec rm -rf {} \;
	# Remove 'special' files
	find $(CURDIR)/dependencies -name perllocal.pod \
	  -o -name ".packlist" \
	  -o -name "*.bs" \
	  | xargs rm -f
	touch build-perl # because perl-$(PERL_RELEASE) is touched by make install

# check cache content
PATCHES_SHA = $(shell find patches/cfengine -type f | sort | xargs sha256sum | sha256sum | awk '{print $$1}')
DEPS_CACHE_PARAMETERS = --with-env name=dependencies lmdb=$(LMDB_SHA1) openssl=$(OPENSSL_SHA1) old-openssl=$(OLD_OPENSSL_SHA1) pcre=$(PCRE_SHA1) curl=$(CURL_SHA1) yaml=$(YAML_SHA1) xml=$(XML_SHA1) zlib=$(ZLIB_SHA1) cfengine=$(CFENGINE_SHA1) patches=$(PATCHES_SHA)
CFENGINE_DEPS = $(shell ../../build-caching get dependencies/ $(DEPS_CACHE_PARAMETERS) || echo $(BUILD_DEPS))
build-cfengine: $(CFENGINE_DEPS) cfengine-source build-cfengine-stamp
	# save into cache if we built it
	if [ "$(CFENGINE_DEPS)" != "" ]; then ../../build-caching put dependencies/ $(DEPS_CACHE_PARAMETERS); fi

build-cfengine-stamp:
	# If there is no configure, bootstrap with autogen.sh first
	cd cfengine-source && [ -x ./configure ] || NO_CONFIGURE=1 ./autogen.sh
	# remove temporary rpath added by configure to build options
	cd cfengine-source && $(SED) 's/[A-Z]*_LDFLAGS="$$[A-Z]*_LDFLAGS -R$$with_[a-z]*\/lib"/true/' configure > configure.new && mv configure.new configure && chmod +x configure
	# build system bug when libxml is enabled
	cd cfengine-source && $(SED) 's/$$(AM_V_CCLD)$$(xml_c14nize_LINK)/$$(AM_V_CCLD)$$(LINK)/' tests/acceptance/Makefile.in > tests/acceptance/Makefile.in.new && mv tests/acceptance/Makefile.in.new tests/acceptance/Makefile.in
	# build system bug when libyaml is enabled
	cd cfengine-source && $(SED) 's/AM_CPPFLAGS = .*/AM_CPPFLAGS = $$(PCRE_CPPFLAGS) $$(OPENSSL_CPPFLAGS) $$(LIBYAML_CPPFLAGS)/' libutils/Makefile.in > libutils/Makefile.in.new && mv libutils/Makefile.in.new libutils/Makefile.in
	cd cfengine-source && ./configure --prefix=$(RUDDER_DIR) --with-workdir=/var/rudder/cfengine-community --enable-static=yes --enable-shared=no --without-postgresql --without-mysql $(ACL_ARG) $(LMDB_ARG) $(OPENSSL_ARG) $(PCRE_ARG) $(CURL_ARG) $(YAML_ARG) $(XML_ARG) $(PAM_ARG) CFLAGS="$(CFLAGS) $(PIE_CFLAGS)" LDFLAGS="$(LDFLAGS)" CPPFLAGS="-I$(CURDIR)/dependencies$(RUDDER_DIR)/include/libxml2"
	cd cfengine-source && $(MAKE) $(MAKE_J)
	cd cfengine-source && $(MAKE) $(MAKE_J) install DESTDIR=$(CURDIR)/dependencies
	touch $@
ifeq (aix,$(OS_FAMILY))
	# be clean
	slibclean
endif

# Test if compiler supports hardening flags
get-flags:
ifeq (aix,$(OS_FAMILY))
	# AIX doesn't automatically unload libraries from memory (and a loaded library cannot be overwritten)
	# some older versions may remain and prevent proper linking/installing
	# This pace is the 'beginning' of the make so do it here
	slibclean
endif
	$(eval HAVE_PROTECTION:=$(shell \
	FLAG_TEST_FILE=`mktemp /tmp/hardening.XXXXXX` ;\
	echo "void main() {}" > "$${FLAG_TEST_FILE}.c" ;\
	gcc $(TRY_CFLAGS) $(TRY_LDFLAGS) -o "$${FLAG_TEST_FILE}" "$${FLAG_TEST_FILE}.c" 2>/dev/null && echo "OK";\
	rm -f "$${FLAG_TEST_FILE}" "$${FLAG_TEST_FILE}".c ))

	$(eval SECURE_CFLAGS:=$(if $(HAVE_PROTECTION),$(TRY_CFLAGS)))
	$(eval SECURE_LDFLAGS:=$(if $(HAVE_PROTECTION),$(TRY_LDFLAGS)))

#####################################
# Install separated into components #
#####################################

install-cfengine: build-cfengine $(INSTALL_DEPS) rudder.8.gz
	mkdir -p $(DESTDIR)
	cp -rp $(CURDIR)/dependencies/* $(DESTDIR)
	# openssl useless parts
	cd $(DESTDIR)/opt/rudder && rm -rf bin/c_rehash lib/pkgconfig/openssl.pc ssl/misc/CA.pl ssl/misc/tsget ssl/openssl.cnf.dist openssl/man
	# pcre useless parts
	cd $(DESTDIR)/opt/rudder && rm -rf bin/pcregrep bin/pcretest
	# libxml useless parts
	cd $(DESTDIR)/opt/rudder && rm -rf bin/xmlcatalog bin/xmllint lib/xml2Conf.sh lib/cmake bin/xml2-config share/doc/libxml* 
	# Install cfengine manpages
	mkdir -p $(DESTDIR)/opt/rudder/share/man/man8
	cd $(DESTDIR)/opt/rudder/bin && for binary in cf-agent cf-promises cf-key cf-execd cf-serverd cf-net cf-runagent; do \
		LD_LIBRARY_PATH="$(DESTDIR)/opt/rudder/lib" ./$${binary} -M | gzip > $(DESTDIR)/opt/rudder/share/man/man8/$${binary}.8.gz; \
	done
	cd $(DESTDIR)/opt/rudder && rm -rf share/doc/cfengine
	printf "#!/bin/sh\necho 'cf-monitord has been removed from Rudder agent'\nexit 1" > $(DESTDIR)/opt/rudder/bin/cf-monitord


CPANM:=$(CURDIR)/App-cpanminus/bin/cpanm
# --notest because tests add new Test:: dependencies that cannot be installed properly
MODULE_INSTALL:=MAKEFLAGS= $(PERL) $(CPANM) $(CPAN_OPT) -L $(DESTDIR)/fusion/opt/rudder --from $(CPAN_URL) --notest
# List from README / Makefile.PL in fusion-inventory-agent
# -> requires + inventory and network recommends
FUSION_MODULES = File::Which LWP::UserAgent Net::IP Text::Template UNIVERSAL::require XML::TreePP Parse::EDID DateTime DateTime::TimeZone DateTime::TimeZone::Local::Unix Net::SNMP Net::NBName Thread::Queue Data::Dumper
# update sources at normation.com with the command: ./mirror $VAR_CPAN $FUSION_MODULES
# update core dependencies (for old perl versions) at normation.com with the command: ./mirror $VAR_CPAN Local::Win32 ExtUtils::MakeMaker parent IO::Compress::Bzip2 HTTP::Lite version CPAN::Meta::YAML CPAN::Meta::Requirements File::Temp Perl::OSType ExtUtils::Install threads::shared Module::Install URI::Escape ExtUtils::CBuilder Pod::Man ExtUtils::ParseXS TAP::Harness threads ExtUtils::Manifest Pod::Simple Module::Build Module::Implementation Test::Harness Module::CoreList File::Spec autodie Devel::PPPort Encode Pod::Escapes Class::C3 IPC::Cmd Digest::MD5 Locale::Maketext::Simple Module::Load Digest::base Params::Check Locale::Maketext::Simple

fusion-modules: App-cpanminus
	mkdir -p $(DESTDIR)/fusion/opt/rudder/lib/perl5
ifeq (true,$(USE_SYSTEM_PERL))
	# install installer dependencies on the system
	MAKEFLAGS= $(PERL) $(CPANM) $(CPAN_OPT) --from $(CPAN_URL) --notest Module::CoreList
endif
	$(MODULE_INSTALL) $(FUSION_MODULES)
	# remove perldoc (10Mb of timezone doc)
	find $(DESTDIR)/fusion/opt/rudder/lib/perl5 -type f -name "*.pod" -exec rm {} \;
	# Replace destdir by prefix in files generated by cpanm
	find $(DESTDIR)/fusion/opt/rudder/lib/perl5 -type f -name "*.packlist" -exec sed -i "s,$(DESTDIR)/fusion,,"  {} \;
	find $(DESTDIR)/fusion/opt/rudder/bin -type f -exec sed -i "s,$(DESTDIR)/fusion,,"  {} \;
	touch $@

FUSION_PATCHES_SHA = $(shell find patches/fusioninventory -type f | sort | xargs sha256sum | sha256sum | awk '{print $$1}')
FUSION_CACHE_PARAMETERS = --with-env name=fusion source=$(FUSION_SHA1) patches=$(FUSION_PATCHES_SHA) cpanm=$(CPANMINUS_SHA1) cpanurl=$(CPAN_URL) perl=$(PERL_SHA1)
FUSION_INSTALL = $(shell ../../build-caching get $(DESTDIR)/ $(FUSION_CACHE_PARAMETERS) || echo install-fusion-real)
install-fusion: $(FUSION_INSTALL)
	# save into cache if we built it
	if [ "$(FUSION_INSTALL)" != "" ]; then ../../build-caching put $(DESTDIR)/fusion $(FUSION_CACHE_PARAMETERS); fi
	cp -r $(DESTDIR)/fusion/* $(DESTDIR)/ && rm -rf $(DESTDIR)/fusion

install-fusion-real: fusioninventory-agent fusion-modules
# Fusion installation
	mkdir -p $(DESTDIR)/fusion/opt/rudder/share/fusion-utils
	cp -r fusioninventory-agent/share/* $(DESTDIR)/fusion/opt/rudder/share/fusion-utils/
ifeq ($(INSTALL),ginstall)
	# fusion doesn't know how to make install without gnu tools in the path
	$(SED) 's/\([^g]\)install -m/\1ginstall -m/' fusioninventory-agent/Makefile.PL > fusioninventory-agent/Makefile.PL.new
	mv fusioninventory-agent/Makefile.PL.new fusioninventory-agent/Makefile.PL
endif
ifeq (true,$(USE_SYSTEM_PERL))
	# install installer dependencies on the system
	MAKEFLAGS= $(PERL) $(CPANM) $(CPAN_OPT) --from $(CPAN_URL) --notest Module::Install
endif
	cd fusioninventory-agent && PERL_MM_USE_DEFAULT=1 $(PERL) -I. Makefile.PL --default PREFIX=$(RUDDER_DIR)
	cd fusioninventory-agent && $(MAKE) install DESTDIR=$(DESTDIR)/fusion
	# bug in fusion installer that doesn't set the right owner to some files
	chown root $(DESTDIR)/fusion/opt/rudder/share/fusioninventory
	chown root $(DESTDIR)/fusion/opt/rudder/share/fusioninventory/html
	# fusion configuration file is never used, do not include it to avoid mistakes
	rm -rf $(DESTDIR)/fusion/opt/rudder/etc/fusioninventory
	cp -r fusioninventory-agent/lib/FusionInventory $(DESTDIR)/fusion/opt/rudder/lib/perl5/

.PHONY: localdepends distclean depend build install clean mrproper install-cfengine install-fusion get-flags
