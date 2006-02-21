Summary: GUI test tool and automation framework
Name: dogtail
Version: 0.5.0
Release: 2
License: GPL
Group: User Interface/X
URL: http://people.redhat.com/zcerza/dogtail/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArchitectures: noarch
BuildRequires: at-spi-devel
Requires: pyspi >= 0.5.3, pygtk2, rpm-python, ImageMagick, Xvfb

# hrm, the brp-python-bytecompile will byte-compile docs stuff too
# which is probably not what we want
%define __os_install_post [ -x /usr/lib/rpm/brp-python-bytecompile ] && /usr/lib/rpm/brp-python-bytecompile find $RPM_BUILD_ROOT/%{_docdir}/dogtail -name *.py[co] |xargs rm -f 

%description
GUI test tool and automation framework that uses Accessibility (a11y) 
technologies to communicate with desktop applications.

%prep
%setup -q

%build
python ./setup.py build

%install
rm -rf $RPM_BUILD_ROOT
python ./setup.py install -O2 --root=$RPM_BUILD_ROOT --record=%{name}.files
rm -rf $RPM_BUILD_ROOT/%{_docdir}/dogtail

%post
[ -x /usr/bin/gtk-update-icon-cache ] && gtk-update-icon-cache -f /usr/share/icons/hicolor 2>/dev/null
rm -rf /usr/share/doc/dogtail/

%clean
rm -rf $RPM_BUILD_ROOT

#%files -f %{name}.files
%files
%defattr(-,root,root,-)
/usr/bin/
/usr/lib/
/usr/share/applications/
/usr/share/dogtail/
/usr/share/icons/hicolor/
%doc COPYING
%doc README
%doc examples/

%changelog
* Fri Feb  17 2006 Zack Cerza <zcerza@redhat.com>
- It looks like xorg-x11-Xvfb changed names. Require 'Xvfb' instead.
- Remove Requires on python-elementtree, since RHEL4 didn't have it. The 
  functionality it provides is probably never used anyway, and will most likely
  be removed in the future.
- Don't run gtk-update-icon-cache if it doesn't exist.

* Fri Feb  3 2006 Zack Cerza <zcerza@redhat.com>
- New upstream release.
- Added missing BuildRequires on at-spi-devel.
- Added Requires on pyspi >= 0.5.3.
- Added Requires on rpm-python, pygtk2, ImageMagick, xorg-x11-Xvfb, 
  python-elementtree.
- Moved documentation (including examples) to the correct place.
- Make sure /usr/share/doc/dogtail is removed.
- Added 'gtk-update-icon-cache' to %post.

* Mon Oct 24 2005 Zack Cerza <zcerza@redhat.com>
- New upstream release.

* Sat Oct  8 2005 Jeremy Katz <katzj@redhat.com> 
- Initial build.

