%define name wammu
%define version 0.7
%define release 1

%define python-gammu-req 0.6
%define wxpython-req 2.4.1.2

Summary:    Mobile phone manager
Name:       %{name}
Version:    %{version}
Release:    %{release}
Source0:    %{name}-%{version}.tar.bz2
License:    GPL
%if %_vendor == "suse"
Group:      Hardware/Mobile
%else
Group:      Applications/Communications
%endif
Packager:   Michal Cihar <michal@cihar.com>
Vendor:     Michal Cihar <michal@cihar.com>
Prefix:     %{_prefix}


%if %_vendor == "suse"
Requires:   python >= 2.3.0, python-wxGTK >= %{wxpython-req}, python-gammu >= %{python-gammu-req}
BuildRequires: python-devel >= 2.3.0,  python-wxGTK >= %{wxpython-req}, python-gammu >= %{python-gammu-req}
%else
Requires:   python >= 2.3, wxPythonGTK >= %{wxpython-req}, python-gammu >= %{python-gammu-req}
BuildRequires: libpython2.3-devel >= 2.3, wxPythonGTK >= %{wxpython-req}, python-gammu >= %{python-gammu-req}
%endif
Url:        http://www.cihar.com/gammu/wammu
Buildroot:  %{_tmppath}/%name-%version-root

%description
Mobile phone manager using Gammu as it's backend. It works with any phone Gammu
supports - many Nokias, Siemens, Alcatel, ... Written using wxGTK.

%prep
%setup

%build
CFLAGS="$RPM_OPT_FLAGS" SKIPWXCHECK=yes python setup.py build

%install
SKIPWXCHECK=yes python setup.py install --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc ChangeLog README TODO AUTHORS FAQ COPYING NEWS
