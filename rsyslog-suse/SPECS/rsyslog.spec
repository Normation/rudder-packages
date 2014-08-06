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

#
# spec file for package rsyslog (Version 4.8.0)
#
# Copyright (c) 2008 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# norootforbuild


Name:           rsyslog
%define         upstream_version 4.8.0
%define         rsyslog_docdir %{_docdir}/%{name}
%define         install_all_modules_in_lib 0
Version:        4.8.0
Release:        1.0
License:        GPL v3 or later
Group:          System/Daemons
Summary:        Rsyslog, the enhanced syslogd for Linux and Unix
Url:            http://www.rsyslog.com/
#Source0:        http://download.rsyslog.com/rsyslog/%{name}-%{upstream_version}.tar.gz
Source0:        %{name}-%{upstream_version}.tar.bz2
Source1:        rsyslog.sysconfig
Source2:        rsyslog.conf.in
Source3:        rsyslog.early.conf.in
Source4:        rsyslog.d.remote.conf.in
AutoReqProv:    on
PreReq:         %insserv_prereq %fillup_prereq /sbin/klogd /etc/init.d/syslog /sbin/checkproc
Provides:       syslog
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  klogd
BuildRequires:  dos2unix openssl-devel pcre-devel pkgconfig zlib-devel
#BuildRequires:  krb5-devel mysql-devel net-snmp-devel postgresql-devel
BuildRequires:  krb5-devel postgresql-devel
%define         _sbindir /sbin
%define         _libdir /%_lib
%define         rsyslogdocdir %{_docdir}/%{name}
%define         additional_sockets %{_localstatedir}/run/rsyslog/additional-log-sockets.conf

%description
Rsyslog is an enhanced multi-threaded syslogd supporting, among others,
MySQL, syslog/tcp, RFC 3195, permitted sender lists, filtering on any
message part, and fine grain output format control. It is quite
compatible to stock sysklogd and can be used as a drop-in replacement.
Its advanced features make it suitable for enterprise-class, encryption
protected syslog relay chains while at the same time being very easy to
setup for the novice user.



Authors:
--------
    Rainer Gerhards <rgerhards@adiscon.com>, Adiscon GmbH
    Michael Meckelein <mmeckelein@hq.adiscon.com>, Adiscon GmbH

%package doc
License:        GPL v3 or later
Group:          System/Daemons
Requires:       %{name} = %{version}
Summary:        Additional documentation for rsyslog

%description doc
Rsyslog is an enhanced multi-threaded syslog daemon. See rsyslog
package.

This package provides additional documentation for rsyslog.



Authors:
--------
    Rainer Gerhards <rgerhards@adiscon.com>, Adiscon GmbH
    Michael Meckelein <mmeckelein@hq.adiscon.com>, Adiscon GmbH

%package module-gssapi
License:        GPL v3 or later
Group:          System/Daemons
Requires:       %{name} = %{version}
Summary:        GSS-API support module for rsyslog

%description module-gssapi
Rsyslog is an enhanced multi-threaded syslog daemon. See rsyslog
package.

This module provides the support to receive syslog messages from the
network protected via Kerberos 5 encryption and authentication.



Authors:
--------
    Rainer Gerhards <rgerhards@adiscon.com>, Adiscon GmbH
    Michael Meckelein <mmeckelein@hq.adiscon.com>, Adiscon GmbH

%package module-pgsql
License:        GPL v3 or later
Group:          System/Daemons
Requires:       %{name} = %{version}
Summary:        PostgreSQL support module for rsyslog

%description module-pgsql
Rsyslog is an enhanced multi-threaded syslog daemon. See rsyslog
package.

This module provides the support for logging into PostgreSQL databases.



Authors:
--------
    Rainer Gerhards <rgerhards@adiscon.com>, Adiscon GmbH
    Michael Meckelein <mmeckelein@hq.adiscon.com>, Adiscon GmbH

