%define debhelper_ver 7.3.12

Summary:        Tools for Debian Packages
Name:           deb
Version:        1.15.0
Release:        1%{?dist}

License:        GPLv2+
URL:            http://www.debian.org
Group:          System Environment/Base
Source:         dpkg_%{version}.tar.bz2
Source1:        debhelper_%{debhelper_ver}.tar.bz2
Patch0:         debhelper-no-localized-manpages.diff
BuildRoot:      %{_tmppath}/%{name}-%{version}-build

AutoReqProv:    off

BuildRequires:  ncurses-devel
BuildRequires:  texlive-latex
BuildRequires:  chkconfig
BuildRequires:  zlib-devel
BuildRequires:  libselinux-devel
BuildRequires:  libsepol-devel
BuildRequires:  recode

Requires(pre):  /bin/touch

Requires:       perl
Requires:       cpio
Requires:       patch
Requires:       make
Requires:       html2text
Requires:       chkconfig

Provides:       dpkg = %{version}
Provides:       dpkg-devel = %{version}
Provides:       debhelper = %{debhelper_ver}
Provides:       dselect = %{version}
Provides:       dpkg-doc = %{version}


%description
This package contains tools for working with Debian packages. It makes
it possible to create and extract Debian packages. If Alien is
installed, the packages can be converted to RPMs.

This package contains the following Debian packages: dpkg, dselect,
dpkg-doc, dpkg-dev, and debhelper.


%prep
%setup -q -n dpkg-%{version} -b 1
cd ..
%patch0
cd -
# update arch table
sed -n '/linux-gnu/ s/linux-gnu/suse-linux/p' debian/archtable > debian/archtable.tmp
cat debian/archtable.tmp >> debian/archtable
rm debian/archtable.tmp


%build
export SELINUX_LIBS="-lselinux"
%configure\
    --with-selinux \
    --localstatedir=%{_localstatedir}/lib\
    --libdir=%{_libdir}

# configure somehow does not detect architecture correctly in OBS (bnc#469337), so 
# let's do an awful hack and fix it in config.h
%ifarch x86_64
sed -i 's/^#define ARCHITECTURE ""/#define ARCHITECTURE "amd64"/' config.h
%endif
%ifarch %ix86
sed -i 's/^#define ARCHITECTURE ""/#define ARCHITECTURE "i386"/' config.h
%endif
%ifarch ppc powerpc
sed -i 's/^#define ARCHITECTURE ""/#define ARCHITECTURE "powerpc"/' config.h
%endif
%ifarch ppc64 powerpc64
sed -i 's/^#define ARCHITECTURE ""/#define ARCHITECTURE "ppc64"/' config.h
%endif

make %{?_smp_mflags}
# This makes debhelper man pages
cd ../debhelper
make VERSION='%{debhelper_ver}'


