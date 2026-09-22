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
