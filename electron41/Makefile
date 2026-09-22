PACKAGE_NAME := electron41
SPEC := electron41.spec
RPM_VERSION := $(shell rpmspec -q --srpm --qf '%{Version}-%{Release}' $(SPEC))
FEDORA_VERSION := $(shell rpm -E %fedora)
RPM := rpm-results/$(PACKAGE_NAME)-$(RPM_VERSION).x86_64.rpm
RPMLINT_REPORT := rpm-results/rpmlint.report.txt
SOURCE_ARCHIVE := electron41-source-$(shell rpmspec -q --srpm --qf '%{Version}' $(SPEC)).tar.zst
SOURCE_CHECKSUM := $(SOURCE_ARCHIVE).sha256
ARTIFACT ?= /mnt/artifacts/electron41/$(SOURCE_ARCHIVE)
# An SRPM embeds the 7+ GiB source archive, so /tmp (often a small tmpfs) and
# the read-only artifact mount are unsuitable.
PROJECTTMPDIR ?= /mnt/fast/$(PACKAGE_NAME)-rpmbuild

.PHONY: srpm build fc rpmlint stage-source clean

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

stage-source:
	test -f "$(ARTIFACT)"
	test -f "$(SOURCE_CHECKSUM)"
	expected_hash="$$(awk 'NF >= 2 && $$2 == "$(SOURCE_ARCHIVE)" { print $$1 }' "$(SOURCE_CHECKSUM)")"; \
		test -n "$$expected_hash"; \
		printf '%s  %s\n' "$$expected_hash" "$(ARTIFACT)" | sha256sum -c -
	rm -f "$(SOURCE_ARCHIVE)"
	cp --reflink=auto "$(ARTIFACT)" "$(SOURCE_ARCHIVE)"

srpm: stage-source
	$(remove_project_tmpdir)
	mkdir -p "$(PROJECTTMPDIR)"
	rpmbuild -bs --define "_sourcedir $(CURDIR)" --define "_srcrpmdir $(PROJECTTMPDIR)" "$(SPEC)"
	@echo "SRPM: $(PROJECTTMPDIR)/$(PACKAGE_NAME)-$(RPM_VERSION).src.rpm"

fc: srpm
	mkdir -p rpm-results
	mock --no-clean --enable-network -r fedora-$(FEDORA_VERSION)-x86_64 --resultdir=rpm-results $(PROJECTTMPDIR)/$(PACKAGE_NAME)-$(RPM_VERSION).src.rpm
	$(MAKE) rpmlint

build: fc

rpmlint:
	rpmlint $(RPM) > $(RPMLINT_REPORT)
	@echo "rpmlint report: $(RPMLINT_REPORT)"

clean:
	$(remove_project_tmpdir)
	rm -rf -- rpm-results "$(SOURCE_ARCHIVE)"
