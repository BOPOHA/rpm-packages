PACKAGE_NAME := electron41
SPEC := electron41.spec
RPM_VERSION := $(shell rpmspec -q --srpm --qf '%{Version}-%{Release}' $(SPEC))
FEDORA_VERSION := $(shell rpm -E %fedora)
RPM := rpm-results/$(PACKAGE_NAME)-$(RPM_VERSION).x86_64.rpm
RPMLINT_REPORT := rpm-results/rpmlint.report.txt
SOURCE_ARCHIVE := electron41-source-$(shell rpmspec -q --srpm --qf '%{Version}' $(SPEC)).tar.zst
ARTIFACT ?= /mnt/artifacts/electron41/$(SOURCE_ARCHIVE)
# An SRPM embeds the 7+ GiB source archive, so /tmp (often a small tmpfs) and
# the read-only artifact mount are unsuitable.
PROJECTTMPDIR ?= /mnt/fast/$(PACKAGE_NAME)-rpmbuild

.PHONY: srpm build fc rpmlint stage-source clean

stage-source:
	test -f "$(ARTIFACT)"
	test -f "$(ARTIFACT).sha256"
	cd "$(dir $(ARTIFACT))" && sha256sum -c "$(notdir $(ARTIFACT)).sha256"
	rm -f "$(SOURCE_ARCHIVE)"
	cp --reflink=auto "$(ARTIFACT)" "$(SOURCE_ARCHIVE)"

srpm: stage-source
	rm -rf $(PROJECTTMPDIR)
	mkdir -p $(PROJECTTMPDIR)
	rpmbuild -bs --define "_sourcedir $(CURDIR)" --define "_srcrpmdir $(PROJECTTMPDIR)" $(SPEC)
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
	rm -rf $(PROJECTTMPDIR) rpm-results $(SOURCE_ARCHIVE)
