%define name wammu
%define version 0.25
%define release 1

%define python_gammu_req 0.20

%if %{!?py_ver:1}0 == 10
%define py_ver %(python -c "import sys; v=sys.version_info[:2]; print '%%d.%%d'%%v" 2>/dev/null || echo PYTHON-NOT-FOUND)
%endif

%define py_minver %py_ver
%define py_maxver %(python -c "import sys; a,b=sys.version_info[:2]; print '%%d.%%d'%%(a,b+1)" 2>/dev/null || echo PYTHON-NOT-FOUND) 

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
BuildRequires:  python, python-devel
Requires:       python >= %py_minver, python < %py_maxver

Url:        http://wammu.eu/
Buildroot:  %{_tmppath}/%name-%version-root

%description
Mobile phone manager using Gammu as it's backend. It works with any phone Gammu
supports - many Nokias, Siemens, Alcatel, ... Written using wxGTK.

%prep
%setup

%build
CFLAGS="$RPM_OPT_FLAGS" python setup.py build --skip-deps

%install
python setup.py install --skip-deps --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
sed -i '/man1/ D' INSTALLED_FILES
%if %_vendor == "redhat"
	# Dirty hack: on Fedora, the .pyo files don't get written to
	# INSTALLED_FILES, so put them there manually (this should also be
	# safe on systems where this works correctly, as we remove
	# duplicates).
	grep '\.pyc$' INSTALLED_FILES | sed 's/\.pyc/.pyo/g' >> INSTALLED_FILES.tmp
	cat INSTALLED_FILES >> INSTALLED_FILES.tmp
	sort -u INSTALLED_FILES.tmp > INSTALLED_FILES
	rm -f INSTALLED_FILES.tmp
	# End dirty hack
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc README AUTHORS FAQ COPYING NEWS
%doc %{_mandir}/man1/*
