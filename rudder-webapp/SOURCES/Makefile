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

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>
RUDDER_MAJOR_VERSION := $(shell echo ${RUDDER_VERSION_TO_PACKAGE} | cut -d'.' -f 1-2)
VIRTUALENV_RELEASE = 16.5.0
VIRTUALENV_SHA256 = 15ee248d13e4001a691d9583948ad3947bcb8a289775102e4c4aa98a8b7a6d73
MAVEN_RELEASE = 3.5.4
MAVEN_SHA256 = ce50b1c91364cb77efe3776f756a6d92b76d9038b0a0782f7d53acf1e997a14d
JETTY_RELEASE = 9.4.11
DATE_RELEASE = 20180605
JETTY_SHA256 = c286e87f36d56ef40821c5acb99acf3f90873d39bdbc1851f482c556c2dca5ae
OPENLDAP_RELEASE = 2.4.47
OPENLDAP_SHA256 = f54c5877865233d9ada77c60c0f69b3e0bfd8b1b55889504c650047cc305520b
TMP_DIR := $(shell mktemp -dq)
PYTHON = python3

DESTDIR = $(CURDIR)/target
APACHE_VHOSTDIR = apache2/sites-available
APACHE_CONFDIR = apache2/conf-available
JETTY_SCRIPT=jetty.sh

PROXY_ENV = $(if $(PROXY), http_proxy=$(PROXY))
# Usage: $(GET) <destination_file> <url> <hash>
# Pass an empty string to skip hash check
# grep 'GET=' */SOURCES/Makefile to patch everywhere
GET=get() { $(PROXY_ENV) curl  --silent --location --fail --output "$$1.part" "$$2" && { openssl dgst -sha256 "$$1.part" | grep -q "$$3" || { echo "Wrong checksum, aborting"; exit 1; }; } && mv "$$1.part" "$$1"; }; get

localdepends: initial-promises initial-ncf rudder-sources rudder-doc rudder.war jetty openldap-source
	rm -rf $(TMP_DIR)

