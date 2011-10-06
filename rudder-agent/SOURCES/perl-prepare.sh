#!/bin/bash
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

# A script to prepare a installation of Perl + FusionInventory Agent for
# Unix/Linux
# This in order to be able to provide an installation for system without
# Perl >= 5.8

set -e

if [ ! -f 'perl-prepare.sh' ]; then
    cd SOURCES
    if [ ! -f 'perl-prepare.sh' ]; then
        echo "Please run the script in the root directory"
        exit 1
    fi
fi

ROOT="$PWD/.."
MAKE="make"
TMP="$PWD/tmp"
FILEDIR="$PWD/files"
#PERL_PREFIX="$TMP/perl"
PERL_PREFIX="/opt/rudder"
BUILDDIR="$TMP/build"
BASETARBALLSDIR="$PWD/base-tarballs"
# MODULES="XML::NamespaceSupport Class::Inspector Digest::MD5 Net::IP File::ShareDir File::Copy::Recursive Net::IP Proc::Daemon Proc::PID::File Digest::MD5 File::Copy File::Path File::Temp Net::NBName Parallel::ForkManager XML::SAX XML::Simple UNIVERSAL::require"
MODULES="Digest::MD5 Net::IP XML::SAX XML::Simple UNIVERSAL::require"
FINALDIR=$PWD
NO_CLEANUP=0
OLD_PATH=$PATH
NO_PERL_REBUILD=0

buildDmidecode () {
    cd $TMP
    gunzip < $FILEDIR/dmidecode-$DMIDECODE_VERSION.tar.gz | tar xvf -
    cd dmidecode-$DMIDECODE_VERSION
    $MAKE
    cp dmidecode $PERL_PREFIX/bin
    cd $TMP
}


installMod () {
    modName=$1
    distName=$2
    args=$3

    if [ -z "$distName" ]; then
        distName=`echo $modName|sed 's,::,-,g'`
    fi
    archive=`ls $FILEDIR/$distName*.tar.gz`
    $TMP/perl$PERL_PREFIX/bin/perl $CPANM -l $TMP/perl$PERL_PREFIX --skip-installed $archive $args
    $TMP/perl$PERL_PREFIX/bin/perl -I $TMP/perl$PERL_PREFIX/lib/perl5 -M$modName -e1
}

cleanUp () {
    rm -rf $BUILDDIR $TMP/openssl $TMP/perl $TMP/Compress::Zlib

}

buildPerl () {

    cd $TMP
    if [ ! -f $FILEDIR/perl-$PERLVERSION.tar.gz ]; then
    echo $FILEDIR/perl-$PERLVERSION.tar.gz
        echo "I did not find the perl sources directory. It either means something failed during the download, or you are trying something funny."
        exit 1
    fi

    cd $BUILDDIR
    gunzip < $FILEDIR/perl-$PERLVERSION.tar.gz | tar xvf -
    cd perl-$PERLVERSION
    
    ./Configure -Dnoextensions=ODBM_File -Duserelocatableinc -Dusethreads -des -Dcc="gcc" -Dinstallprefix=$PERL_PREFIX -Dsiteprefix=$PERL_PREFIX -Dprefix=$PERL_PREFIX
    $MAKE
    $MAKE install DESTDIR=$TMP/perl

}

PERLVERSION="5.12.1"

# Clean up
if [ "$NO_CLEANUP" = "0" ]; then
    cleanUp
fi

[ -d $TMP ] || mkdir $TMP
[ -d $BUILDDIR ] || mkdir $BUILDDIR

if [ ! -d $BUILDDIR ]; then
  echo "$BUILDDIR dir is missing"
fi

if [ "$NO_PERL_REBUILD" = "0" ]; then
    buildPerl
fi

cd $BUILDDIR
gunzip < $FILEDIR/Crypt-SSLeay-0.57.tar.gz | tar xvf -
cd Crypt-SSLeay-0.57
PERL_MM_USE_DEFAULT=1 $TMP/perl$PERL_PREFIX/bin/perl Makefile.PL --default INSTALL_BASE=$TMP/perl$PERL_PREFIX
$MAKE install

cd $BUILDDIR
echo $PWD
archive=`ls $FILEDIR/App-cpanminus-*.tar.gz`
echo $archive
gunzip < $archive | tar xvf -
CPANM=$BUILDDIR/App-cpanminus-1.0004/bin/cpanm

installMod "URI"
installMod "HTML::Tagset"
installMod "HTML::Parser"
installMod "LWP" "libwww-perl"
installMod "Compress::Zlib" "IO-Compress"

# Tree dependencies not pulled by cpanm
for modName in $MODULES; do
    installMod $modName
done

cd $PWD/../../fusioninventory-agent
mkdir -p $TMP/perl$PERL_PREFIX/share/fusion-utils && cp -a share/* $TMP/perl$PERL_PREFIX/share/fusion-utils
PERL_MM_USE_DEFAULT=1 $TMP/perl$PERL_PREFIX/bin/perl Makefile.PL --default INSTALL_BASE=$TMP/perl$PERL_PREFIX
$MAKE install

#Restoring PATH
PATH=$OLD_PATH

cd $TMP
mv perl $FINALDIR/perl-custom