%prep
%setup -q -n %{name}-%{upstream_version}
dos2unix doc/*.html

%build
export CFLAGS="$RPM_OPT_FLAGS -fno-strict-aliasing -W -Wall"
%if 0%{?suse_version} > 1000 && 0%{?suse_version} < 1030
    export CFLAGS="$CFLAGS -fstack-protector"
%endif
autoreconf -fi
%configure			\
%if ! 0%{install_all_modules_in_lib}
  --with-moddirs=%{_prefix}%{_libdir}/rsyslog/ \
%endif
  --enable-largefile	\
  --enable-pthreads	\
  --enable-regexp		\
  --enable-zlib		\
  --enable-klog		\
  --enable-inet		\
  --enable-rsyslogd	\
  --enable-gssapi-krb5	\
  --enable-pgsql		\
  --enable-mail		\
  --enable-imfile		\
  --enable-imtemplate	\
  --enable-imptcp		\
  --disable-static
#
#optional (disabled by MCE)
        # --enable-openssl      \
        # --enable-mysql        \
        # --enable-snmp
#
#
#optional (need additional libs):
#	--enable-rfc3195	\
#	--enable-relp		\
#	--enable-libdbi		\
#
#for debugging only:
#	--enable-rtinst		\
#	--enable-debug		\
#	--enable-valgrind	\
#
make %{?_smp_mflags:%{_smp_mflags}}

%install
make install DESTDIR="%{buildroot}"
#
rm -f %{buildroot}%{_libdir}/rsyslog/*.la
#
%if ! 0%{install_all_modules_in_lib}
# move all modules linking libraries in /usr to /usr/%_lib
# the user has to specify them with full path then...
install -d -m0755 %{buildroot}%{_prefix}%{_libdir}/rsyslog
# for mod in omgssapi.so imgssapi.so lmgssutil.so ommysql.so ompgsql.so omsnmp.so ; do
for mod in omgssapi.so imgssapi.so lmgssutil.so ompgsql.so ; do
  mv -f %{buildroot}%{_libdir}/rsyslog/$mod \
        %{buildroot}%{_prefix}%{_libdir}/rsyslog/
done
%endif
#
install -d -m0755 %{buildroot}%{_sysconfdir}/rsyslog.d
install -d -m0755 %{buildroot}%{_localstatedir}/run/rsyslog
install -d -m0755 %{buildroot}%{_localstatedir}/spool/rsyslog
for file in rsyslog.conf rsyslog.early.conf rsyslog.d.remote.conf ; do
  sed \
%ifarch s390 s390x
  -e 's;tty10;console;g' \
%endif
  -e 's;ADDITIONAL_SOCKETS;%{additional_sockets};g' \
  -e 's;ETC_RSYSLOG_D_GLOB;%{_sysconfdir}/rsyslog.d/*.conf;g' \
  -e 's;RSYSLOG_SPOOL_DIR;%{_localstatedir}/spool/rsyslog;g' \
  %{_sourcedir}/${file}.in > ${file}.$$
done
install    -m0600 rsyslog.conf.$$ \
                  %{buildroot}%{_sysconfdir}/rsyslog.conf
install    -m0600 rsyslog.early.conf.$$ \
                  %{buildroot}%{_sysconfdir}/rsyslog.early.conf
install    -m0600 rsyslog.d.remote.conf.$$ \
                  %{buildroot}%{_sysconfdir}/rsyslog.d/remote.conf
#
install -d -m0755 %{buildroot}/var/adm/fillup-templates
install    -m0600 %{_sourcedir}/rsyslog.sysconfig \
                  %{buildroot}/var/adm/fillup-templates/sysconfig.syslog-rsyslog
#
rm -f doc/Makefile*
install -d -m0755 %{buildroot}%{rsyslogdocdir}/
find ChangeLog README AUTHORS COPYING COPYING.LESSER rsyslog.conf doc \
  \( -type d -exec install -m755 -d   %{buildroot}%{rsyslogdocdir}/\{\} \; \) \
     -o \( -type f -exec install -m644 \{\} %{buildroot}%{rsyslogdocdir}/\{\} \; \)
install -m644 plugins/ompgsql/createDB.sql \
  %{buildroot}%{rsyslogdocdir}/pgsql-createDB.sql
#

%clean
if [ -n "%{buildroot}" ] && [ "%{buildroot}" != "/" ] ; then
  rm -rf "%{buildroot}"
fi

%post
#
# update linker caches
#
/sbin/ldconfig
#
# add syslog variables provided by klogd if needed
#
%{fillup_and_insserv -ny syslog syslog}
%{fillup_and_insserv -nY syslog earlysyslog}
#
# add RSYSLOGD_* variables if needed
#
%{fillup_only -ns syslog rsyslog}
#
# check if daemon configured in SYSLOG_DAEMON is installed
# and switch to ourself if it's missed
#
source etc/sysconfig/syslog
# Normation tweak : We WANT rsyslog to replace the default logger !
replace_syslog=yes
if test "$SYSLOG_DAEMON" != "rsyslogd" ; then
    if test -z "$SYSLOG_DAEMON" || \
       test ! -x sbin/${SYSLOG_DAEMON} ; then
        replace_syslog=yes
    fi
fi
if test "$replace_syslog" = "yes" ; then
    sed -i -e 's/^SYSLOG_DAEMON=.*/SYSLOG_DAEMON="rsyslogd"/g' \
              etc/sysconfig/syslog
