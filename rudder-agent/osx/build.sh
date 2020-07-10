#!/bin/bash

set -xe

# TODO package for homebrew
# TODO setup launchd service

# VM hosting: hostmyapple.com

base=$(pwd)
mkdir tmp 

cd ../SOURCES
# use gnu or system tools as possible (todo do not depend on it since we don't have dependencies management)
# on OSX 10.15.1
# - curl 7.64.1
# - openssl = libressl
# - no jq, no lmdb, no yaml, no pcre
build_env="USE_HTTPS=true USE_SYSTEM_OPENSSL=false USE_SYSTEM_FUSION=false USE_SYSTEM_PERL=true USE_SYSTEMD=false USE_SYSTEM_CURL=true USE_SYSTEM_JQ=false USE_SYSTEM_YAML=false USE_SYSTEM_XML=true USE_PIE=yes USE_SYSTEM_LMDB=false USE_ACL=false USE_SYSTEM_PCRE=false"

./configure --with-openssl --with-jq --with-libyaml --with-lmdb --with-pcre

make build ${build_env}

make install ${build_env} DESTDIR="${base}/tmp"

cd "${base}"

# on osx we cannot install the rudder command to/usr/bin
mkdir tmp/usr/local
mv tmp/usr/bin tmp/usr/local/

# package for native installer
# Doc: 
# https://stackoverflow.com/questions/11487596/making-macos-installer-packages-which-are-developer-id-ready/11487658#11487658
# https://ilostmynotes.blogspot.com/2012/06/mac-os-x-pkg-bom-files-package.html
# http://s.sudre.free.fr/Stuff/Ivanhoe/FLAT.html
# https://matthew-brett.github.io/docosx/flat_packages.html
pkgbuild --root "${base}/tmp" --scripts scripts --identifier com.normation.rudder-agent.pkg rudder-agent.pkg

# install with: installer -pkg my_package.pkg -target /
# There is no simple way to uninstall the package
# https://stackoverflow.com/questions/25925752/uninstall-packages-in-mac-os-x


# TODO package for homebrew (needs brew to install but uninstall is easy)
