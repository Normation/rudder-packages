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

.DEFAULT_GOAL := build
SHELL = /bin/bash

RUDDER_VERSION_TO_PACKAGE =
RUDDER_MAJOR_VERSION := $(shell echo ${RUDDER_VERSION_TO_PACKAGE} | cut -d'.' -f 1-2)
# Original URL: http://repo1.maven.org/maven2/org/eclipse/jetty/jetty-home/${JETTY_RELEASE}/jetty-home-${JETTY_RELEASE}.tar.gz
JETTY_RELEASE = 10.0.9
JETTY_SHA256 = 69e4508d69d036e7569c82f242ef566b3ca7ad9ba7ad877408923e2abc1521e9
# Original URL: https://www.openldap.org/software/download/OpenLDAP/openldap-release/openldap-2.6.2.tgz
OPENLDAP_RELEASE = 2.6.2
OPENLDAP_SHA256 = 81d09345232eb62486ecf5acacd2c56c0c45b4a6c8c066612e7f421a23a1cf87
TMP_DIR := $(shell mktemp -dq)
RELEASE_TYPE := $(shell if echo ${RUDDER_VERSION_TO_PACKAGE} | grep -q git; then echo nightly; else echo release; fi)

DESTDIR = $(CURDIR)/target
APACHE_VHOSTDIR = apache2/sites-available
APACHE_CONFDIR = apache2/conf-available
JETTY_SCRIPT=jetty.sh
WEBAPPDIR = rudder-sources/rudder/webapp/sources
LANGDIR = rudder-sources/rudder/policies
CORE_RESOURCES = $(WEBAPPDIR)/rudder/rudder-core/src/main/resources
WEB_RESOURCES = $(WEBAPPDIR)/rudder/rudder-web/src/main/resources

SECURE_CFLAGS = -fstack-protector-strong -D_FORTIFY_SOURCE=2 -fPIE
SECURE_LDFLAGS = -fstack-protector-strong -Wl,-z,relro -Wl,-z,now -pie

PROXY_ENV = $(if $(PROXY), http_proxy=$(PROXY))
# Usage: $(GET) <destination_file> <url> <hash>
# Pass an empty string to skip hash check
# grep 'GET=' */SOURCES/Makefile to patch everywhere
GET=get() { $(PROXY_ENV) curl --silent --location --fail --output "$$1.part" "$$2" && { openssl dgst -sha256 "$$1.part" | grep -q "$$3" || { echo "Wrong checksum, aborting"; exit 1; }; } && mv "$$1.part" "$$1"; }; get

# Defauth PATHs
DESTDIR = $(CURDIR)/target

localdepends: initial-promises initial-ncf rudder-sources rudder-doc rudder.war jetty openldap-source
	rm -rf $(TMP_DIR)

openldap-source:
	$(GET) ./openldap.tgz https://repository.rudder.io/build-dependencies/openldap/openldap-$(OPENLDAP_RELEASE).tgz $(OPENLDAP_SHA256)
	tar xzf ./openldap.tgz -C .
	mv ./openldap-$(OPENLDAP_RELEASE) ./openldap-source

	# Apply patches
	#for PATCHNAME in patches/openldap/*.patch; do echo "Applying $$PATCHNAME..."; patch -d ./openldap-source -p1 < $$PATCHNAME || exit; done
	# Make sure there were no rejects
	test `find ./openldap-source -name \*.rej | wc -l` = 0
	rm -rf ./openldap.tgz

jetty:
	$(GET) $(TMP_DIR)/jetty.tgz https://repository.rudder.io/build-dependencies/jetty/jetty-home-$(JETTY_RELEASE).tar.gz $(JETTY_SHA256)
	tar xzf $(TMP_DIR)/jetty.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/jetty-home-$(JETTY_RELEASE) jetty
	rm -rf $(TMP_DIR)

	# Remove useless / demo elements from Jetty
	# jetty 10 is clean now 
	# rm -rf jetty/...

	# Change jetty.sh before distincts files
	patch -p0 -s < patches/jetty/jetty-init-java-options.patch
	patch -p0 -s < patches/jetty/jetty-init-umask.patch
	patch -p0 -s < patches/jetty/jetty-init-stop-fix.patch
	patch -p0 -s < patches/jetty/jetty-init-sizecheck.patch
	patch -p0 -s < patches/jetty/jetty-init-prevent-false-failed-starts.patch
	patch -p0 -s < patches/jetty/jetty-init-redirect-stderrout.patch
	patch -p0 -s < patches/jetty/jetty-init-stop-forcestop.patch

	cp jetty/bin/jetty.sh ./jetty/bin/jetty-rpm.sh
	patch -p0 -s < patches/jetty/jetty-init-softokn-version-check.patch

	cp jetty/bin/jetty-rpm.sh jetty/bin/jetty-sles.sh
	patch -p0 -s < patches/jetty/jetty-init-sles.patch
	patch -p0 -s < patches/jetty/jetty-init-ulimit.patch

	# Provide jetty's init script to the debian package's standard location
	cp rudder-jetty.default ../debian/rudder-jetty.default

	# Make sure there were no rejects
	test `find . -name \*.rej | wc -l` = 0

