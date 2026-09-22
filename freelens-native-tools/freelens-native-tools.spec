# Package FreeLens's pinned Kubernetes helper executables independently from
# the Electron application, so they can be updated without rebuilding it.

%global debug_package %{nil}
%global kubectl_version 1.36.2
%global helm_version 4.2.2
%global proxy_version 1.8.0

Name:           freelens-native-tools
Version:        1
Release:        1%{?dist}
Summary:        Pinned Kubernetes helper tools for FreeLens
License:        Apache-2.0 AND MIT
URL:            https://freelens.app/
Source0:        https://dl.k8s.io/release/v%{kubectl_version}/bin/linux/amd64/kubectl#/kubectl
Source1:        https://dl.k8s.io/release/v%{kubectl_version}/bin/linux/amd64/kubectl.sha256#/kubectl.sha256
Source2:        https://get.helm.sh/helm-v%{helm_version}-linux-amd64.tar.gz#/helm-v%{helm_version}-linux-amd64.tar.gz
Source3:        https://get.helm.sh/helm-v%{helm_version}-linux-amd64.tar.gz.sha256sum#/helm-v%{helm_version}-linux-amd64.tar.gz.sha256sum
Source4:        https://github.com/freelensapp/freelens-k8s-proxy/releases/download/v%{proxy_version}/freelens-k8s-proxy-linux-amd64#/freelens-k8s-proxy
Source5:        https://github.com/freelensapp/freelens-k8s-proxy/releases/download/v%{proxy_version}/freelens-k8s-proxy-linux-amd64.sha256#/freelens-k8s-proxy.sha256
Source6:        https://raw.githubusercontent.com/kubernetes/kubernetes/v%{kubectl_version}/LICENSE#/LICENSE.kubernetes
Source7:        https://raw.githubusercontent.com/freelensapp/freelens-k8s-proxy/v%{proxy_version}/LICENSE#/LICENSE.freelens-k8s-proxy
Source8:        README.md

ExclusiveArch:  x86_64
BuildRequires:  tar
Requires:       freelens-native%{?_isa}
Conflicts:      freelens-bundled
Provides:       freelens-native-kubectl = %{kubectl_version}
Provides:       freelens-native-helm = %{helm_version}
Provides:       freelens-native-k8s-proxy = %{proxy_version}

%description
Version-pinned kubectl, Helm, and FreeLens Kubernetes proxy executables for
the native FreeLens package. They are installed in FreeLens's private resource
directory and are not replacements for system kubectl or Helm packages.

%prep
expected_kubectl="$(tr -d '[:space:]' < %{SOURCE1})"
printf '%s  %s\n' "$expected_kubectl" "%{SOURCE0}" | sha256sum -c -

expected_proxy="$(tr -d '[:space:]' < %{SOURCE5})"
printf '%s  %s\n' "$expected_proxy" "%{SOURCE4}" | sha256sum -c -

(
    cd "$(dirname %{SOURCE2})"
    sha256sum -c "%{SOURCE3}"
)
mkdir helm
tar -xzf %{SOURCE2} --strip-components=1 -C helm

%build
# The upstream executables are prebuilt and checksum-verified in %prep.

%install
install -d %{buildroot}%{_libdir}/freelens-native/x64
install -pm0755 %{SOURCE0} %{buildroot}%{_libdir}/freelens-native/x64/kubectl
install -pm0755 helm/helm %{buildroot}%{_libdir}/freelens-native/x64/helm
install -pm0755 %{SOURCE4} %{buildroot}%{_libdir}/freelens-native/x64/freelens-k8s-proxy
install -Dm0644 %{SOURCE6} %{buildroot}%{_licensedir}/%{name}/LICENSE.kubernetes
install -Dm0644 helm/LICENSE %{buildroot}%{_licensedir}/%{name}/LICENSE.helm
install -Dm0644 %{SOURCE7} %{buildroot}%{_licensedir}/%{name}/LICENSE.freelens-k8s-proxy
install -Dm0644 %{SOURCE8} %{buildroot}%{_docdir}/%{name}/README.md

%check
test -x %{buildroot}%{_libdir}/freelens-native/x64/kubectl
test -x %{buildroot}%{_libdir}/freelens-native/x64/helm
test -x %{buildroot}%{_libdir}/freelens-native/x64/freelens-k8s-proxy

%files
%license %{_licensedir}/%{name}/LICENSE.kubernetes
%license %{_licensedir}/%{name}/LICENSE.helm
%license %{_licensedir}/%{name}/LICENSE.freelens-k8s-proxy
%doc %{_docdir}/%{name}/README.md
%dir %{_libdir}/freelens-native
%dir %{_libdir}/freelens-native/x64
%{_libdir}/freelens-native/x64/kubectl
%{_libdir}/freelens-native/x64/helm
%{_libdir}/freelens-native/x64/freelens-k8s-proxy

%changelog
* Tue Sep 22 2026 Anatolii Vorona <vorona.tolik@gmail.com> - 1-1
- Split the pinned Kubernetes helper executables from freelens-native.
