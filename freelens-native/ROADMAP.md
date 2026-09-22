# freelens-native roadmap

## Kubernetes tools subpackage

`freelens-native-tools` contains the three upstream helper executables which
were previously installed in `freelens-native`:

- `kubectl` (about 60 MB)
- `helm` (about 64 MB)
- `freelens-k8s-proxy` (about 28 MB)

Together they account for about 151 MB. Keeping them in a distinct RPM lets us
update their pinned versions without rebuilding the FreeLens application. The
base package currently requires the tools package to retain the upstream
out-of-the-box experience.

The native build uses the Electron 41 RPM payload as Electron Builder's input,
so it does not download a second Electron archive just to discard it.

Future work can make the tools dependency optional after verifying the
settings and fallback behavior for each tool. Helm can use Fedora's `helm`
package, kubectl may be managed by the user or a future Fedora package, and
the FreeLens Kubernetes proxy has no current system-package replacement.

## Deferred payload and build-time work

- The production RPM excludes `static/build/license.txt`, because Electron
  Builder's `dir` target does not consume the AppImage/Flatpak/Snap license
  payload. FreeLens still generates the file during `build:resources`; patch
  that task to retain tray-icon generation while skipping license generation.
  This reduces build work but does not further reduce the installed RPM.
- Re-inventory the largest remaining ASAR directories before any later size
  reduction. Only remove package metadata or assets whose runtime path is
  demonstrated unused.
- Do not remove bundled `pnpm` merely to reduce size. FreeLens launches it at
  runtime for extension install/remove. A future optional extension-management
  subpackage could carry it, but would make that user-facing feature conditional
  and needs separate integration testing.
