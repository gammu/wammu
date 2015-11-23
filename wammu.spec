Name:           wammu
Version:        0.41
Release:        1

%define extension   bz2

%define python_gammu_req 0.24

%{!?__python: %define __python python}
%define wammu_python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(0)")

Summary:        Mobile phone manager
Source:         http://dl.cihar.com/%{name}/latest/%{name}-%{version}.tar.%{extension}
License:        GPL-2.0
%if 0%{?suse_version}
Group:          Hardware/Mobile
%else
Group:          Applications/Communications
%endif
Vendor:         Michal Čihař <michal@cihar.com>

Requires:       wxPython >= 2.6, python-gammu >= %{python_gammu_req}
BuildRequires:  python-devel
%if 0%{?suse_version}
BuildRequires:  python-xml
BuildRequires:  update-desktop-files
%endif
%if 0%{?fedora_version} || 0%{?centos_version} || 0%{?rhel_version} || 0%{?fedora} || 0%{?rhel}
BuildRequires:  desktop-file-utils
%endif
%{?py_requires}

Url:        http://wammu.eu/
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root
# These distributions use /usr/lib for python on all architectures
%if 0%{?fedora_version} || 0%{?centos_version} || 0%{?rhel_version} || 0%{?fedora} || 0%{?rhel} || 0%{?mandriva_version} || 0%{?suse_version} > 1110
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
# Ugly hack for SUSE because it does not like TelephonyTools
%if 0%{?suse_version}
sed -i 's/TelephonyTools/Telephony/' wammu.desktop.in
%endif


%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build

%install
%if 0%{?suse_version} == 0
rm -rf %buildroot
mkdir %buildroot
%endif
%{__python} setup.py install --root=%buildroot --prefix=%{_prefix}
%if 0%{?fedora_version} || 0%{?centos_version} || 0%{?rhel_version} || 0%{?fedora} || 0%{?rhel}
%{__python} setup.py install -O1 --root=%buildroot --prefix=%{_prefix}
%endif
%find_lang %{name}
%if 0%{?suse_version}
%suse_update_desktop_file %{name}
%endif
%if 0%{?fedora_version} || 0%{?centos_version} || 0%{?rhel_version} || 0%{?fedora} || 0%{?rhel}
desktop-file-install --vendor "" \
    --dir %buildroot%{_datadir}/applications \
    --mode 0644 \
    --remove-category=Application \
    %buildroot%{_datadir}/applications/%{name}.desktop
%endif

%clean
rm -rf %buildroot

%files -f %name.lang
%defattr(-,root,root)
%doc COPYING README.rst PKG-INFO ChangeLog
%doc %{_mandir}/man1/*
%lang(cs) %doc %{_mandir}/cs
%lang(de) %doc %{_mandir}/de
%lang(en_GB) %doc %{_mandir}/en_GB
%lang(es) %doc %{_mandir}/es
%lang(et) %doc %{_mandir}/et
%lang(da) %doc %{_mandir}/da
%lang(fr) %doc %{_mandir}/fr
%lang(hu) %doc %{_mandir}/hu
%lang(id) %doc %{_mandir}/id
%lang(it) %doc %{_mandir}/it
%lang(nl) %doc %{_mandir}/nl
%lang(pt_BR) %doc %{_mandir}/pt_BR
%lang(ru) %doc %{_mandir}/ru
%lang(sk) %doc %{_mandir}/sk
%lang(tr) %doc %{_mandir}/tr
%lang(uk) %doc %{_mandir}/uk

%{_bindir}/%{name}
%{_bindir}/%{name}-configure
%{_datadir}/Wammu
%{_datadir}/pixmaps/*
%dir %{_datadir}/appdata
%{_datadir}/appdata/%{name}.appdata.xml
%{_datadir}/applications/%{name}.desktop
%{wammu_python_sitelib}/*

%changelog
