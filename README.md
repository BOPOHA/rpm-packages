# Freelens RPM packaging

This repository repackages the official Freelens Electron RPM for the local
RPM repository. It does not rebuild the TypeScript/Electron application from
source: that upstream build needs Node 24, pnpm, Electron Builder, and downloads
the verified bundled `kubectl`, Helm, and Kubernetes-proxy executables.

The spec extracts the official release payload, verifies its SHA-256 digest,
and applies explicit Fedora/RHEL-family runtime dependencies. It deliberately
disables automatic ELF dependency/provide generation because Freelens bundles
Electron/Chromium shared libraries under `/opt/Freelens`.

## Fedora Mock build

```bash
make fc
```

`make fc` first creates an SRPM with `rpkg`, then builds it in the local Fedora
Mock chroot. Its results are written to `rpm-results/`. The upstream RPM is
downloaded as an SRPM source file and verified again by `%prep` within Mock.

Create only the source RPM with:

```bash
make srpm
```

`fc` currently builds x86_64, matching the existing local Fedora mock profile.
The spec contains the verified upstream assets for both x86_64 and aarch64.

## Updating Freelens

1. Change `VERSION` in `Makefile` and `upstream_version` in `freelens.spec`.
2. Download the release asset and record its official SHA-256 in the matching
   architecture branch of `freelens.spec`.
3. Commit the changed packaging repository, then build with `make fc` and
   install/test the resulting RPM on the supported
   Fedora/RHEL-family target.

The current upstream binary requires glibc 2.34 or newer, so target RHEL 9+
or Fedora rather than RHEL 8.
