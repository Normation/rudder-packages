#!/bin/sh

set -ex

if [ -z "$1" ]
then
  echo "Usage $0 <version> [<architecture>]"
  echo " ex: $0 3.0.6"
  exit 1
fi

version="$1"
if [ -n "$2" ]; then
  arch="$2"
else
  arch=i386
fi

LC_ALL=C
export LC_ALL
ROOTPATH=`pwd`
SOURCES="`dirname ${ROOTPATH}`/SOURCES"
BUILDROOT="${ROOTPATH}/tmp"
PKGROOT="${BUILDROOT}/rudder-agent"
rm -rf ${BUILDROOT}
mkdir ${BUILDROOT}

# Build rudder agent and install to a temporary destination
cd ${SOURCES}
# not needed
#gmake RUDDER_VERSION_TO_PACKAGE=${version}
gmake install DESTDIR=${PKGROOT} RUDDER_VERSION_TO_PACKAGE=${version}

cd ${BUILDROOT}
# Create prototype file that contains included files list
find rudder-agent | grep -v '^rudder-agent$' | pkgproto | sed 's/ rudder-agent/ /' > Prototype.tmp
cat - Prototype.tmp >Prototype <<EOF
i pkginfo
i postinstall
i postremove
i preremove
EOF
rm Prototype.tmp

# Create package information file
date=`date '+%m%d%Y'`
eval "cat - << EOF
`cat ${ROOTPATH}/pkginfo`
EOF
" >> ${BUILDROOT}/pkginfo

# Retreive postinst et al scripts
cp ${ROOTPATH}/postinstall ${BUILDROOT}/
cp ${ROOTPATH}/postremove ${BUILDROOT}/
cp ${ROOTPATH}/preremove ${BUILDROOT}/

# Create the package content description file
pkgmk -o -r ${PKGROOT} -d ${BUILDROOT} -f Prototype

# create the final package file
cd ${BUILDROOT}
# avoid tar warning (bug in the build system ?)
touch RudderAgent/root/opt/rudder/lib/perl5/Test/Deep.pm
tar -cf - RudderAgent | gzip -9 -c > RudderAgent.${version}.${arch}.pkg.tar.gz
mv RudderAgent.${version}.${arch}.pkg.tar.gz ${ROOTPATH}

