# Repackage the upstream Electron application for the local RPM repository.
# The upstream release artifact is verified before its payload is installed.

%global debug_package %{nil}
%global _build_id_links none
%global upstream_version 1.10.3

%ifarch x86_64
%global upstream_arch amd64
%global upstream_sha256 8a7687b3db4165e40469d5e7f3598c90d12d90148f1084d12c8fedd33fa4b0a0
%endif
%ifarch aarch64
%global upstream_arch arm64
%global upstream_sha256 97091c134f8f8b64e78e4e03efd58f1abac908d004bb8a61f6cee97a4f12316d
%endif

Name:           freelens
Version:        %{upstream_version}
Release:        2%{?dist}
Summary:        Free IDE for Kubernetes
License:        MIT
URL:            https://freelens.app/
# rpkg expands Source0 from the committed repository. Source1 is fetched while
# making the SRPM, so Mock builds entirely from the SRPM's source payload.
Source0:        {{{ git_repo_pack }}}
Source1:        https://github.com/freelensapp/freelens/releases/download/v%{upstream_version}/Freelens-%{upstream_version}-linux-%{upstream_arch}.rpm

# This package ships upstream's prebuilt Electron application under /opt. Do
# not derive ELF dependencies from the bundled Chromium/Electron libraries:
# they would expose private bundled libraries as RPM capabilities and make the
# package depend on implementation details. Keep the runtime contract explicit.
AutoReqProv:    no
ExclusiveArch:  x86_64 aarch64
BuildRequires:  cpio
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
%setup -q -n freelens-packages

echo "%{upstream_sha256}  %{SOURCE1}" | sha256sum --check --strict
rpm2cpio %{SOURCE1} | cpio -idm --quiet

%build
# The upstream RPM contains the already-built Electron application.

%install
install -d %{buildroot}
cp -a opt usr %{buildroot}/

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
