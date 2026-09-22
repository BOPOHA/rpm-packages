PACKAGE_NAME := freelens-bundled
SPEC := freelens.spec
PROJECTTMPDIR := /tmp/$(PACKAGE_NAME)
RPM_VERSION := $(shell rpmspec -q --srpm --qf '%{Version}-%{Release}' $(SPEC))
FEDORA_VERSION := $(shell rpm -E %fedora)
RPM := rpm-results/$(PACKAGE_NAME)-$(RPM_VERSION).x86_64.rpm
RPMLINT_CONFIG := rpmlint.toml
RPMLINT_REPORT := rpmlint.report.txt

.PHONY: srpm fc rpmlint clean

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

srpm:
	$(remove_project_tmpdir)
	mkdir -p "$(PROJECTTMPDIR)"
	spectool --get-files --directory $(PROJECTTMPDIR) $(SPEC)
	rpkg srpm --spec $(SPEC) --outdir $(PROJECTTMPDIR)
	@echo "SRPM: $(PROJECTTMPDIR)/$(PACKAGE_NAME)-$(RPM_VERSION).src.rpm"

fc: srpm
	mock --no-clean --enable-network -r fedora-$(FEDORA_VERSION)-x86_64 --resultdir=rpm-results $(PROJECTTMPDIR)/$(PACKAGE_NAME)-$(RPM_VERSION).src.rpm
	$(MAKE) rpmlint

rpmlint:
	rpmlint --config $(RPMLINT_CONFIG) $(RPM) > $(RPMLINT_REPORT)
	@echo "rpmlint report: $(RPMLINT_REPORT)"

clean:
	$(remove_project_tmpdir)
	rm -rf -- rpm-results
