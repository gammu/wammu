%define name wammu
%define version 0.10.1
%define release 1

%define python_gammu_req 0.8

Summary:        Mobile phone manager
Name:           %{name}
Version:        %{version}
Release:        %{release}
Source0:        %{name}-%{version}.tar.bz2
License:        GPL
%if %_vendor == "suse"
Group:          Hardware/Mobile
%else
Group:          Applications/Communications
%endif
Packager:       Michal Cihar <michal@cihar.com>
Vendor:         Michal Cihar <michal@cihar.com>
Prefix:         %{_prefix}

# /usr/bin/pycrust is here for make vendor independant dependancy on wxPython.
# If you know better way, please let me know.
Requires:       /usr/bin/pycrust, python-gammu >= %{python_gammu_req}
BuildRequires:  /usr/bin/pycrust, python-gammu >= %{python_gammu_req}

%py_requires -d

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
sed -i '/man1/ D' INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc README TODO AUTHORS FAQ COPYING NEWS
%doc %{_mandir}/man1/*
