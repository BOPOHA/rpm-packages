# freelens-native RPM packaging

`freelens-native` is the thin FreeLens package. It contains the FreeLens
application, its native Node add-ons, and its pinned Kubernetes helper tools,
but it does not contain Electron or Chromium. It runs with the separately
installed `electron41` RPM.

FreeLens 1.10.3 pins Electron 41.10.0. The RPM therefore requires Electron
41.10.0 or newer within major version 41. The packages `freelens-native` and
`freelens-bundled` are mutually exclusive because both provide the `freelens`
command and desktop integration.

## Build on Fedora

```bash
make fc
```

The build downloads the pinned upstream source and JavaScript dependencies in
a Fedora Mock chroot. Electron Builder is used to assemble the application,
but only `resources/app.asar`, its unpacked native modules, and FreeLens's
Kubernetes helper programs are copied into the RPM. The downloaded Electron
runtime is not included.

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
application still carries its JavaScript dependency tree and the upstream
kubectl, Helm, and Kubernetes proxy executables.

Planned payload reductions are tracked in [ROADMAP.md](ROADMAP.md).
