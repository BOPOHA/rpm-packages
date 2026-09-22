PACKAGE_NAME := freelens-native-tools
SPEC := freelens-native-tools.spec
RPM_VERSION := $(shell rpmspec -q --srpm --qf '%{Version}-%{Release}' $(SPEC))
FEDORA_VERSION := $(shell rpm -E %fedora)
PROJECTTMPDIR := /tmp/$(PACKAGE_NAME)
RPM := rpm-results/$(PACKAGE_NAME)-$(RPM_VERSION).x86_64.rpm
RPMLINT_CONFIG := rpmlint.toml
RPMLINT_REPORT := rpmlint.report.txt

.PHONY: sources srpm fc rpmlint clean

define remove_project_tmpdir
	@project_tmpdir='$(PROJECTTMPDIR)'; \
	if test -z "$$project_tmpdir"; then \
		echo 'Refusing to remove an empty PROJECTTMPDIR' >&2; exit 1; \
	fi; \
	project_tmpdir="$$(realpath -m -- "$$project_tmpdir")"; \
	case "$$(basename -- "$$project_tmpdir")" in \
		'$(PACKAGE_NAME)'|'$(PACKAGE_NAME)-'*) ;; \
		*) echo "Refusing unsafe PROJECTTMPDIR: $$project_tmpdir" >&2; exit 1 ;; \
	esac; \
	rm -rf -- "$$project_tmpdir"
endef

sources:
	spectool --get-files --directory . $(SPEC)

srpm: sources
	$(remove_project_tmpdir)
	mkdir -p "$(PROJECTTMPDIR)"
	rpmbuild -bs \
		--define "_sourcedir $(CURDIR)" \
		--define "_srcrpmdir $(PROJECTTMPDIR)" \
		$(SPEC)
	@echo "SRPM: $(PROJECTTMPDIR)/$(PACKAGE_NAME)-$(RPM_VERSION).src.rpm"

fc: srpm
	mkdir -p rpm-results
	mock --no-clean --enable-network \
		-r fedora-$(FEDORA_VERSION)-x86_64 \
		--resultdir=rpm-results \
		$(PROJECTTMPDIR)/$(PACKAGE_NAME)-$(RPM_VERSION).src.rpm
	$(MAKE) rpmlint

rpmlint:
	rpmlint --config $(RPMLINT_CONFIG) $(RPM) > $(RPMLINT_REPORT)
	@echo "rpmlint report: $(RPMLINT_REPORT)"

clean:
	$(remove_project_tmpdir)
	rm -rf -- rpm-results \
		kubectl kubectl.sha256 helm-v*.tar.gz helm-v*.tar.gz.sha256sum \
		freelens-k8s-proxy freelens-k8s-proxy.sha256 LICENSE.kubernetes LICENSE.freelens-k8s-proxy