fi
#
# create dirs, touch log default files
#
mkdir -p var/log
touch var/log/messages;  chmod 640 var/log/messages
touch var/log/boot.log;  chmod 640 var/log/boot.log
touch var/log/mail;      chmod 640 var/log/mail
touch var/log/mail.info; chmod 640 var/log/mail.info
touch var/log/mail.warn; chmod 640 var/log/mail.warn
touch var/log/mail.err;  chmod 640 var/log/mail.err
test -f var/log/news && mv -f var/log/news var/log/news.bak
mkdir -p -m 0750 var/log/news
chown news:news  var/log/news
touch var/log/news/news.crit;   chmod 640 var/log/news/news.crit
chown news:news var/log/news/news.crit
touch var/log/news/news.err;    chmod 640 var/log/news/news.err
chown news:news var/log/news/news.err
touch var/log/news/news.notice; chmod 640 var/log/news/news.notice
chown news:news var/log/news/news.notice
#
# touch the additional log files we are using
#
touch var/log/acpid;            chmod 640 var/log/acpid
touch var/log/firewall;         chmod 640 var/log/firewall
touch var/log/NetworkManager;   chmod 640 var/log/NetworkManager
#
# touch the additional log sockets config file
#
additional_sockets="%{additional_sockets}"
touch "${additional_sockets#/}"; chmod 640 "${additional_sockets#/}"
#
# Restart syslog
#
/sbin/service syslog restart

%preun
#
# stop the rsyslogd daemon when it is running
#
%{stop_on_removal syslog}

%postun
#
# update linker caches
#
/sbin/ldconfig
#
# reset SYSLOG_DAEMON variable
#
if test -f etc/sysconfig/syslog ; then
  source etc/sysconfig/syslog
  if test "$SYSLOG_DAEMON" == "rsyslogd" ; then
    sed -i -e 's/^SYSLOG_DAEMON=.*/SYSLOG_DAEMON=""/g' \
              etc/sysconfig/syslog
  fi
fi
#
# stop the rsyslogd daemon when it is running
#
%{restart_on_update syslog}
#
# cleanup init scripts
#
%{insserv_cleanup}

