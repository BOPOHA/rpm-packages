# Freelens RPM packaging

This repository builds Freelens from its pinned upstream GitHub release tag in
Fedora Mock. The upstream build needs Node 24, pnpm, Electron Builder, and
downloads the verified bundled `kubectl`, Helm, and Kubernetes-proxy executables.

Electron Builder creates an unpacked application directory from the source
build. The spec installs it under `%{_libdir}/freelens`, adds a `/usr/bin`
launcher, and installs desktop, icon, and AppStream metadata separately. The
spec deliberately disables automatic ELF dependency/provide generation because
Freelens bundles Electron/Chromium shared libraries.

## Fedora Mock build

```bash
make fc
```

`make fc` first creates an SRPM with `rpkg`, then builds it in the local Fedora
Mock chroot. Its results are written to `rpm-results/`. The upstream GitHub
source archive is downloaded as an SRPM source file; Mock then resolves the
lockfile and builds the Electron application. Fedora's Node package does not
ship Corepack, so the build installs a pinned Corepack launcher locally in the
build directory before pnpm selects the repository-pinned pnpm release.

After a successful build, `make fc` runs rpmlint against the produced binary
RPM and writes the tracked `rpmlint.report.txt`. The command fails on any
unfiltered finding. `rpmlint.toml` documents the narrow exceptions for
upstream's prebuilt Kubernetes and Electron helper binaries.

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

## TODO: package Corepack

The native build temporarily installs `corepack@0.34.0` locally with npm because
Fedora's Node.js package does not ship it. Create a `corepack` RPM in this same
Freelens COPR repository, then replace that local npm bootstrap with
`BuildRequires: corepack` in `freelens.spec`.
