%define name wammu
%define version 0.26
%define rel 1
%define extension   bz2

%define python_gammu_req 0.24

%if %{!?py_ver:1}0 == 10
%define py_ver %(python -c "import sys; v=sys.version_info[:2]; print '%%d.%%d'%%v" 2>/dev/null || echo PYTHON-NOT-FOUND)
%endif

%define py_minver %py_ver
%define py_maxver %(python -c "import sys; a,b=sys.version_info[:2]; print '%%d.%%d'%%(a,b+1)" 2>/dev/null || echo PYTHON-NOT-FOUND) 

Summary:        Mobile phone manager
Name:           %{name}
Version:        %{version}
Release:        %{rel}
Source0:        %{name}-%{version}.tar.%{extension}
License:        GPL
%if 0%{?suse_version}
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
BuildRequires:  python, python-devel
Requires:       python >= %py_minver, python < %py_maxver

Url:        http://wammu.eu/
Buildroot:  %{_tmppath}/%name-%version-root
BuildArch: noarch

%description
Mobile phone manager using Gammu as it's backend. It works with any phone Gammu
supports - many Nokias, Siemens, Alcatel, ... Written using wxGTK.

%prep
%setup

%build
CFLAGS="$RPM_OPT_FLAGS" python setup.py build --skip-deps

%install
python setup.py install --skip-deps --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES --prefix=%{_prefix}
sed -i '/man1/ D' INSTALLED_FILES

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc README AUTHORS FAQ COPYING NEWS
%doc %{_mandir}/man1/*
