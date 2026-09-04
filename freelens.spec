# Build the upstream Electron application from a pinned release source tag.

%global debug_package %{nil}
%global _build_id_links none
%global upstream_version 1.10.3

Name:           freelens
Version:        %{upstream_version}
Release:        3%{?dist}
Summary:        Free IDE for Kubernetes
License:        MIT
URL:            https://freelens.app/
# rpkg expands Source0 from the committed repository. Source1 is the pinned
# upstream GitHub release tag; the Electron application is built inside Mock.
Source0:        {{{ git_repo_pack }}}
Source1:        https://github.com/freelensapp/freelens/archive/refs/tags/v%{upstream_version}.tar.gz#/freelens-%{upstream_version}.tar.gz

# Do not derive ELF dependencies from the bundled Chromium/Electron libraries:
# they would expose private bundled libraries as RPM capabilities and make the
# package depend on implementation details. Keep the runtime contract explicit.
AutoReqProv:    no
ExclusiveArch:  x86_64 aarch64
BuildRequires:  cpio
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
# Fedora's generic nodejs capability currently resolves to nodejs22; Freelens
# declares Node >=24, so request the versioned Fedora packages explicitly.
BuildRequires:  nodejs24
BuildRequires:  nodejs24-npm
BuildRequires:  python3
BuildRequires:  rpm
Requires:       alsa-lib
Requires:       at-spi2-core
Requires:       gtk3
Requires:       libXScrnSaver
Requires:       libnotify
Requires:       nss
Requires:       xdg-utils

%description
Freelens is a free and open-source Kubernetes IDE. It provides a graphical
interface for managing Kubernetes clusters and bundles compatible kubectl,
Helm, and Freelens Kubernetes proxy binaries.

%prep
%setup -q -n freelens-packages -a 1

%build
cd freelens-%{upstream_version}
# Mock builds as the unprivileged mockbuild user. Install Corepack locally
# rather than into npm's root-owned global prefix, then expose its pnpm shim.
# TODO: replace this temporary bootstrap with a Corepack RPM built in this COPR
# repository and add it to BuildRequires.
npm install --ignore-scripts --no-audit --no-fund --prefix .build-tools corepack@0.34.0
mkdir -p .build-tools/bin
node .build-tools/node_modules/corepack/dist/corepack.js enable --install-directory "$PWD/.build-tools/bin"
export PATH="$PWD/.build-tools/bin:$PATH"
pnpm install --frozen-lockfile
pnpm build:di
pnpm build
pnpm build:app dir --x64
test -x freelens/dist/linux-unpacked/freelens

%install
install -d %{buildroot}%{_bindir} %{buildroot}%{_libdir}
cp -a freelens-%{upstream_version}/freelens/dist/linux-unpacked \
    %{buildroot}%{_libdir}/freelens

ln -s %{_libdir}/freelens/freelens %{buildroot}%{_bindir}/freelens
install -Dm0644 freelens.desktop \
    %{buildroot}%{_datadir}/applications/freelens.desktop
install -Dm0644 freelens-%{upstream_version}/freelens/build/metainfo.xml \
    %{buildroot}%{_datadir}/metainfo/app.freelens.Freelens.metainfo.xml
for icon in freelens-%{upstream_version}/freelens/build/icons/*.png; do
    size="$(basename "$icon" .png)"
    install -Dm0644 "$icon" \
        %{buildroot}%{_datadir}/icons/hicolor/${size}/apps/freelens.png
done

# Keep license files marked as licenses without listing them twice through the
# recursively installed application directory.
find %{buildroot}%{_libdir}/freelens -mindepth 1 \
    ! -path '%{buildroot}%{_libdir}/freelens/LICENSE.electron.txt' \
    ! -path '%{buildroot}%{_libdir}/freelens/LICENSES.chromium.html' \
    -printf '%{_libdir}/freelens/%%P\n' > %{_builddir}/freelens.files

%check
test -x %{buildroot}%{_libdir}/freelens/freelens
test -f %{buildroot}%{_datadir}/applications/freelens.desktop
test -f %{buildroot}%{_datadir}/metainfo/app.freelens.Freelens.metainfo.xml

%files -f %{_builddir}/freelens.files
%dir %{_libdir}/freelens
%license %{_libdir}/freelens/LICENSE.electron.txt
%license %{_libdir}/freelens/LICENSES.chromium.html
%{_bindir}/freelens
%{_datadir}/applications/freelens.desktop
%{_datadir}/icons/hicolor/*/apps/freelens.png
%{_datadir}/metainfo/app.freelens.Freelens.metainfo.xml

%changelog
* Fri Sep 04 2026 Anatolii Vorona <vorona.tolik@gmail.com> - 1.10.3-2
- Initial downstream RPM repackage of the verified upstream binary release.
