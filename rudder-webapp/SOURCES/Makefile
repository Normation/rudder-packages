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

RUDDER_VERSION_TO_PACKAGE = <put Rudder version or version-snapshot here>
RUDDER_MAJOR_VERSION := $(shell echo ${RUDDER_VERSION_TO_PACKAGE} | cut -d'.' -f 1-2)
VIRTUALENV_RELEASE = 16.0.0
VIRTUALENV_SHA256 = ca07b4c0b54e14a91af9f34d0919790b016923d157afda5efdde55c96718f752
MAVEN_RELEASE = 3.5.4
MAVEN_SHA256 = ce50b1c91364cb77efe3776f756a6d92b76d9038b0a0782f7d53acf1e997a14d
JETTY_RELEASE = 9.4.11
DATE_RELEASE = 20180605
JETTY_SHA256 = c286e87f36d56ef40821c5acb99acf3f90873d39bdbc1851f482c556c2dca5ae
TMP_DIR := $(shell mktemp -dq)

MAVEN_PROXY := $(if $(PROXY), $(shell echo "$(PROXY)" |  perl -ne ' \
    if (m|(https?)://(?:([^:@]+)(?::([^@]+))?\@)?([^:/]+)(?::([0-9]+))?|) { \
        chomp; \
        my $$proto = "<protocol>$$1</protocol>"; \
        my $$user = defined($$2) ? "<username>$$2</username>" : ""; \
        my $$pass = defined($$3) ? "<password><![CDATA[$$3]]></password>" : ""; \
        my $$host = "<host>$$4</host>";  \
        my $$id   = "<id>$$4</id>"; \
        my $$port = defined($5) ? "<port>$$5</port>" : ""; \
        print "<proxies> <proxy> <active>true</active> $$id $$proto $$user $$pass $$host $$port </proxy> </proxies>"; \
    }'))

DESTDIR = $(CURDIR)/target
APACHE_VHOSTDIR = apache2/sites-available
APACHE_CONFDIR = apache2/conf-available
JETTY_SCRIPT=jetty.sh

# We are on an nrm builder
ifeq (,$(wildcard /tmp/nrm_builder))
NRM := true
else
NRM := false
NEXUS_IGNORE := || true
endif


PROXY_ENV = $(if $(PROXY), http_proxy=$(PROXY))
# Usage: $(GET) <destination_file> <url> <hash>
# Pass an empty string to skip hash check
# grep 'GET=' */SOURCES/Makefile to patch everywhere
GET=get() { $(PROXY_ENV) curl -s --http1.1 -L -o "$$1.part" "$$2" && { openssl dgst -sha256 "$$1.part" | grep -q "$$3" || { echo "Wrong checksum, aborting"; exit 1; }; } && mv "$$1.part" "$$1"; }; get

localdepends: rudder-sources rudder-doc rudder.war endpoint.war jetty
	rm -rf $(TMP_DIR)

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


maven/bin/mvn:
	# Original URL: http://apache.multidist.com/maven/binaries/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz
	$(GET) maven.tgz.dl https://repository.rudder.io/build-dependencies/maven/apache-maven-$(MAVEN_RELEASE)-bin.tar.gz $(MAVEN_SHA256)
	mv maven.tgz.dl maven.tgz
	tar -xzf maven.tgz -C .
	rm -rf maven
	mv apache-maven-$(MAVEN_RELEASE) maven
	sed 's|<!--PROXY-->|$(MAVEN_PROXY)|g' settings-external.xml.tpl > settings-external.xml

rudder.war: maven/bin/mvn rudder-sources endpoint.war
	maven/bin/mvn -s settings-external.xml --batch-mode org.apache.maven.plugins:maven-dependency-plugin:3.0.0:copy -Dmaven.repo.local=.m2/repository -Dartifact=com.normation.rudder:rudder-web:$$(sed -n '/<parent>/,/<.parent>/s/.*<version>\(.*\)<.version>.*/\1/p' rudder-sources/rudder/pom.xml):war -DoutputDirectory=. && mv rudder-web*.war rudder.war $(NEXUS_IGNORE)
