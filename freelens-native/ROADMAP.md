# freelens-native roadmap

## Optional Kubernetes tools subpackage

Create a `freelens-native-tools` package containing the three upstream helper
executables currently installed in `freelens-native`:

- `kubectl` (about 60 MB)
- `helm` (about 64 MB)
- `freelens-k8s-proxy` (about 28 MB)

Together they account for about 151 MB of the current 325 MB installed native
package. The base package should be able to use system or user-configured
tools, while `freelens-native-tools` preserves the upstream out-of-the-box
experience for users who want the pinned helper versions.

Before splitting, verify the FreeLens settings and fallback behavior for each
tool. In particular, Helm can use Fedora's `helm` package, kubectl may be
managed by the user or a future Fedora package, and the FreeLens Kubernetes
proxy has no current system-package replacement.
