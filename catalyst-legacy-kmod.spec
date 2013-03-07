# buildforkernels macro hint: when you build a new version or a new release
# that contains bugfixes or other improvements then you must disable the
# "buildforkernels newest" macro for just that build; immediately after
# queuing that build enable the macro again for subsequent builds; that way
# a new akmod package will only get build when a new one is actually needed
%global buildforkernels newest

# Tweak to have debuginfo - part 1/2
%if 0%{?fedora} > 7
%define __debug_install_post %{_builddir}/%{?buildsubdir}/find-debuginfo.sh %{_builddir}/%{?buildsubdir}\
%{nil}
%endif

Name:        catalyst-legacy-kmod
Version:     12.6
Release:     3%{?dist}
# Taken over by kmodtool
Summary:     AMD display legacy driver kernel module
Group:       System Environment/Kernel
License:     Redistributable, no modification permitted
URL:         http://ati.amd.com/support/drivers/linux/linux-radeon.html
Source0:     http://www.linux-ati-drivers.homecall.co.uk/catalyst-legacy-kmod-data-%{version}.tar.bz2
Source11:    catalyst-kmodtool-excludekernel-filterfile
Patch0:      compat_alloc-Makefile.patch
Patch1:      3.5-do_mmap.patch
Patch2:      3.7_kernel.patch
Patch3:      3.8_kernel.patch
BuildRoot:   %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

# needed for plague to make sure it builds for i686
ExclusiveArch:  i686 x86_64

# get the needed BuildRequires (in parts depending on what we build for)
BuildRequires:  %{_bindir}/kmodtool
%{!?kernels:BuildRequires: buildsys-build-rpmfusion-kerneldevpkgs-%{?buildforkernels:%{buildforkernels}}%{!?buildforkernels:current}-%{_target_cpu} }
# kmodtool does its magic here
%{expand:%(kmodtool --target %{_target_cpu} --repo rpmfusion --kmodname %{name} --filterfile %{SOURCE11} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description
The catalyst legacy %{version} display driver kernel module.


%prep
# error out if there was something wrong with kmodtool
%{?kmodtool_check}
# print kmodtool output for debugging purposes:
kmodtool  --target %{_target_cpu} --repo rpmfusion --kmodname %{name} --filterfile %{SOURCE11} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null
%setup -q -c -T -a 0

# Tweak to have debuginfo - part 2/2
%if 0%{?fedora} > 7
cp -p %{_prefix}/lib/rpm/find-debuginfo.sh .
sed -i -e 's|strict=true|strict=false|' find-debuginfo.sh
%endif

mkdir fglrxpkg
%ifarch %{ix86}
cp -r fglrx/common/* fglrx/arch/x86/* fglrxpkg/
%endif

%ifarch x86_64
cp -r fglrx/common/* fglrx/arch/x86_64/* fglrxpkg/
%endif

# proper permissions
find fglrxpkg/lib/modules/fglrx/build_mod/ -type f -print0 | xargs -0 chmod 0644

# debuginfo fix
#sed -i -e 's|strip -g|/bin/true|' fglrxpkg/lib/modules/fglrx/build_mod/make.sh

pushd fglrxpkg
%patch0 -p0 -b.compat_alloc
%patch1 -p0 -b.3.5-do_mmap
%patch2 -p0 -b.3.7_kernel
%patch3 -p0 -b.3.8_kernel
popd

for kernel_version  in %{?kernel_versions} ; do
    cp -a fglrxpkg/  _kmod_build_${kernel_version%%___*}
done


%build
for kernel_version in %{?kernel_versions}; do
    pushd _kmod_build_${kernel_version%%___*}/lib/modules/fglrx/build_mod/2.6.x
    make CC="gcc" PAGE_ATTR_FIX=0 MODVERSIONS=8.98 \
      KVER="${kernel_version%%___*}" \
      KDIR="/usr/src/kernels/${kernel_version%%___*}"
    popd
done


%install
rm -rf $RPM_BUILD_ROOT
for kernel_version in %{?kernel_versions}; do
    install -D -m 0755 _kmod_build_${kernel_version%%___*}/lib/modules/fglrx/build_mod/2.6.x/fglrx.ko $RPM_BUILD_ROOT%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/fglrx.ko
done
%{?akmod_install}


%clean
rm -rf $RPM_BUILD_ROOT


%changelog
* Thu Mar 07 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-3
- Patch for 3.8 kernel

* Sat Mar 02 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.11
- Rebuilt for kernel

* Tue Feb 26 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.10
- Rebuilt for kernel

* Tue Feb 19 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.9
- Rebuilt for kernel

* Sat Feb 16 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.8
- Rebuilt for kernel

* Sat Feb 16 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.7
- Rebuilt for kernel

* Tue Feb 05 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.6
- Rebuilt for kernel

* Mon Feb 04 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.5
- Rebuilt for akmod

* Wed Jan 30 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.4
- Rebuilt for akmod

* Wed Jan 30 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.3
- Rebuilt for updated kernel

* Fri Jan 25 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.2
- Rebuilt for updated kernel

* Sat Jan 19 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-2.1
- Rebuilt for updated kernel

* Sat Jan 19 2013 Leigh Scott <leigh123linux@googlemail.com> - 12.6-2
- patch for 3.7 kernel

* Thu Jan 17 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-1.7
- Rebuilt for updated kernel

* Wed Jan 09 2013 Nicolas Chauvet <kwizart@gmail.com> - 12.6-1.6
- Rebuilt for updated kernel

* Sun Dec 23 2012 Nicolas Chauvet <kwizart@gmail.com> - 12.6-1.5
- Rebuilt for updated kernel

* Sat Dec 22 2012 Nicolas Chauvet <kwizart@gmail.com> - 12.6-1.4
- Rebuilt for updated kernel

* Tue Dec 18 2012 Nicolas Chauvet <kwizart@gmail.com> - 12.6-1.3
- Rebuilt for updated kernel

* Wed Dec 12 2012 Nicolas Chauvet <kwizart@gmail.com> - 12.6-1.2
- Rebuilt for updated kernel

* Wed Dec 05 2012 Nicolas Chauvet <kwizart@gmail.com> - 12.6-1.1
- Rebuilt for updated kernel

* Thu Nov 29 2012 Leigh Scott <leigh123linux@googlemail.com> - 12.6-1
- Update to Catalyst 12.6 legacy (internal version 8.97.100.3)

* Fri Jul 06 2012 leigh scott <leigh123linux@googlemail.com> - 12.6-0.1
- Based on xorg-x11-drv-catalyst
- Update to Catalyst legacy 12.6 beta (internal version 8.97.100.3)
