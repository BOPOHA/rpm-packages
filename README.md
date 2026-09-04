# Freelens RPM packaging

This repository builds Freelens from its pinned upstream GitHub release tag in
Fedora Mock. The upstream build needs Node 24, pnpm, Electron Builder, and
downloads the verified bundled `kubectl`, Helm, and Kubernetes-proxy executables.

Electron Builder creates an intermediate RPM from the source build; the spec
extracts its payload into the final RPM. This preserves upstream's launcher,
icons, AppStream metadata, and bundled Kubernetes tools. The spec deliberately
disables automatic ELF dependency/provide generation because Freelens bundles
Electron/Chromium shared libraries under `/opt/Freelens`.

## Fedora Mock build

```bash
make fc
```

`make fc` first creates an SRPM with `rpkg`, then builds it in the local Fedora
Mock chroot. Its results are written to `rpm-results/`. The upstream GitHub
source archive is downloaded as an SRPM source file; Mock then resolves the
lockfile and builds the Electron application.

Create only the source RPM with:

```bash
make srpm
```

`fc` currently builds x86_64, matching the existing local Fedora Mock profile.

## Updating Freelens

1. Change `VERSION` in `Makefile` and `upstream_version` in `freelens.spec`.
2. Confirm the source tag exists and update the expected Electron build target
   if the upstream architecture matrix changes.
3. Commit the changed packaging repository, then build with `make fc` and
   install/test the resulting RPM on the supported
   Fedora/RHEL-family target.

The current upstream binary requires glibc 2.34 or newer, so target RHEL 9+
or Fedora rather than RHEL 8.