%install
##
# dpkg stuff
##
make DESTDIR=%{buildroot} install
# locales
%{find_lang} dpkg
%{find_lang} dselect
%{find_lang} dpkg-dev
cat dpkg.lang dselect.lang dpkg-dev.lang > %{name}.lang
# docs
install -d -m 755 %{buildroot}/%{_docdir}/deb/dpkg
install -m 644 ABOUT-NLS %{buildroot}/%{_docdir}/deb/dpkg
install -m 644 AUTHORS %{buildroot}/%{_docdir}/deb/dpkg
install -m 644 COPYING %{buildroot}/%{_docdir}/deb/dpkg
install -m 644 doc/triggers.txt %{buildroot}/%{_docdir}/deb/dpkg
install -m 644 INSTALL %{buildroot}/%{_docdir}/deb/dpkg
install -m 644 NEWS %{buildroot}/%{_docdir}/deb/dpkg
install -m 644 README* %{buildroot}/%{_docdir}/deb/dpkg
install -m 644 THANKS %{buildroot}/%{_docdir}/deb/dpkg
install -m 644 TODO %{buildroot}/%{_docdir}/deb/dpkg
install -m 644 debian/changelog %{buildroot}/%{_docdir}/deb/dpkg
##
# debhelper stuff
##
cd ../debhelper
# autoscripts
install -d -m 755 %{buildroot}%{_datadir}/debhelper/autoscripts
install -m 644 autoscripts/* %{buildroot}%{_datadir}/debhelper/autoscripts
# perl modules:
install -d -m 755 %{buildroot}%{perl_vendorarch}/Debian/Debhelper
install -d -m 755 %{buildroot}%{perl_vendorarch}/Debian/Debhelper/Sequence
install -m 644 Debian/Debhelper/Sequence/*.pm %{buildroot}%{perl_vendorarch}/Debian/Debhelper/Sequence
install -m 644 Debian/Debhelper/*.pm %{buildroot}%{perl_vendorarch}/Debian/Debhelper
# docs:
install -d -m 755 %{buildroot}%{_docdir}/deb/debhelper/examples
install -m 644 examples/* %{buildroot}%{_docdir}/deb/debhelper/examples
install -m 644 doc/* %{buildroot}%{_docdir}/deb/debhelper
install -m 644 debian/{changelog,copyright} %{buildroot}%{_docdir}/deb/debhelper
# man pages:
install -d -m 755 %{buildroot}%{_mandir}/man1
install -d -m 755 %{buildroot}%{_mandir}/man7
install -m 644 *.1 %{buildroot}%{_mandir}/man1
install -m 644 debhelper.7 %{buildroot}%{_mandir}/man7
# binaries:
install -d -m 755 %{buildroot}%{_bindir}
install -m 755 dh_*[^1-9] %{buildroot}%{_bindir}
##
# remove update-alternatives stuff (included in separate package)
##
rm -rf %{buildroot}%{_sysconfdir}/alternatives
rm -rf %{buildroot}%{_localstatedir}/lib/dpkg/alternatives
rm -rf %{buildroot}%{_bindir}/update-alternatives
rm -rf %{buildroot}%{_sbindir}/update-alternatives
rm -rf %{buildroot}%{_mandir}/man8/update-alternatives.8
rm -rf %{buildroot}%{_mandir}/*/man8/update-alternatives.8
##
# remove duplicate files
##

find %{buildroot}%{_mandir} -type f | xargs recode -f ..utf8

mv %{buildroot}%{_docdir}/deb %{buildroot}%{_docdir}/deb-%{version}
mv  %{buildroot}%{_datadir}/perl5/* %{buildroot}%{_libdir}/perl5
rmdir %{buildroot}%{_datadir}/perl5

%find_lang dpkg
%find_lang dselect
%find_lang dpkg-dev

cat dpkg.lang dselect.lang dpkg-dev.lang > deb.lang


%clean
rm -rf %{buildroot}


%post
cd %{_localstatedir}/lib/dpkg
for f in diversions statoverride status ; do
    [ ! -f $f ] && touch $f
done
exit 0


%files -f %{name}.lang
%defattr(-,root,root)
%doc %{_docdir}/deb-%{version}
%doc %{_mandir}/fr
%doc %{_mandir}/ja
%doc %{_mandir}/sv
%doc %{_mandir}/es
%doc %{_mandir}/pt_BR
%doc %{_mandir}/ru
%doc %{_mandir}/de
%doc %{_mandir}/pl
%doc %{_mandir}/hu
%doc %{_mandir}/man?/*
%dir %{_sysconfdir}/dpkg
%config(noreplace) %{_sysconfdir}/dpkg/*
%{_bindir}/*
%{_sbindir}/*
%{_libdir}/dpkg
%{_datadir}/dpkg
%{_localstatedir}/lib/dpkg
%{_datadir}/debhelper
%{perl_vendorarch}/Debian
%{perl_vendorarch}/Dpkg
%{perl_vendorarch}/Dpkg.pm


%changelog
* Sat Feb 20 2010 Arkady L. Shane <ashejn@yandex-team.ru> - 1.15.0-1
- initial build for Fedora
