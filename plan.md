# Freelens RPM unbundling plan

## Goal

Move from the upstream Electron bundle toward a Fedora-native package without
unverified third-party executable payloads. Each phase must retain a working
Freelens installation on the supported Fedora target before the next starts.

## Package variants

Maintain two mutually exclusive RPM variants from the same source and release:

- `freelens-bundled` is the compatibility package. It follows the upstream
  Electron build and retains its bundled Electron/Chromium runtime and helper
  executables, apart from low-risk cleanup already proven safe. It is the
  fallback and the package to use when upstream-version compatibility matters.
- `freelens-native` is the Fedora-native package. It uses system or separately
  built RPM components wherever practical, beginning with Vulkan and then the
  Kubernetes helpers, native Node modules, and Electron itself.

They must not be co-installable: both own the `freelens` command, desktop ID,
configuration location, and application data. Each variant should `Provides:
freelens`, and declare reciprocal `Conflicts:` (with a deliberate upgrade path
using `Obsoletes:` only if the current unqualified package name is retired).

Use explicit build targets such as `make fc-bundled` and `make fc-native`, each
producing a distinct SRPM/binary RPM and rpmlint report. Do not call the native
variant equivalent until its phase-specific tests pass.

## Phase 1: low-risk cleanup — implemented

- Use Fedora's `vulkan-loader` (`libvulkan.so.1`) instead of Electron's bundled
  Vulkan loader.
- Remove `@electron-internal/extract-zip` native add-ons that do not match the
  RPM's Linux architecture. Keep only the glibc add-on for the target arch.
- Retain the Electron graphics stack, native Node modules, and Kubernetes
  helpers for now.

Validation: run `make fc`, install the RPM in a test environment, and start
Freelens with both GPU acceleration and `--disable-gpu` to verify startup.

## Phase 2: Kubernetes helper packages

- Package `freelens-k8s-proxy` from source as its own RPM.
- Evaluate Fedora `kubectl` and Helm packages against Freelens' pinned
  compatibility expectations.
- Patch the native variant or supply controlled resource-path symlinks only
  after proving its supported operations work with system tools. Keep the
  bundled variant's pinned resources unchanged.

Validation: cluster connection, kubectl operations, Helm repository/chart/
release operations, and proxy-backed features against supported Kubernetes
versions.

## Phase 3: native Node add-ons

- Build `node-pty` and `@electron-internal/extract-zip` from source for the
  Electron ABI used by the native variant.
- Add the required compiler, Node/Electron headers, and reproducibility checks.

Validation: terminal/exec sessions, archive extraction, and a clean rebuild in
Mock for every supported architecture.

## Phase 4: Electron runtime transition

- Determine whether the Fedora Electron version can support Freelens' required
  Electron/Node APIs and Chromium behavior.
- Patch only the native build to use the system Electron and its compatible
  library set; do not substitute individual Chromium private libraries
  piecemeal.
- Remove the upstream Electron ZIP and its bundled Chromium graphics/codec
  libraries from the native RPM only after the system-Electron build is proven.

Validation: full UI smoke test, GPU and software rendering, Wayland/X11,
terminal support, extensions, and update the RPM dependency/provides policy.

## Phase 5: maintenance policy

- Keep every remaining external artifact source-versioned and independently
  verifiable.
- Require Mock builds and installed-RPM smoke tests for each Freelens, Electron,
  or Kubernetes-helper update.
