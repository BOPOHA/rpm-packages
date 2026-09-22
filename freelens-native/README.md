# freelens-native RPM packaging

> **Publication scope:** this is a packaging proof of concept only. This
> repository does not publish or support public `freelens-native` binary RPMs.
> Public binaries require the separate Electron and dependency legal/security
> reviews to be completed first.

`freelens-native` is the thin FreeLens package. It contains the FreeLens
application and its native Node add-ons, but it does not contain Electron,
Chromium, or Kubernetes helper tools. It runs with the separately installed
`electron41` and `freelens-native-tools` RPMs.

FreeLens 1.10.3 pins Electron 41.10.0. The RPM therefore requires Electron
41.10.0 or newer within major version 41. The packages `freelens-native` and
`freelens-bundled` are mutually exclusive because both provide the `freelens`
command and desktop integration.

## Build on Fedora

```bash
make fc
```

`make fc` installs the locally built `electron41` and `electron41-devel` RPMs
from `$(HOME)/rpmbuild/RPMS/x86_64` into the Mock buildroot before the build.
To use a different location, pass `ELECTRON_RPM_DIR=/path/to/rpms`.

The build downloads the pinned upstream source and JavaScript dependencies in
a Fedora Mock chroot. Electron Builder is used to assemble the application,
but receives the installed Electron 41 RPM payload as its input. It neither
downloads nor copies Electron; only `resources/app.asar` and its unpacked
native modules are copied into this RPM. Kubernetes helper programs come from
the sibling tools RPM.

The result is written under `rpm-results/`. If no other FreeLens variant is
installed, install it with DNF so the `electron41` dependency is checked:

```bash
sudo dnf install rpm-results/freelens-native-*.x86_64.rpm
```

Replace an installed compatibility package with:

```bash
sudo dnf swap freelens-bundled rpm-results/freelens-native-*.x86_64.rpm
```

This is a proof of concept rather than a fully Fedora-unbundled package. The
application still carries its JavaScript dependency tree. The pinned kubectl,
Helm, and Kubernetes proxy executables are built and updated independently in
the sibling `freelens-native-tools` package.

Planned payload reductions are tracked in [ROADMAP.md](ROADMAP.md).
