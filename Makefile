PROJECTNAME := $(notdir $(CURDIR))
PACKAGE_NAME := freelens-bundled
SPEC := freelens.spec
PROJECTTMPDIR := /tmp/$(PROJECTNAME)
RPM_VERSION := $(shell rpmspec -q --srpm --qf '%{Version}-%{Release}' $(SPEC))
FEDORA_VERSION := $(shell rpm -E %fedora)
RPM := rpm-results/$(PACKAGE_NAME)-$(RPM_VERSION).x86_64.rpm
ELECTRON41_PACKAGE_NAME := electron41
ELECTRON41_SPEC := electron41.spec
ELECTRON41_PROJECTTMPDIR := /tmp/$(PROJECTNAME)-electron41
ELECTRON41_RPM_VERSION := $(shell rpmspec -q --srpm --qf '%{Version}-%{Release}' $(ELECTRON41_SPEC))
ELECTRON41_RESULTDIR := rpm-results/electron41
ELECTRON41_RPM := $(ELECTRON41_RESULTDIR)/$(ELECTRON41_PACKAGE_NAME)-$(ELECTRON41_RPM_VERSION).x86_64.rpm
RPMLINT_CONFIG := rpmlint.toml
RPMLINT_REPORT := rpmlint.report.txt
ELECTRON41_RPMLINT_REPORT := $(ELECTRON41_RESULTDIR)/rpmlint.report.txt

.PHONY: srpm fc fc-bundled rpmlint electron41-srpm fc-electron41 rpmlint-electron41 clean

srpm:
	rm -rf $(PROJECTTMPDIR)
	mkdir -p $(PROJECTTMPDIR)
	spectool --get-files --directory $(PROJECTTMPDIR) $(SPEC)
	rpkg srpm --spec $(SPEC) --outdir $(PROJECTTMPDIR)
	@echo "SRPM: $(PROJECTTMPDIR)/$(PACKAGE_NAME)-$(RPM_VERSION).src.rpm"

fc: srpm
	mock --no-clean --enable-network -r fedora-$(FEDORA_VERSION)-x86_64 --resultdir=rpm-results $(PROJECTTMPDIR)/$(PACKAGE_NAME)-$(RPM_VERSION).src.rpm
	$(MAKE) rpmlint

fc-bundled: fc

rpmlint:
	rpmlint --config $(RPMLINT_CONFIG) $(RPM) > $(RPMLINT_REPORT)
	@echo "rpmlint report: $(RPMLINT_REPORT)"

electron41-srpm:
	rm -rf $(ELECTRON41_PROJECTTMPDIR)
	mkdir -p $(ELECTRON41_PROJECTTMPDIR)
	spectool --get-files --directory $(ELECTRON41_PROJECTTMPDIR) $(ELECTRON41_SPEC)
	rpkg srpm --spec $(ELECTRON41_SPEC) --outdir $(ELECTRON41_PROJECTTMPDIR)
	@echo "SRPM: $(ELECTRON41_PROJECTTMPDIR)/$(ELECTRON41_PACKAGE_NAME)-$(ELECTRON41_RPM_VERSION).src.rpm"

fc-electron41: electron41-srpm
	mkdir -p $(ELECTRON41_RESULTDIR)
	mock --no-clean --enable-network -r fedora-$(FEDORA_VERSION)-x86_64 --resultdir=$(ELECTRON41_RESULTDIR) $(ELECTRON41_PROJECTTMPDIR)/$(ELECTRON41_PACKAGE_NAME)-$(ELECTRON41_RPM_VERSION).src.rpm
	$(MAKE) rpmlint-electron41

rpmlint-electron41:
	rpmlint --config $(RPMLINT_CONFIG) $(ELECTRON41_RPM) > $(ELECTRON41_RPMLINT_REPORT)
	@echo "rpmlint report: $(ELECTRON41_RPMLINT_REPORT)"

clean:
	rm -rf $(PROJECTTMPDIR) $(ELECTRON41_PROJECTTMPDIR) rpm-results