initial-promises: ./rudder-sources
	rm -rf ./initial-promises/
	cp -r ./rudder-sources/rudder-techniques/initial-promises/node-server/ ./initial-promises

initial-ncf: ./rudder-sources ./initial-promises
	rm -rf ./initial-ncf
	cp -r ./rudder-sources/ncf/tree ./initial-ncf

rudder.war: rudder-sources
	# Direct download the war
	./mvn-like $(WEBAPPDIR)/rudder/pom.xml com.normation.rudder rudder-web rudder.war

rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2 https://repository.rudder.io/sources/$(RUDDER_VERSION_TO_PACKAGE)/rudder-sources-$(RUDDER_VERSION_TO_PACKAGE).tar.bz2 ""

rudder-sources: rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/
	# Remove tests folders we don't want to package
	find rudder-sources/rudder-techniques -name "tests" -type d | xargs -r rm -r

rudder-doc:
	# Get user manual from rudder-project.org and rename directory containing it to rudder-doc
	$(GET) doc-${RUDDER_MAJOR_VERSION}.tar.gz https://docs.rudder.io/archives/doc-${RUDDER_MAJOR_VERSION}.tar.gz ""
	tar -xf doc-${RUDDER_MAJOR_VERSION}.tar.gz
	mkdir -p rudder-doc
	mv doc-${RUDDER_MAJOR_VERSION} rudder-doc/html

PATCHES_SHA = $(shell find patches/ -type f | sort | xargs sha256sum | sha256sum | awk '{print $$1}')
CACHE_PARAMETERS = --with-env name=openldap ldap=$(OPENLDAP_SHA256) patches=$(PATCHES_SHA) release_type=$(RELEASE_TYPE)
BUILD_LDAP = $(shell ../../build-caching get openldap-source/ $(CACHE_PARAMETERS) || echo build-ldap)
build: $(BUILD_LDAP) rudder-sources build-language rudder-doc jetty rudder.war
	# save ldap build into cache
	if [ "$(BUILD_LDAP)" != "" ]; then ../../build-caching put openldap-source/ $(CACHE_PARAMETERS); fi
	touch $@

# for centos7
DEBUGOPT:=$(shell make -v --debug=n >/dev/null 2>&1 && echo --debug=n)
build-ldap: openldap-source
	cd openldap-source && CFLAGS="-Wno-format-extra-args -O2 ${SECURE_CFLAGS}" LDFLAGS="${SECURE_LDFLAGS}" ./configure --prefix=/opt/rudder --libdir=/opt/rudder/lib/ldap --enable-dynamic --enable-debug --enable-modules --enable-monitor=mod --enable-dynlist=mod --enable-mdb=yes --enable-hdb=no --enable-bdb=no
	cd openldap-source && make $(DEBUGOPT) depend
	cd openldap-source && make $(DEBUGOPT)
	touch $@

build-language:
	cd $(LANGDIR) && make $(DEBUGOPT) build

rudder-server-version:
	# versions details from the source tarbal
	[ -f rudder-sources/versions ] && cp ./rudder-sources/versions $@ || echo "rudder_version=unknown" > $@
	# version details from the ci checkout
	[ -f ../../versions ] && cat ../../versions >> $@ || true

