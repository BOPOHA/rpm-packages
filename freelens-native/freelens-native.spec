# Build FreeLens from its pinned source tag and run it with system electron41.

%global debug_package %{nil}
%global _build_id_links none
%global upstream_version 1.10.3
%global electron_major 41
%global electron_version 41.10.0

# Native Node add-ons are private implementation details, not capabilities for
# other RPMs to consume. Automatic Requires remain enabled for their ELF ABIs.
%global __provides_exclude_from ^%{_libdir}/freelens-native/.*\\.node$

Name:           freelens-native
Version:        %{upstream_version}
Release:        1%{?dist}
Summary:        Free Kubernetes IDE using the system Electron runtime
License:        MIT
URL:            https://freelens.app/
Source0:        https://github.com/freelensapp/freelens/archive/refs/tags/v%{upstream_version}.tar.gz#/freelens-%{upstream_version}.tar.gz
Source1:        freelens-native.sh
Source2:        freelens.desktop
Source3:        freelens.1
Patch0:         freelens-1.10.3-system-resources-path.patch

ExclusiveArch:  x86_64
BuildRequires:  cpio
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  nodejs24
BuildRequires:  nodejs24-npm
BuildRequires:  python3
BuildRequires:  rpm
Requires:       electron%{electron_major}%{?_isa} >= %{electron_version}
Requires:       electron%{electron_major}%{?_isa} < 42
Requires:       xdg-utils
Provides:       freelens = %{version}-%{release}
Obsoletes:      freelens < %{version}-%{release}
Conflicts:      freelens-bundled

%description
Freelens is a free and open-source Kubernetes IDE. This thin variant uses the
separately packaged Electron 41 runtime instead of carrying another copy of
Electron and Chromium. It retains the application JavaScript, native Node
modules, and upstream Kubernetes helper binaries.

%prep
%autosetup -p1 -n freelens-%{upstream_version}

%build
# Fedora's Node package does not currently ship Corepack. Install only the
# pinned launcher in the build tree, then let it select upstream's pinned pnpm.
npm install --ignore-scripts --no-audit --no-fund --prefix .build-tools corepack@0.34.0
mkdir -p .build-tools/bin
node .build-tools/node_modules/corepack/dist/corepack.js enable --install-directory "$PWD/.build-tools/bin"
export PATH="$PWD/.build-tools/bin:$PATH"
pnpm install --frozen-lockfile
pnpm build:di
pnpm build

# Electron Builder performs upstream's native-module preparation and creates
# the canonical app.asar/resource layout. The packaging stage takes only the
# application resources, never the downloaded Electron/Chromium runtime.
pnpm build:app dir --x64
test -f freelens/dist/linux-unpacked/resources/app.asar
test -x freelens/dist/linux-unpacked/resources/x64/kubectl
test -x freelens/dist/linux-unpacked/resources/x64/helm
test -x freelens/dist/linux-unpacked/resources/x64/freelens-k8s-proxy

%install
install -d %{buildroot}%{_libdir}/freelens-native
cp -a freelens/dist/linux-unpacked/resources/app.asar \
    %{buildroot}%{_libdir}/freelens-native/
cp -a freelens/dist/linux-unpacked/resources/app.asar.unpacked \
    %{buildroot}%{_libdir}/freelens-native/
cp -a freelens/dist/linux-unpacked/resources/x64 \
    %{buildroot}%{_libdir}/freelens-native/

# Remove debug sections from the two runtime-loaded node-pty implementations.
%{__strip} --strip-unneeded \
    %{buildroot}%{_libdir}/freelens-native/app.asar.unpacked/node_modules/node-pty/bin/linux-x64-*/node-pty.node \
    %{buildroot}%{_libdir}/freelens-native/app.asar.unpacked/node_modules/node-pty/prebuilds/linux-x64/pty.node

# Retain only native add-ons for this RPM's architecture.
extract_zip_dir=%{buildroot}%{_libdir}/freelens-native/app.asar.unpacked/node_modules/@electron-internal/extract-zip
find "$extract_zip_dir" -type f -name '*.node' ! -name 'index.linux-x64-gnu.node' -delete

# electron-builder copies upstream development metadata that cannot be used by
# the installed application, plus Windows-only node-pty headers.
rm -f \
    %{buildroot}%{_libdir}/freelens-native/app.asar.unpacked/node_modules/jszip/.codeclimate.yml \
    %{buildroot}%{_libdir}/freelens-native/app.asar.unpacked/node_modules/jszip/.editorconfig \
    %{buildroot}%{_libdir}/freelens-native/app.asar.unpacked/node_modules/jszip/.eslintrc.js \
    %{buildroot}%{_libdir}/freelens-native/app.asar.unpacked/node_modules/jszip/.jekyll-metadata \
    %{buildroot}%{_libdir}/freelens-native/app.asar.unpacked/node_modules/node-pty/src/win/conpty.h \
    %{buildroot}%{_libdir}/freelens-native/app.asar.unpacked/node_modules/node-pty/src/win/path_util.h

install -Dm0755 %{SOURCE1} %{buildroot}%{_bindir}/freelens
install -Dm0644 %{SOURCE2} %{buildroot}%{_datadir}/applications/freelens.desktop
install -Dm0644 %{SOURCE3} %{buildroot}%{_mandir}/man1/freelens.1
install -Dm0644 freelens/build/metainfo.xml \
    %{buildroot}%{_datadir}/metainfo/app.freelens.Freelens.metainfo.xml
for icon in freelens/build/icons/*.png; do
    size="$(basename "$icon" .png)"
    install -Dm0644 "$icon" \
        %{buildroot}%{_datadir}/icons/hicolor/${size}/apps/freelens.png
done
install -Dm0644 LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE

%check
test -x %{buildroot}%{_bindir}/freelens
test -f %{buildroot}%{_libdir}/freelens-native/app.asar
test ! -e %{buildroot}%{_libdir}/freelens-native/electron
test ! -e %{buildroot}%{_libdir}/freelens-native/chrome-sandbox
test -f %{buildroot}%{_datadir}/applications/freelens.desktop

%files
%license %{_licensedir}/%{name}/LICENSE
%doc README.md
%{_bindir}/freelens
%{_libdir}/freelens-native
%{_mandir}/man1/freelens.1*
%{_datadir}/applications/freelens.desktop
%{_datadir}/icons/hicolor/*/apps/freelens.png
%{_datadir}/metainfo/app.freelens.Freelens.metainfo.xml

%changelog
* Tue Sep 22 2026 Anatolii Vorona <vorona.tolik@gmail.com> - 1.10.3-1
- Add thin FreeLens variant using the separately packaged Electron 41 runtime.
