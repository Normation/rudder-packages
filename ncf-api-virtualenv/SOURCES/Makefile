#####################################################################################
# Copyright 2014 Normation SAS
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
VIRTUALENV_RELEASE = 12.0.7

WGET := $(if $(PROXY), http_proxy=$(PROXY) ftp_proxy=$(PROXY)) /usr/bin/wget -q

localdepends: ./rudder-sources ./virtualenv/virtualenv.py ./virtualenv-1.10.1/virtualenv.py
	# N/A

./rudder-sources.tar.bz2:
	$(WGET) -O rudder-sources.tar.bz2 http://www.rudder-project.org/archives/rudder-sources-${RUDDER_VERSION_TO_PACKAGE}.tar.bz2

./rudder-sources: ./rudder-sources.tar.bz2
	tar -xjf rudder-sources.tar.bz2
	mv rudder-sources-*/ rudder-sources/

./virtualenv.tgz: /usr/bin/wget
	# Original URL: https://pypi.python.org/packages/source/v/virtualenv/virtualenv-12.0.7.tar.gz
	$(WGET) -O virtualenv.tgz http://www.normation.com/tarball/virtualenv/virtualenv-$(VIRTUALENV_RELEASE).tar.gz

./virtualenv/virtualenv.py: ./virtualenv.tgz
	tar -xzf ./virtualenv.tgz
	mv ./virtualenv-$(VIRTUALENV_RELEASE)/ virtualenv/

./virtualenv-1.10.1.tgz: /usr/bin/wget
	# Original URL: https://pypi.python.org/packages/source/v/virtualenv/virtualenv-1.10.1.tar.gz
	$(WGET) -O virtualenv-1.10.1.tgz http://www.normation.com/tarball/virtualenv/virtualenv-1.10.1.tar.gz

./virtualenv-1.10.1/virtualenv.py: ./virtualenv-1.10.1.tgz
	tar -xzf ./virtualenv-1.10.1.tgz

localclean:
	rm -rf rudder-sources
	rm -rf virtualenv/
	rm -rf virtualenv-1.10.1/
	rm -rf ncf-api-virtualenv

veryclean:
	rm -f virtualenv.tgz
	rm -f virtualenv-1.10.1.tgz
	rm -f rudder-sources.tar.bz2

clean: localclean veryclean

.PHONY: localclean localdepends clean veryclean
