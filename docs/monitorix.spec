# rpm spec for Monitorix
#

Summary: Monitorix is a system monitoring tool
Name: monitorix
Version: 2.6.0
Release: 1%{?dist}
License: GPL
Group: Applications/System
URL: http://www.monitorix.org
Packager: Jordi Sanfeliu <jordi@fibranet.cat>

Source: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch

Requires: rrdtool
Requires: perl
Requires: perl-libwww-perl
Requires: perl-MailTools
Requires: perl-MIME-Lite
Requires: perl-DBI
Requires: perl-XML-Simple

%description
Monitorix is a free, open source, lightweight system monitoring tool designed
to monitor as many services and system resources as possible. It has been
created to be used under production UNIX/Linux servers, but due to its
simplicity and small size may also be used on embedded devices as well. 

%prep
%setup

%build

%install
rm -rf %{buildroot}
mkdir -p %{buildroot}%{_initrddir}
install -m 0755 docs/monitorix.init %{buildroot}%{_initrddir}/monitorix
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
install -m 0644 docs/monitorix-apache.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/monitorix.conf
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d
install -m 0644 docs/monitorix.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/monitorix
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
install -m 0644 docs/monitorix.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/monitorix
mkdir -p %{buildroot}%{_sysconfdir}
install -m 0644 monitorix.conf %{buildroot}%{_sysconfdir}/monitorix.conf
mkdir -p %{buildroot}%{_bindir}
install -m 0755 monitorix %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_datadir}/monitorix
install -m 0644 logo_top.png %{buildroot}%{_datadir}/monitorix
install -m 0644 logo_bot.png %{buildroot}%{_datadir}/monitorix
install -m 0644 monitorixico.png %{buildroot}%{_datadir}/monitorix
mkdir -p %{buildroot}%{_datadir}/monitorix/imgs
mkdir -p %{buildroot}%{_datadir}/monitorix/cgi-bin
install -m 0755 monitorix.cgi %{buildroot}%{_datadir}/monitorix/cgi-bin
mkdir -p %{buildroot}%{_localstatedir}/lib/monitorix/reports
install -m 0644 reports/*.html %{buildroot}%{_localstatedir}/lib/monitorix/reports
install -m 0755 reports/send_reports %{buildroot}%{_localstatedir}/lib/monitorix/reports
mkdir -p %{buildroot}%{_localstatedir}/lib/monitorix/usage
mkdir -p %{buildroot}%{_mandir}/man5
mkdir -p %{buildroot}%{_mandir}/man8
install -m 0644 man/man5/monitorix.conf.5 %{buildroot}%{_mandir}/man5
install -m 0644 man/man8/monitorix.8 %{buildroot}%{_mandir}/man8

%clean
rm -rf %{buildroot}

%post
/sbin/chkconfig --add monitorix

%files
%defattr(-, root, root)
%{_initrddir}/monitorix
%config(noreplace) %{_sysconfdir}/httpd/conf.d/monitorix.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/monitorix
%config(noreplace) %{_sysconfdir}/sysconfig/monitorix
%config(noreplace) %{_sysconfdir}/monitorix.conf
%{_bindir}/monitorix
%{_datadir}/monitorix/logo_top.png
%{_datadir}/monitorix/logo_bot.png
%{_datadir}/monitorix/monitorixico.png
%{_datadir}/monitorix/cgi-bin/monitorix.cgi
%attr(777,apache,apache) %{_datadir}/monitorix/imgs
%attr(755,root,root) %{_localstatedir}/lib/monitorix/usage
%config(noreplace) %{_localstatedir}/lib/monitorix/reports/*.html
%{_localstatedir}/lib/monitorix/reports/send_reports
%doc %{_mandir}/man5/monitorix.conf.5.gz
%doc %{_mandir}/man8/monitorix.8.gz
%doc Changes COPYING README README.nginx README.FreeBSD README.OpenBSD README.NetBSD docs/monitorix-alert.sh docs/monitorix-lighttpd.conf

%changelog
* Thu Sep 01 2005 Jordi Sanfeliu <jordi@fibranet.cat>
- Release 0.7.8.
- First public release.
- All changes are described in the Changes file.