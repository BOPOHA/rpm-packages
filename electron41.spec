# Bootstrap Electron 41 from source for parallel installation on Fedora.
#
# This is intended for COPR-style networked builds. Electron's documented build
# process synchronizes the Chromium revision and other dependencies from DEPS;
# it is therefore not yet a Fedora-reviewable, fully vendored source package.

%global electron_major 41
%global depot_tools_commit b6aeae1769e1448cf8b53d0d05c4b125fb5e2c93
%global electron_libdir %{_libdir}/electron%{electron_major}
%global electron_includedir %{_includedir}/electron%{electron_major}

Name:           electron%{electron_major}
Version:        41.10.0
Release:        1%{?dist}
Summary:        Cross-platform desktop runtime based on Chromium and Node.js
# Electron itself is MIT. The built runtime incorporates Chromium and further
# third-party components; LICENSES.chromium.html is installed with the RPM.
License:        MIT AND LicenseRef-Electron-ThirdParty
URL:            https://www.electronjs.org/
Source0:        https://github.com/electron/electron/archive/refs/tags/v%{version}.tar.gz#/electron-%{version}.tar.gz
Source1:        https://chromium.googlesource.com/chromium/tools/depot_tools/+archive/%{depot_tools_commit}.tar.gz#/depot_tools-%{depot_tools_commit}.tar.gz

ExclusiveArch:  x86_64 aarch64
BuildRequires:  bzip2
BuildRequires:  clang
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  glib2-devel
BuildRequires:  gtk3-devel
BuildRequires:  mesa-libgbm-devel
BuildRequires:  nodejs
BuildRequires:  nss-devel
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(atk)
BuildRequires:  pkgconfig(cups)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(expat)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libevent)
BuildRequires:  pkgconfig(libnotify)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libva)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(nspr)
BuildRequires:  pkgconfig(nss)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcomposite)
BuildRequires:  pkgconfig(xdamage)
BuildRequires:  pkgconfig(xext)
BuildRequires:  pkgconfig(xfixes)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(xscrnsaver)
BuildRequires:  pkgconfig(xtst)
BuildRequires:  python3
BuildRequires:  unzip

Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libnotify
Requires:       mesa-libgbm
Requires:       nss
Requires:       xdg-utils

%description
Electron is a cross-platform desktop runtime based on Chromium and Node.js.
This versioned runtime is installed under %{_libdir}/electron%{electron_major}
and invoked as electron%{electron_major}, allowing multiple Electron major
versions to coexist.

%package devel
Summary:        Development files for Electron %{electron_major}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
Headers and build metadata for native Node.js modules targeting Electron
%{electron_major}. The headers are installed in a versioned directory so this
package can coexist with other Electron development packages.

%prep
%setup -q -n electron-%{version}
# Gitiles archives depot_tools without a leading directory, so unpack it into
# a versioned sibling explicitly instead of relying on the setup macro.
mkdir ../depot_tools-%{depot_tools_commit}
tar -xzf %{SOURCE1} -C ../depot_tools-%{depot_tools_commit}

%build
# Keep the complete Chromium checkout outside the unpacked Electron source.
# gclient reads Electron's pinned DEPS file and makes src/electron unmanaged,
# preserving the Source0 content rather than fetching an unpinned Electron tip.
mkdir -p ../electron%{electron_major}-checkout/src
ln -s ../../electron-%{version} ../electron%{electron_major}-checkout/src/electron
mv ../depot_tools-%{depot_tools_commit} ../electron%{electron_major}-checkout/depot_tools
cd ../electron%{electron_major}-checkout
export PATH="$PWD/depot_tools:$PATH"
gclient config --name src/electron --unmanaged https://github.com/electron/electron
gclient sync -f --nohooks
cd src
export CHROMIUM_BUILDTOOLS_PATH="$PWD/buildtools"
gn gen out/Release --args='import("//electron/build/args/release.gn") is_component_build=false'
autoninja -C out/Release electron electron:electron_dist_zip electron:node_headers

%install
cd ../electron%{electron_major}-checkout/src
install -d %{buildroot}%{electron_libdir}
# electron_dist_zip creates the runtime layout without copying intermediate
# Chromium objects. Keep the versioned runtime self-contained.
unzip -q out/Release/dist.zip -d %{buildroot}%{electron_libdir}
install -d %{buildroot}%{_bindir}
ln -s ../%{_lib}/electron%{electron_major}/electron %{buildroot}%{_bindir}/electron%{electron_major}

install -d %{buildroot}%{electron_includedir}
cp -a out/Release/gen/node_headers/include/. %{buildroot}%{electron_includedir}/
install -Dm0644 electron/LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE
install -Dm0644 %{buildroot}%{electron_libdir}/LICENSES.chromium.html \
    %{buildroot}%{_licensedir}/%{name}/LICENSES.chromium.html

%check
test -x %{buildroot}%{electron_libdir}/electron
test -L %{buildroot}%{_bindir}/electron%{electron_major}
test -f %{buildroot}%{electron_libdir}/LICENSES.chromium.html
test -f %{buildroot}%{electron_includedir}/node/node.h

%files
%license %{_licensedir}/%{name}/LICENSE
%license %{_licensedir}/%{name}/LICENSES.chromium.html
%{_bindir}/electron%{electron_major}
%{electron_libdir}

%files devel
%{electron_includedir}

%changelog
* Fri Sep 04 2026 Anatolii Vorona <vorona.tolik@gmail.com> - 41.10.0-1
- Add a parallel-installable Electron 41 runtime and development package.