%files
%defattr(-,root,root)
%dir %{_sysconfdir}/rsyslog.d
%config(noreplace) %attr(600,root,root) %{_sysconfdir}/rsyslog.conf
%config(noreplace) %attr(600,root,root) %{_sysconfdir}/rsyslog.early.conf
%config(noreplace) %attr(600,root,root) %{_sysconfdir}/rsyslog.d/remote.conf
%{_sbindir}/rsyslogd
%dir %{_libdir}/rsyslog
%{_libdir}/rsyslog/imfile.so
%{_libdir}/rsyslog/imklog.so
%{_libdir}/rsyslog/immark.so
%{_libdir}/rsyslog/imtcp.so
%{_libdir}/rsyslog/imtemplate.so
%{_libdir}/rsyslog/imudp.so
%{_libdir}/rsyslog/imuxsock.so
%{_libdir}/rsyslog/lmnet.so
%{_libdir}/rsyslog/lmregexp.so
%{_libdir}/rsyslog/lmtcpclt.so
%{_libdir}/rsyslog/lmtcpsrv.so
%{_libdir}/rsyslog/ommail.so
%{_libdir}/rsyslog/omtesting.so
%{_libdir}/rsyslog/imptcp.so
%{_libdir}/rsyslog/lmnetstrms.so
%{_libdir}/rsyslog/lmnsd_ptcp.so
%{_libdir}/rsyslog/lmstrmsrv.so
%{_libdir}/rsyslog/lmzlibw.so
%if ! 0%{install_all_modules_in_lib}
%dir %{_prefix}%{_libdir}/rsyslog
%endif
%{_mandir}/man5/rsyslog.conf.5*
%{_mandir}/man8/rsyslogd.8*
%dir %{rsyslogdocdir}
%doc %{rsyslogdocdir}/rsyslog.conf
%doc %{rsyslogdocdir}/ChangeLog
%doc %{rsyslogdocdir}/README
%doc %{rsyslogdocdir}/AUTHORS
%doc %{rsyslogdocdir}/COPYING
%doc %{rsyslogdocdir}/COPYING.LESSER
%dir %{_localstatedir}/run/rsyslog
%dir %{_localstatedir}/spool/rsyslog
/var/adm/fillup-templates/sysconfig.syslog-rsyslog

%files doc
%defattr(-,root,root)
%dir %{rsyslogdocdir}
%doc %{rsyslogdocdir}/doc

%files module-gssapi
%defattr(-,root,root)
%if 0%{install_all_modules_in_lib}
%dir %{_libdir}/rsyslog
%{_libdir}/rsyslog/omgssapi.so
%{_libdir}/rsyslog/imgssapi.so
%{_libdir}/rsyslog/lmgssutil.so
%else
%dir %{_prefix}%{_libdir}/rsyslog
%{_prefix}%{_libdir}/rsyslog/omgssapi.so
%{_prefix}%{_libdir}/rsyslog/imgssapi.so
%{_prefix}%{_libdir}/rsyslog/lmgssutil.so
%endif

%files module-pgsql
%defattr(-,root,root)
%doc %{rsyslogdocdir}/pgsql-createDB.sql
%if 0%{install_all_modules_in_lib}
%dir %{_libdir}/rsyslog
%{_libdir}/rsyslog/ompgsql.so
%else
%dir %{_prefix}%{_libdir}/rsyslog
%{_prefix}%{_libdir}/rsyslog/ompgsql.so
%endif

%changelog
* Fri Sep 16 2011 matthieu.cerda@normation.com
- Updated upstream version to 4.8.0 and stripped unused parts.
* Mon Dec 15 2008 mt@suse.de
- Security fix to honor $AllowedSender settings (bnc#457273).
- Security fix [DoS] from 3.20.2 to emit a discard message every
  minute only (when DisallowWarning enabled) instead of every time;
  this prevernts an attacker can fill the disk (bnc#457273).
* Wed Sep 10 2008 schwab@suse.de
- Run autoreconf.
* Tue Sep  9 2008 mt@suse.de
- Enabled mail, imfile and imtemplate modules
- Enabled snmp module, packaged as rsyslog-module-snmp
- Added patch to support multiple module directories,
  in our case /lib[64]/rsyslog:/usr/lib[64]/rsyslog
* Thu Sep  4 2008 mt@suse.de
- initial rsyslog 3.18.3 package
