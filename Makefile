PROJECTNAME := $(notdir $(CURDIR))
PACKAGE_NAME := freelens-bundled
SPEC := freelens.spec
PROJECTTMPDIR := /tmp/$(PROJECTNAME)
RPM_VERSION := $(shell rpmspec -q --srpm --qf '%{Version}-%{Release}' $(SPEC))
FEDORA_VERSION := $(shell rpm -E %fedora)
RPM := rpm-results/$(PACKAGE_NAME)-$(RPM_VERSION).x86_64.rpm
RPMLINT_CONFIG := rpmlint.toml
RPMLINT_REPORT := rpmlint.report.txt

.PHONY: srpm fc rpmlint clean

srpm:
	rm -rf $(PROJECTTMPDIR)
	mkdir -p $(PROJECTTMPDIR)
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
	rm -rf $(PROJECTTMPDIR) rpm-results
