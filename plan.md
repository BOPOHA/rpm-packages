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
  built RPM components wherever practical, beginning with a compatible Electron
  runtime and then the Kubernetes helpers and native Node modules.

They must not be co-installable: both own the `freelens` command, desktop ID,
configuration location, and application data. `freelens-bundled` provides the
unqualified `freelens` capability and obsoletes older unqualified packages so
that RPM-installed GitHub releases migrate transactionally. Both variants
declare reciprocal `Conflicts:` by their exact package names.

Use package-local build commands such as `cd freelens-bundled && make fc` and,
once its spec exists, `cd freelens-native && make fc`. Each package produces a
distinct SRPM/binary RPM and rpmlint report. Do not call the native variant
equivalent until its phase-specific tests pass.

## Phase 1: low-risk cleanup — implemented

- Use Fedora's `vulkan-loader` (`libvulkan.so.1`) instead of Electron's bundled
  Vulkan loader.
- Remove `@electron-internal/extract-zip` native add-ons that do not match the
  RPM's Linux architecture. Keep only the glibc add-on for the target arch.
- Retain the Electron graphics stack, native Node modules, and Kubernetes
  helpers for now.

Validation: run `make fc`, install the RPM in a test environment, and start
Freelens with both GPU acceleration and `--disable-gpu` to verify startup.

## Phase 2: Fedora Electron runtime — current priority

- Fedora 44 currently has no `electron` or `electron-devel` package in the
  enabled repositories, while Freelens 1.10.3 requires Electron 41.10.0.
- The `electron41.spec` bootstrap provides parallel-installable `electron41`
  and `electron41-devel` packages.
- Audit Electron's generated Chromium third-party notice before publication;
  the initial aggregate license expression deliberately does not claim the
  runtime is MIT-only.
- Do not substitute individual Chromium private libraries; the native variant
  must use a whole compatible system Electron runtime.

### Recommended delivery decision

Use a prepared, immutable `linux-x86_64` Electron build-input artifact as the
temporary solution. A dedicated large machine runs the pinned Electron checkout
and `gclient sync` with hooks once per Electron update, then publishes a
compressed archive, SHA-256 checksum, `SOURCE-MANIFEST.json`, and
`GCLIENT-REVINFO.txt` to controlled object storage. The RPM build downloads or
uses that declared `Source` artifact, unpacks it, and performs GN/Ninja only;
it must not invoke `gclient` in Mock. This makes ordinary Mock/COPR builds
independent of the 80+ GiB dependency synchronization while retaining the
complete exact input set.

The current `create-source-artifact.sh` implements the producer side. Its
workspace is deliberately persistent and idempotent: a Git object cache and a
completion stamp reuse completed downloads and skip `gclient` on subsequent
runs. The artifact is a prepared build input, not pure source: Electron hooks
can download platform-specific CIPD/GCS payloads. Publish one artifact per
host/target architecture and retain its provenance and license records.

Pros: fast repeatable RPM builds, no networked dependency resolver in `%build`,
and a practical route to a working Electron 41 runtime. Cons: a very large
internal artifact, continued bundled Chromium dependencies, architecture-
specific inputs, and it is not sufficient for a Fedora-reviewable package.

### Long-term Fedora-quality path

Arch Linux's Electron 41 package is the reference approach to evaluate rather
than copy wholesale. It parses Electron `DEPS` into roughly 158 individually
pinned Git sources, reconstructs the source tree, selectively reproduces
required hooks, uses system toolchains/libraries, and carries compatibility
patches for its current toolchain. A Fedora port would need an RPM-oriented
source-roller/lockfile, explicit handling of needed CIPD/GCS artifacts,
Fedora-specific compiler/Rust/GN settings, library unbundling work, and tested
downstream patches. Do this only after the temporary artifact-backed runtime is
validated.

Immediate implementation guardrails:

- Support `x86_64` first. Do not advertise `aarch64` until it has its own
  prepared artifact and installed-RPM validation.
- Set Fedora toolchain and GN policy explicitly (`use_sysroot=false`, suitable
  PGO policy, compiler/Rust locations) instead of relying on downloaded
  Chromium defaults.
- Add the missing compiler, linker, Rust, Java, GN/Ninja, Node/Yarn, and
  system-library build requirements as actual build failures establish them.
- Port Arch/Gentoo/NixOS patches only when they are applicable to the Fedora
  toolchain; do not copy them as an unreviewed bundle.

Validation: reproducible Electron RPM build, then Freelens startup under that
runtime with GPU, software rendering, Wayland/X11, terminal, and extensions.

## Phase 3: Kubernetes helper packages — deferred

- Build `freelens-k8s-proxy` from source inside `freelens-native`.
- Use Fedora Helm 4.2.2 and Kubernetes 1.36 client packages via controlled
  resource-path symlinks in `freelens-native`. Keep the bundled variant's
  pinned resources unchanged.

Validation: cluster connection, kubectl operations, Helm repository/chart/
release operations, and proxy-backed features against supported Kubernetes
versions.

## Phase 4: native Node add-ons

- Build `node-pty` and `@electron-internal/extract-zip` from source for the
  Electron ABI used by the native variant.
- Add the required compiler, Node/Electron headers, and reproducibility checks.

Validation: terminal/exec sessions, archive extraction, and a clean rebuild in
Mock for every supported architecture.

## Phase 5: native variant integration

- Patch the native build to use the validated system Electron runtime and its
  compatible library set; do not substitute individual Chromium private
  libraries piecemeal.
- Remove the upstream Electron ZIP and its bundled Chromium graphics/codec
  libraries from the native RPM only after the system-Electron build is proven.

Validation: full UI smoke test, GPU and software rendering, Wayland/X11,
terminal support, extensions, and update the RPM dependency/provides policy.

## Phase 6: maintenance policy

- Keep every remaining external artifact source-versioned and independently
  verifiable.
- Require Mock builds and installed-RPM smoke tests for each Freelens, Electron,
  or Kubernetes-helper update.