ifeq (false,$(NRM))
	if [ ! -f rudder.war ]; then cd rudder-sources/rudder            && ../../maven/bin/mvn -s settings-external.xml --batch-mode -Dmaven.repo.local=.m2/repository -Dmaven.test.skip=true -U install; fi
	if [ ! -f rudder.war ]; then mv rudder-sources/rudder/rudder-web/target/rudder-web*.war rudder.war; fi
endif

endpoint.war: maven/bin/mvn rudder-sources
	maven/bin/mvn -s settings-external.xml --batch-mode org.apache.maven.plugins:maven-dependency-plugin:3.0.0:copy -Dmaven.repo.local=.m2/repository  -Dartifact=com.normation.inventory:inventory-provisioning-web:$$(sed -n '/<parent>/,/<.parent>/s/.*<version>\(.*\)<.version>.*/\1/p' rudder-sources/ldap-inventory/pom.xml):war -DoutputDirectory=. && mv inventory-provisioning-web*.war endpoint.war $(NEXUS_IGNORE)
ifeq (false,$(NRM))
	if [ ! -f endpoint.war ]; then cd rudder-sources/rudder-parent-pom && ../../maven/bin/mvn -s settings-external.xml --batch-mode -Dmaven.repo.local=.m2/repository -Dmaven.test.skip=true -U install; fi
	if [ ! -f endpoint.war ]; then cd rudder-sources/rudder-commons    && ../../maven/bin/mvn -s settings-external.xml --batch-mode -Dmaven.repo.local=.m2/repository -Dmaven.test.skip=true -U install; fi
	if [ ! -f endpoint.war ]; then cd rudder-sources/scala-ldap        && ../../maven/bin/mvn -s settings-external.xml --batch-mode -Dmaven.repo.local=.m2/repository -Dmaven.test.skip=true -U install; fi
	if [ ! -f endpoint.war ]; then cd rudder-sources/ldap-inventory    && ../../maven/bin/mvn -s settings-external.xml --batch-mode -Dmaven.repo.local=.m2/repository -Dmaven.test.skip=true -U install; fi
	if [ ! -f endpoint.war ]; then mv rudder-sources/rudder/rudder-web/target/inventory-provisioning-web*.war endpoint.war; fi
endif

rudder-sources.tar.bz2:
	$(GET) rudder-sources.tar.bz2 https://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2 ""

rudder-sources: rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/
	# Remove tests folders we don't want to package
	find rudder-sources/rudder-techniques -name "tests" -type d | xargs -r rm -r
	# Set version in technique editor files so use correctly browser cache (See https://issues.rudder.io/issues/14194)
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

build: rudder-sources virtualenv/virtualenv.py rudder-doc jetty rudder.war endpoint.war
	python virtualenv/virtualenv.py ncf-api-virtualenv
	ncf-api-virtualenv/bin/pip install -r rudder-sources/ncf/api/requirements.txt
	for i in easy_install python pip; do rm -f ncf-api-virtualenv/bin/$${i}*; done
	touch $@

