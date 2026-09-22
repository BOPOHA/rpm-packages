# Third-party software and trademarks

The top-level MIT license applies to packaging code, specifications, patches,
scripts, and documentation created for this repository. It does not relicense
upstream projects, downloaded source archives, prepared build inputs, or the
contents of resulting RPM packages.

Repository patches include portions derived from FreeLens and Electron source:

- FreeLens is MIT-licensed. Copyright (c) 2024-2026 FreeLens Authors and
  copyright (c) 2022 OpenLens Authors. The upstream license is available at
  <https://github.com/freelensapp/freelens/blob/main/LICENSE>.
- Electron is MIT-licensed. Its upstream license and third-party Chromium
  notices are available at
  <https://github.com/electron/electron/blob/main/LICENSE>.
- Kubernetes and kubectl are Apache-2.0 licensed. Their upstream notices are
  available at <https://github.com/kubernetes/kubernetes>.
- Helm is Apache-2.0 licensed. Its upstream notices are available at
  <https://github.com/helm/helm>.

The `freelens-bundled` RPM additionally installs FreeLens's generated
production dependency-license report, the exact `freelens-k8s-proxy` license,
and the Electron and Chromium notices included by Electron Builder. These
files are installed as RPM `%license` content; they are not replaced by this
repository's top-level MIT license.

Each upstream project and dependency remains subject to its own copyright,
license, notice, patent, and redistribution terms. Binary packages can contain
many additional dependencies and are not cleared for public distribution merely
because this packaging repository is MIT-licensed.

Electron, FreeLens, OpenLens, Kubernetes, Helm, and their respective names,
logos, and marks belong to their owners. This repository is an independent
packaging proof of concept and is not affiliated with or endorsed by those
projects or trademark owners.