install: build rudder-server-version initial-promises initial-ncf
	mkdir -p $(DESTDIR)/opt/rudder/etc/postgresql/
	mkdir -p $(DESTDIR)/usr/lib/systemd/system
	mkdir -p $(DESTDIR)/opt/rudder/share/package-scripts/
	mkdir -p $(DESTDIR)/opt/rudder/share/versions/
	install -m 644 rudder-sources/rudder/webapp/sources/rudder/rudder-core/src/main/resources/reportsSchema.sql $(DESTDIR)/opt/rudder/etc/postgresql/
	install -m 644 rudder-server.service $(DESTDIR)/usr/lib/systemd/system/
	install -m 755 rudder-server-postinst $(DESTDIR)/opt/rudder/share/package-scripts/
	install -m 644 rudder-server-version $(DESTDIR)/opt/rudder/share/versions/
	mkdir -p $(DESTDIR)/opt/rudder/etc/
	mkdir -p $(DESTDIR)/opt/rudder/etc/plugins/licenses
	mkdir -p $(DESTDIR)/opt/rudder/etc/hooks.d/
	mkdir -p $(DESTDIR)/opt/rudder/bin/
	mkdir -p $(DESTDIR)/opt/rudder/share/webapps/
	mkdir -p $(DESTDIR)/opt/rudder/share/rudder-plugins/
	mkdir -p $(DESTDIR)/opt/rudder/share/tools
	mkdir -p $(DESTDIR)/opt/rudder/share/plugins/
	mkdir -p $(DESTDIR)/opt/rudder/share/upgrade-tools/
	mkdir -p $(DESTDIR)/opt/rudder/share/certificates/
	mkdir -p $(DESTDIR)/opt/rudder/share/selinux/
	mkdir -p $(DESTDIR)/opt/rudder/share/package-scripts/
	mkdir -p $(DESTDIR)/var/rudder/inventories/received
	mkdir -p $(DESTDIR)/var/rudder/run
	mkdir -p $(DESTDIR)/var/rudder/ldap/openldap-data
	mkdir -p $(DESTDIR)/var/log/rudder/apache2/
	mkdir -p $(DESTDIR)/var/log/rudder/webapp
	mkdir -p $(DESTDIR)/var/log/rudder/ldap
	mkdir -p $(DESTDIR)/var/rudder/run
	mkdir -p $(DESTDIR)/etc/$(APACHE_VHOSTDIR)/
	mkdir -p $(DESTDIR)/etc/$(APACHE_CONFDIR)/
	mkdir -p $(DESTDIR)/etc/sysconfig/
	mkdir -p $(DESTDIR)/etc/rsyslog.d
	mkdir -p $(DESTDIR)/etc/default
	mkdir -p $(DESTDIR)/usr/share/doc/rudder
	mkdir -p $(DESTDIR)/usr/share/
	mkdir -p $(DESTDIR)/usr/bin/
	mkdir -p $(DESTDIR)/usr/lib/systemd/system/
	mkdir -p $(DESTDIR)/opt/rudder/share/versions/

	cd openldap-source && make $(DEBUGOPT) install DESTDIR=$(DESTDIR)

	# Install language
	cd $(LANGDIR) && make $(DEBUGOPT) install DESTDIR=$(DESTDIR)

	# Install openldap
	install -m 640 slapd.conf $(DESTDIR)/opt/rudder/etc/openldap/slapd.conf
	install -m 644 $(WEBAPPDIR)/ldap-inventory/inventory-repository/src/main/resources/ldap/inventory.schema $(DESTDIR)/opt/rudder/etc/openldap/schema/
	install -m 644 $(CORE_RESOURCES)/ldap/rudder.schema $(DESTDIR)/opt/rudder/etc/openldap/schema/
	install -m 644 rsyslog/rudder-slapd.conf $(DESTDIR)/etc/rsyslog.d/rudder-slapd.conf
	install -m 644 rudder-slapd.service $(DESTDIR)/usr/lib/systemd/system/rudder-slapd.service
	[ $$(systemctl --version | head -1 | cut -d' ' -f2) -gt 232 ] && sed -i '/\[Service\]/ r rudder-slapd-hardening' $(DESTDIR)/usr/lib/systemd/system/rudder-slapd.service || true


	# Install helper scripts
	install -m 755 rudder-init $(DESTDIR)/opt/rudder/bin/
	install -m 755 rudder-node-to-relay $(DESTDIR)/opt/rudder/bin/
	install -m 755 rudder-metrics-reporting $(DESTDIR)/opt/rudder/bin/
	install -m 755 rudder-reload-cf-serverd $(DESTDIR)/opt/rudder/bin/
	install -m 755 rudder_synchronize.py ${DESTDIR}/opt/rudder/bin/

	install -m 644 $(WEB_RESOURCES)/demo-rudder-users.xml $(DESTDIR)/opt/rudder/etc/rudder-users.xml
	install -m 644 $(CORE_RESOURCES)/ldap/bootstrap.ldif $(DESTDIR)/opt/rudder/share/
	install -m 644 $(CORE_RESOURCES)/ldap/init-policy-server.ldif $(DESTDIR)/opt/rudder/share/
	install -m 644 $(WEB_RESOURCES)/configuration.properties.sample $(DESTDIR)/opt/rudder/etc/rudder-web.properties
	install -m 644 $(WEB_RESOURCES)/logback.xml $(DESTDIR)/opt/rudder/etc/
	cp -r rudder-sources/rudder-techniques/techniques/ $(DESTDIR)/opt/rudder/share/

	mkdir -p $(DESTDIR)/usr/share/ncf
	cp -r rudder-sources/ncf/tools $(DESTDIR)/usr/share/ncf/
	cp -r rudder-sources/ncf/tree $(DESTDIR)/usr/share/ncf/
	install -m 755 rudder-sources/ncf/ncf $(DESTDIR)/usr/share/ncf/
	install -m 644 rudder.war $(DESTDIR)/opt/rudder/share/webapps/rudder.war

	cp -rf $(WEB_RESOURCES)/load-page $(DESTDIR)/opt/rudder/share/
	install -m 644 $(CORE_RESOURCES)/reportsInfo.xml $(DESTDIR)/opt/rudder/etc/
	install -m 644 rudder-apache-webapp-common.conf $(DESTDIR)/opt/rudder/etc/rudder-apache-webapp-common.conf
	install -m 644 rudder-apache-webapp-ssl.conf $(DESTDIR)/opt/rudder/etc/rudder-apache-webapp-ssl.conf
	install -m 644 rudder-apache-webapp-nossl.conf $(DESTDIR)/opt/rudder/etc/rudder-apache-webapp-nossl.conf
	install -m 644 rudder-webapp-apache $(DESTDIR)/etc/sysconfig/rudder-webapp-apache

	cp -r $(CORE_RESOURCES)/hooks.d $(DESTDIR)/opt/rudder/etc/

	install -m 644 rudder.xml $(DESTDIR)/opt/rudder/share/webapps/

	# Install upgrade tools and migration scripts

	## SQL init
	install -m 644 $(CORE_RESOURCES)/reportsSchema.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	## SQL migration
	install -m 644 $(CORE_RESOURCES)/Migration/dbMigration-6.1-6.2-remove-unused-index-on-ruddersysevents.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	install -m 644 $(CORE_RESOURCES)/Migration/dbMigration-6.1-7.0-compliance_computation_change.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	install -m 644 $(CORE_RESOURCES)/Migration/dbMigration-6.x-7.0-drop-historization-table.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	install -m 644 $(CORE_RESOURCES)/Migration/dbMigration-7.0-7.1-serial_to_reportid_change.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	install -m 644 $(CORE_RESOURCES)/Migration/dbMigration-7.1-7.2-create-campaign-table.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/


	install -m 755 rudder-upgrade $(DESTDIR)/opt/rudder/bin/

	install -m 640 rudder-passwords.conf $(DESTDIR)/opt/rudder/etc/

	# Add rudder-metrics-reporting
	install -m 755 rudder-metrics-reporting $(DESTDIR)/opt/rudder/bin/
	install -m 644 ca-bundle.crt $(DESTDIR)/opt/rudder/share/certificates/

	# Install documentation
	cp -rf rudder-doc/html $(DESTDIR)/usr/share/doc/rudder

	# Install rudder fix repository permissions script
	install -m 755 rudder-fix-repository-permissions $(DESTDIR)/opt/rudder/bin/

	# Install gitignore file for our git repo
	mkdir -p $(DESTDIR)/var/rudder/configuration-repository/

	cp -a jetty $(DESTDIR)/opt/rudder
	cp -a rudder-jetty-base $(DESTDIR)/opt/rudder/etc

	# Init script
	install -m 755 jetty/bin/$(JETTY_SCRIPT) $(DESTDIR)/opt/rudder/bin/rudder-jetty.sh
	install -m 644 rudder-jetty.default $(DESTDIR)/etc/default/rudder-jetty
	install -m 644 rudder-jetty.conf $(DESTDIR)/opt/rudder/etc/

	install -m 644 rudder-jetty.service $(DESTDIR)/usr/lib/systemd/system/

	cp -r initial-promises/ $(DESTDIR)/opt/rudder/share/
	cp -r initial-ncf/ $(DESTDIR)/opt/rudder/share/

	touch $@

clean:
	rm -rf rudder-users.xml
	rm -rf maven/
	rm -rf .m2/
	rm -rf rudder-doc
	rm -rf .gitignore
	rm -rf settings-external.xml
	rm -rf jetty
	rm -f .debian/rudder-jetty.init
	rm -f .debian/rudder-jetty.default
	rm -rf $(TMP_DIR)
	rm -f build install
	rm -rf openldap-source

distclean: clean
	rm -rf maven.tgz
	rm -rf initial-promises initial-ncf
	rm -rf $(TMP_DIR)

# distclean should remove everything except rudder-sources.tar.bz2 since it can be brought by by external means
mrproper: distclean
	rm -f ./rudder-sources.tar.bz2

.PHONY: build install clean localdepends distclean mrproper
