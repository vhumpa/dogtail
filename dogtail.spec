Summary: GUI test tool and automation framework
Name: dogtail
Version: 0.5.1
Release: 1
License: GPL
Group: User Interface/X
URL: http://people.redhat.com/zcerza/dogtail/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArch: noarch
BuildRequires: python
Requires: pyspi >= 0.5.3
Requires: pygtk2
Requires: rpm-python
Requires: ImageMagick
Requires: Xvfb
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

%description
GUI test tool and automation framework that uses assistive technologies to 
communicate with desktop applications.

%prep
%setup -q

%build
python ./setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python ./setup.py install -O2 --root=$RPM_BUILD_ROOT --record=%{name}.files
rm -rf $RPM_BUILD_ROOT/%{_docdir}/dogtail

%post
touch --no-create %{_datadir}/icons/hicolor || :
[ -x /usr/bin/gtk-update-icon-cache ] && gtk-update-icon-cache --quiet -f %{_datadir}/icons/hicolor || :
update-desktop-database &> /dev/null || :
rm -rf %{_datadir}/doc/dogtail/

%postun
touch --no-create %{_datadir}/icons/hicolor || :
[ -x /usr/bin/gtk-update-icon-cache ] && gtk-update-icon-cache --quiet -f %{_datadir}/icons/hicolor || :
update-desktop-database &> /dev/null || :

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%{_bindir}
%{_libdir}
%{_datadir}/applications/
%{_datadir}/dogtail/
%{_datadir}/icons/hicolor/
%doc COPYING
%doc README
%doc examples/

%changelog
* Fri Feb 24 2006 Zack Cerza <zcerza@redhat.com> - 0.5.1-1
- Remove BuildRequires on at-spi-devel. Added one on python.
- Use macros instead of absolute paths.
- Touch %{_datadir}/icons/hicolor/ before running gtk-update-icon-cache.
- Require and use desktop-file-utils.
- %postun = %post.
- Shorten BuildArchitectures to BuildArch. The former worked, but even vim's 
  hilighting hated it.
- Put each *Requires on a separate line.
- Remove __os_install_post definition.

* Fri Feb 17 2006 Zack Cerza <zcerza@redhat.com> - 0.5.0-2
- It looks like xorg-x11-Xvfb changed names. Require 'Xvfb' instead.
- Remove Requires on python-elementtree, since RHEL4 didn't have it. The 
  functionality it provides is probably never used anyway, and will most likely
  be removed in the future.
- Don't run gtk-update-icon-cache if it doesn't exist.

* Fri Feb  3 2006 Zack Cerza <zcerza@redhat.com> - 0.5.0-1
- New upstream release.
- Added missing BuildRequires on at-spi-devel.
- Added Requires on pyspi >= 0.5.3.
- Added Requires on rpm-python, pygtk2, ImageMagick, xorg-x11-Xvfb, 
  python-elementtree.
- Moved documentation (including examples) to the correct place.
- Make sure /usr/share/doc/dogtail is removed.
- Added 'gtk-update-icon-cache' to %post.

* Mon Oct 24 2005 Zack Cerza <zcerza@redhat.com> - 0.4.3-1
- New upstream release.

* Sat Oct  8 2005 Jeremy Katz <katzj@redhat.com> - 0.4.2-1
- Initial build.