# install into DESTDIR
install: build
	mkdir -p $(DESTDIR)/opt/rudder/etc/
	mkdir -p $(DESTDIR)/opt/rudder/etc/plugins/
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
	mkdir -p $(DESTDIR)/var/rudder/inventories/received
	mkdir -p $(DESTDIR)/var/rudder/inventories/failed
	mkdir -p $(DESTDIR)/var/rudder/configuration-repository/ncf/ncf-hooks.d
	mkdir -p $(DESTDIR)/var/log/rudder/apache2/
	mkdir -p $(DESTDIR)/var/log/rudder/webapp
	mkdir -p $(DESTDIR)/var/rudder/run
	mkdir -p $(DESTDIR)/etc/$(APACHE_VHOSTDIR)/
	mkdir -p $(DESTDIR)/etc/$(APACHE_CONFDIR)/
	mkdir -p $(DESTDIR)/etc/sysconfig/
	mkdir -p $(DESTDIR)/etc/default
	mkdir -p $(DESTDIR)/usr/share/doc/rudder
	mkdir -p $(DESTDIR)/usr/share/
	mkdir -p $(DESTDIR)/usr/bin/
	mkdir -p $(DESTDIR)/usr/share/ncf-api-virtualenv/share/selinux/
	mkdir -p $(DESTDIR)/var/lib/ncf-api-venv/
	mkdir -p $(DESTDIR)/opt/rudder/share/package-scripts/
	mkdir -p $(DESTDIR)/usr/lib/systemd/system/

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
	install -m 644 rudder-sources/ldap-inventory/inventory-provisioning-web/src/main/resources/configuration.properties.sample $(DESTDIR)/opt/rudder/etc/inventory-web.properties
	install -m 644 rudder-sources/rudder/rudder-web/src/main/resources/logback.xml $(DESTDIR)/opt/rudder/etc/
	cp -r rudder-sources/rudder-techniques/techniques/ $(DESTDIR)/opt/rudder/share/
	
	cp -r rudder-sources/ncf/ $(DESTDIR)/usr/share/
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
	
	install -m 755 rudder-upgrade $(DESTDIR)/opt/rudder/bin/
	
	install -m 644 rudder-webapp $(DESTDIR)/opt/rudder/etc/server-roles.d/
	install -m 644 rudder-web $(DESTDIR)/opt/rudder/etc/server-roles.d/
	install -m 640 rudder-passwords.conf $(DESTDIR)/opt/rudder/etc/
	
	install -m 755 post.write_technique.10_commit.sh $(DESTDIR)/var/rudder/configuration-repository/ncf/ncf-hooks.d/
	install -m 755 post.write_technique.50_rudderify.sh $(DESTDIR)/var/rudder/configuration-repository/ncf/ncf-hooks.d/
	# Add rudder-metrics-reporting
	install -m 755 rudder-metrics-reporting $(DESTDIR)/opt/rudder/bin/
	install -m 644 ca-bundle.crt $(DESTDIR)/opt/rudder/share/certificates/
	
	# Install documentation
	cp -rf rudder-doc/html $(DESTDIR)/usr/share/doc/rudder
	
	# Install rudder keys
	install -m 755 rudder-keys $(DESTDIR)/opt/rudder/bin/
	
	# Install rudder fix repository permissions script
	install -m 755 rudder-fix-repository-permissions $(DESTDIR)/opt/rudder/bin/
	
	# Install gitignore file for our git repo
	install -m 644 configuration-repository-gitignore $(DESTDIR)/var/rudder/configuration-repository/.gitignore
	
	install -m 644 endpoint.war $(DESTDIR)/opt/rudder/share/webapps/
	install -m 755 rudder-inventory-endpoint-upgrade $(DESTDIR)/opt/rudder/bin/
	
	install -m 644 rudder-inventory-endpoint $(DESTDIR)/opt/rudder/etc/server-roles.d/
	
	install -m 644 endpoint.xml $(DESTDIR)/opt/rudder/share/webapps/
	
	cp -a jetty $(DESTDIR)/opt/rudder
	cp -a rudder-jetty-base $(DESTDIR)/opt/rudder/etc
	
	# Init script
	install -m 755 jetty/bin/$(JETTY_SCRIPT) $(DESTDIR)/opt/rudder/bin/rudder-jetty.sh
	install -m 644 rudder-jetty.default $(DESTDIR)/etc/default/rudder-jetty
	install -m 644 rudder-jetty.conf $(DESTDIR)/opt/rudder/etc/
	install -m 644 rudder-jetty $(DESTDIR)/opt/rudder/etc/server-roles.d/

	install -m 755 rudder-webapp-postinst $(DESTDIR)/opt/rudder/share/package-scripts/
	install -m 644 rudder-jetty.service $(DESTDIR)/usr/lib/systemd/system/

	touch $@

clean: localclean
localclean:
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

distclean: veryclean
veryclean: clean
	rm -f rudder-sources.tar.bz2
	rm -rf maven.tgz
	rm -f virtualenv.tgz
	rm -rf $(TMP_DIR)

.PHONY: clean localclean localdepends veryclean distclean