openldap-source:
	# Original URL: ftp://ftp.openldap.org/pub/OpenLDAP/openldap-release/openldap-$(OPENLDAP_RELEASE).tgz
	$(GET) ./openldap.tgz https://repository.rudder.io/build-dependencies/openldap/openldap-$(OPENLDAP_RELEASE).tgz $(OPENLDAP_SHA256)
	tar xzf ./openldap.tgz -C .
	mv ./openldap-$(OPENLDAP_RELEASE) ./openldap-source
	
	# Apply patches
	for PATCHNAME in patches/openldap/*.patch; do echo "Applying $$PATCHNAME..."; patch -d ./openldap-source -p1 < $$PATCHNAME; done
	# Make sure there were no rejects
	test `find ./openldap-source -name \*.rej | wc -l` = 0
	rm -rf ./openldap.tgz

jetty:
	# Original URL: http://repo1.maven.org/maven2/org/eclipse/jetty/jetty-distribution/$(JETTY_RELEASE).v$(DATE_RELEASE)/jetty-distribution-$(JETTY_RELEASE).v$(DATE_RELEASE).tar.gz
	$(GET) $(TMP_DIR)/jetty.tgz https://repository.rudder.io/build-dependencies/jetty/jetty-distribution-$(JETTY_RELEASE).v$(DATE_RELEASE).tar.gz $(JETTY_SHA256)
	tar xzf $(TMP_DIR)/jetty.tgz -C $(TMP_DIR)
	mv $(TMP_DIR)/jetty-distribution-$(JETTY_RELEASE).v$(DATE_RELEASE) jetty
	rm -rf $(TMP_DIR)

	# Remove useless / demo elements from Jetty
	# jetty9 is clean now - only demo-base
	rm -rf jetty/demo-base

	# Change jetty.sh before distincts files
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

	# Restore the name for log file from version of Rudder before 4.3 (see https://www.rudder-project.org/redmine/issues/12607)
	patch -p0 -s < patches/jetty/jetty-console-capture-restore-log-filename.patch

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
	./mvn-like rudder-sources/rudder/pom.xml com.normation.rudder rudder-web rudder.war

rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2 https://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2 ""

rudder-sources: rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/
	# Remove tests folders we don't want to package
	find rudder-sources/rudder-techniques -name "tests" -type d | xargs -r rm -r
	# Set version in technique editor files to use correctly browser cache (See https://issues.rudder.io/issues/14194)
	sed -i "s/version=dev/version=${RUDDER_VERSION_TO_PACKAGE}/" rudder-sources/ncf/builder/index.html


rudder-doc:
	# Get user manual from rudder-project.org and rename directory containing it to rudder-doc
	$(GET) doc-${RUDDER_MAJOR_VERSION}.tar.gz https://docs.rudder.io/archives/doc-${RUDDER_MAJOR_VERSION}.tar.gz ""
	tar -xzf doc-${RUDDER_MAJOR_VERSION}.tar.gz
	mkdir -p rudder-doc
	mv doc-${RUDDER_MAJOR_VERSION} rudder-doc/html

virtualenv/virtualenv.py:
	# Original URL: https://pypi.python.org/packages/source/v/virtualenv/virtualenv-12.0.7.tar.gz
	$(GET) virtualenv.tgz https://repository.rudder.io/build-dependencies/virtualenv/virtualenv-$(VIRTUALENV_RELEASE).tar.gz $(VIRTUALENV_SHA256)
	tar -xzf virtualenv.tgz
	mv virtualenv-$(VIRTUALENV_RELEASE)/ virtualenv/

PATCHES_SHA = $(shell find patches/ -type f | xargs | sha256sum | awk '{print $$1}')
CACHE_PARAMETERS = --with-env name=openldap ldap=$(OPENLDAP_SHA256) patches=$(PATCHES_SHA)
BUILD_LDAP = $(shell ../../build-caching get openldap-source/ $(CACHE_PARAMETERS) || echo build-ldap)
build: $(BUILD_LDAP) rudder-sources virtualenv/virtualenv.py rudder-doc jetty rudder.war
	# save ldap build into cache
	if [ "$(BUILD_LDAP)" != "" ]; then ../../build-caching put openldap-source/ $(CACHE_PARAMETERS); fi
	$(PYTHON) virtualenv/virtualenv.py ncf-api-virtualenv
	ncf-api-virtualenv/bin/pip install -r rudder-sources/ncf/api/requirements.txt
	for i in easy_install python pip; do rm -f ncf-api-virtualenv/bin/$${i}*; done
	touch $@

build-ldap: openldap-source
	cd openldap-source && ./configure --prefix=/opt/rudder --libdir=/opt/rudder/lib/ldap --enable-dynamic --enable-debug --enable-modules --enable-monitor=mod --enable-dynlist=mod --enable-mdb=yes --enable-hdb=no --enable-bdb=no
	cd openldap-source && make depend
	cd openldap-source && make
	touch $@

# install into DESTDIR
install: build initial-promises initial-ncf
	mkdir -p $(DESTDIR)/opt/rudder/etc/
	mkdir -p $(DESTDIR)/opt/rudder/etc/plugins/licenses
	mkdir -p $(DESTDIR)/opt/rudder/etc/server-roles.d/
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
	mkdir -p $(DESTDIR)/var/rudder/inventories/failed
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
	mkdir -p $(DESTDIR)/usr/share/ncf-api-virtualenv/share/selinux/
	mkdir -p $(DESTDIR)/usr/lib/systemd/system/
	mkdir -p $(DESTDIR)/var/lib/ncf-api-venv/
	cd openldap-source && make install DESTDIR=$(DESTDIR)

	# Install openldap
	install -m 640 slapd.conf $(DESTDIR)/opt/rudder/etc/openldap/slapd.conf
	install -m 644 rudder-sources/rudder/webapp/sources/ldap-inventory/inventory-repository/src/main/resources/ldap/inventory.schema $(DESTDIR)/opt/rudder/etc/openldap/schema/
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/ldap/rudder.schema $(DESTDIR)/opt/rudder/etc/openldap/schema/
	install -m 644 rsyslog/rudder-slapd.conf $(DESTDIR)/etc/rsyslog.d/rudder-slapd.conf
	install -m 644 rudder-slapd.service $(DESTDIR)/usr/lib/systemd/system/rudder-slapd.service

	# Install helper scripts
	install -m 755 rudder-init $(DESTDIR)/opt/rudder/bin/
	install -m 755 rudder-node-to-relay $(DESTDIR)/opt/rudder/bin/
	install -m 755 rudder-root-rename $(DESTDIR)/opt/rudder/bin/
	install -m 755 rudder-plugin $(DESTDIR)/opt/rudder/bin/
	install -m 755 rudder-metrics-reporting $(DESTDIR)/opt/rudder/bin/
	install -m 755 rudder-reload-cf-serverd $(DESTDIR)/opt/rudder/bin/
	
	install -m 644 rudder-sources/rudder/rudder-web/src/main/resources/demo-rudder-users.xml $(DESTDIR)/opt/rudder/etc/rudder-users.xml
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/ldap/bootstrap.ldif $(DESTDIR)/opt/rudder/share/
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/ldap/init-policy-server.ldif $(DESTDIR)/opt/rudder/share/
	install -m 644 rudder-sources/rudder/rudder-web/src/main/resources/configuration.properties.sample $(DESTDIR)/opt/rudder/etc/rudder-web.properties
	install -m 644 rudder-sources/rudder/rudder-web/src/main/resources/logback.xml $(DESTDIR)/opt/rudder/etc/
	cp -r rudder-sources/rudder-techniques/techniques/ $(DESTDIR)/opt/rudder/share/
	
	mkdir -p $(DESTDIR)/usr/share/ncf
	cp -r rudder-sources/ncf/{api,builder,tools,tree} $(DESTDIR)/usr/share/ncf/
	install -m 755 rudder-sources/ncf/ncf $(DESTDIR)/usr/share/ncf/
	install -m 644 rudder.war $(DESTDIR)/opt/rudder/share/webapps/rudder.war
	
	cp -rf rudder-sources/rudder/rudder-web/src/main/resources/load-page $(DESTDIR)/opt/rudder/share/
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/reportsInfo.xml $(DESTDIR)/opt/rudder/etc/
	install -m 644 rudder-apache-webapp-common.conf $(DESTDIR)/opt/rudder/etc/rudder-apache-webapp-common.conf
	install -m 644 rudder-apache-webapp-ssl.conf $(DESTDIR)/opt/rudder/etc/rudder-apache-webapp-ssl.conf
	install -m 644 rudder-apache-webapp-nossl.conf $(DESTDIR)/opt/rudder/etc/rudder-apache-webapp-nossl.conf
	install -m 644 rudder-webapp-apache $(DESTDIR)/etc/sysconfig/rudder-webapp-apache
	
	cp -r rudder-sources/rudder/rudder-core/src/main/resources/hooks.d $(DESTDIR)/opt/rudder/etc/
	
	install -m 644 rudder.xml $(DESTDIR)/opt/rudder/share/webapps/
	
	cp -r ncf-api-virtualenv/* $(DESTDIR)/usr/share/ncf-api-virtualenv/
	
	install -m 644 ncf_api_flask_app.wsgi $(DESTDIR)/usr/share/ncf-api-virtualenv/
	install -m 644 ncf-api-virtualenv.conf $(DESTDIR)/etc/$(APACHE_CONFDIR)/
	
	# Install upgrade tools and migration scripts
	
	## SQL migration
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-4.1.x-4.1.12-add-compliancelevel-table.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-4.1.x-4.1.21-drop-rulesgroupjoin-constraint.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-4.3.x-4.3.8-correct-indexes-on-compliancelevel.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-5.0.x-5.0.7-tune-autovacuum_on_table_basis.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-5.0.x-5.0.12-composite-index-on-ruddersysevents.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	install -m 644 rudder-sources/rudder/rudder-core/src/main/resources/Migration/dbMigration-5.0.x-5.0.13-remove-autovacuum-on-ruddersysevents.sql $(DESTDIR)/opt/rudder/share/upgrade-tools/
	
	install -m 755 rudder-upgrade $(DESTDIR)/opt/rudder/bin/
	
	install -m 644 rudder-webapp $(DESTDIR)/opt/rudder/etc/server-roles.d/
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
	install -m 644 configuration-repository-gitignore $(DESTDIR)/var/rudder/configuration-repository/.gitignore
	
	cp -a jetty $(DESTDIR)/opt/rudder
	cp -a rudder-jetty-base $(DESTDIR)/opt/rudder/etc
	
	# Init script
	install -m 755 jetty/bin/$(JETTY_SCRIPT) $(DESTDIR)/opt/rudder/bin/rudder-jetty.sh
	install -m 644 rudder-jetty.default $(DESTDIR)/etc/default/rudder-jetty
	install -m 644 rudder-jetty.conf $(DESTDIR)/opt/rudder/etc/

	install -m 755 rudder-webapp-postinst $(DESTDIR)/opt/rudder/share/package-scripts/
	install -m 644 rudder-jetty.service $(DESTDIR)/usr/lib/systemd/system/

	cp -r initial-promises/ $(DESTDIR)/opt/rudder/share/
	cp -r initial-ncf/ $(DESTDIR)/opt/rudder/share/

	touch $@

clean:
	rm -rf rudder-users.xml
	rm -rf maven/
	rm -rf .m2/
	rm -rf rudder-sources
	rm -rf rudder-doc
	rm -rf .gitignore
	rm -rf settings-external.xml
	rm -rf virtualenv/
	rm -rf ncf-api-virtualenv
	rm -rf jetty
	rm -f .debian/rudder-jetty.init
	rm -f .debian/rudder-jetty.default
	rm -rf $(TMP_DIR)
	rm -f build install
	rm -rf openldap-source

# distclean should remove everything except rudder-sources.tar.bz2 since it can be brought by by external means
distclean: clean
	rm -rf maven.tgz
	rm -f virtualenv.tgz
	rm -rf initial-promises initial-ncf
	rm -rf $(TMP_DIR)

mrproper: distclean
	rm -f rudder-sources.tar.bz2

.PHONY: install clean localdepends distclean mrproper
