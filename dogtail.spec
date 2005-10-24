Summary: GUI test tool and automation framework
Name: dogtail
Version: 0.4.3
Release: 1
License: GPL
Group: User Interface/X
URL: http://people.redhat.com/zcerza/dogtail/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildArchitectures: noarch

# hrm, the brp-python-bytecompile will byte-compile docs stuff too
# which is probably not what we want
%define __os_install_post \
  [ -x /usr/lib/rpm/brp-python-bytecompile ] && /usr/lib/rpm/brp-python-bytecompile \
  find $RPM_BUILD_ROOT/%{_docdir}/dogtail -name *.py[co] |xargs rm -f \
%{nil}

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

%clean
rm -rf $RPM_BUILD_ROOT


%files -f %{name}.files
%defattr(-,root,root,-)
%doc COPYING


%changelog
* Mon Oct 24 2005 Zack Cerza <zcerza@redhat.com>
- New upstream release.

* Sat Oct  8 2005 Jeremy Katz <katzj@redhat.com> 
- Initial build.

