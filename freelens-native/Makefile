PACKAGE_NAME := freelens-native
SPEC := freelens-native.spec
RPM_VERSION := $(shell rpmspec -q --srpm --qf '%{Version}-%{Release}' $(SPEC))
FEDORA_VERSION := $(shell rpm -E %fedora)
PROJECTTMPDIR := /tmp/$(PACKAGE_NAME)
RPM := rpm-results/$(PACKAGE_NAME)-$(RPM_VERSION).x86_64.rpm
SOURCE := freelens-$(shell rpmspec -q --srpm --qf '%{Version}' $(SPEC)).tar.gz
RPMLINT_CONFIG := rpmlint.toml
RPMLINT_REPORT := rpmlint.report.txt

.PHONY: srpm fc rpmlint clean

$(SOURCE):
	spectool --get-files --directory . $(SPEC)

srpm: $(SOURCE)
	rm -rf $(PROJECTTMPDIR)
	mkdir -p $(PROJECTTMPDIR)
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
	rm -rf $(PROJECTTMPDIR) rpm-results $(SOURCE)
