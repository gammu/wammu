%define name wammu
%define version 0.30
%define rel 1
%define extension   bz2

%define python_gammu_req 0.24

%if %{!?py_ver:1}0 == 10
%define py_ver %(python -c "import sys; v=sys.version_info[:2]; print '%%d.%%d'%%v" 2>/dev/null || echo PYTHON-NOT-FOUND)
%endif

%if %{!?%py_sitedir:1}0 == 10
%define py_prefix      %(python -c "import sys; print sys.prefix" 2>/dev/null || echo PYTHON-NOT-FOUND)
%if 0%{?fedora_version} || 0%{?centos_version} || 0%{?rhel_version} || 0%{?mandriva_version}
%define py_libdir      %{py_prefix}/lib/python%{py_ver}
%else
%define py_libdir      %{py_prefix}/%{_lib}/python%{py_ver}
%endif
%define py_sitedir     %{py_libdir}/site-packages
%endif

%define py_minver %py_ver
%define py_maxver %(python -c "import sys; a,b=sys.version_info[:2]; print '%%d.%%d'%%(a,b+1)" 2>/dev/null || echo PYTHON-NOT-FOUND) 

Summary:        Mobile phone manager
Name:           %{name}
Version:        %{version}
Release:        %{rel}
Source0:        %{name}-%{version}.tar.%{extension}
License:        GPLv2
%if 0%{?suse_version}
Group:          Hardware/Mobile
%else
Group:          Applications/Communications
%endif
Vendor:         Michal Cihar <michal@cihar.com>

Requires:       wxPython >= 2.6, python-gammu >= %{python_gammu_req}, python >= %py_minver, python < %py_maxver
BuildRequires:  python, python-devel
%if 0%{?suse_version}
BuildRequires:  update-desktop-files
%endif

Url:        http://wammu.eu/
Buildroot:  %{_tmppath}/%name-%version-root
# These distributions use /usr/lib for python on all architectures
%if 0%{?fedora_version} || 0%{?centos_version} || 0%{?rhel_version} || 0%{?mandriva_version}
BuildArch: noarch
%endif

%description
It works with any phone that Gammu supports, including many models from
Nokia, Siemens, and Alcatel. It has complete support (read, edit,
delete, copy) for contacts, todo, and calendar. It can read, save, and
send SMS. It includes an SMS composer for multi-part SMS messages, and
it can display SMS messages that include pictures. Currently, only text
and predefined bitmaps or sounds can be edited in the SMS composer. It
can export messages to an IMAP4 server (or other email storage).

This program does not support browsing files in phone, use gMobileMedia
instead.


%prep
%setup -q

%build
CFLAGS="$RPM_OPT_FLAGS" python setup.py build --skip-deps

%install
rm -rf %buildroot
mkdir %buildroot
python setup.py install --skip-deps --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES --prefix=%{_prefix}
sed -i '/man1/ D ; /locale/ D' INSTALLED_FILES
%find_lang %{name}
cat %{name}.lang >> INSTALLED_FILES
%if 0%{?suse_version}
%suse_update_desktop_file %{name}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%files -f INSTALLED_FILES
%defattr(-,root,root)
%doc README AUTHORS FAQ COPYING ChangeLog
%doc %{_mandir}/man1/*
%dir %py_sitedir/Wammu
%dir %py_sitedir/Wammu/wxcomp
%dir /usr/share/Wammu
%dir /usr/share/Wammu/images
%dir /usr/share/Wammu/images/icons
%dir /usr/share/Wammu/images/misc

%changelog
* Wed Oct  8 2008 michal@cihar.com
- do not make it noarch package because it is sometimes in lib64 dir
* Mon Jan 05 2004 michal@cihar.com
- initial packaging
- see SVN log for changelog
