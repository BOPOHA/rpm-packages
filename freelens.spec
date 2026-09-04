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
BuildRequires:  nodejs >= 24
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
npm install --global corepack@0.34.0
corepack enable pnpm
pnpm install --frozen-lockfile
pnpm build:di
pnpm build
pnpm build:app rpm --x64

rpm_file="$(find freelens/dist -maxdepth 1 -type f -name '*.rpm' -print -quit)"
test -n "$rpm_file"
cp "$rpm_file" %{_builddir}/freelens-built.rpm

%install
install -d %{buildroot}
rpm2cpio %{_builddir}/freelens-built.rpm | cpio -idm --quiet -D %{buildroot}

%check
test -x %{buildroot}/opt/Freelens/freelens
test -f %{buildroot}%{_datadir}/applications/freelens.desktop
test -f %{buildroot}%{_datadir}/metainfo/app.freelens.Freelens.metainfo.xml

%files
%license /opt/Freelens/LICENSE.electron.txt
%license /opt/Freelens/LICENSES.chromium.html
/opt/Freelens
%{_datadir}/applications/freelens.desktop
%{_datadir}/icons/hicolor/*/apps/freelens.png
%{_datadir}/metainfo/app.freelens.Freelens.metainfo.xml

%changelog
* Fri Sep 04 2026 Anatolii Vorona <vorona.tolik@gmail.com> - 1.10.3-2
- Initial downstream RPM repackage of the verified upstream binary release.
