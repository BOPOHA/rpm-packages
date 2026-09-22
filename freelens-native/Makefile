PACKAGE_NAME := freelens-native
SPEC := freelens-native.spec
ARCH := x86_64
RPM_VERSION := $(shell rpmspec -q --srpm --qf '%{Version}-%{Release}' $(SPEC))
FEDORA_VERSION := $(shell rpm -E %fedora)
PROJECTTMPDIR := /tmp/$(PACKAGE_NAME)
RPM := rpm-results/$(PACKAGE_NAME)-$(RPM_VERSION).$(ARCH).rpm
SOURCE := freelens-$(shell rpmspec -q --srpm --qf '%{Version}' $(SPEC)).tar.gz
RPMLINT_CONFIG := rpmlint.toml
RPMLINT_REPORT := rpmlint.report.txt
# The Electron runtime is an internal, locally built dependency for now. Mock
# installs these RPMs before resolving BuildRequires, so Electron Builder can
# use the RPM payload rather than fetching an upstream archive.
ELECTRON_RPM_DIR ?= /home/user/rpmbuild/RPMS/$(ARCH)
ELECTRON_RPMS := $(sort $(wildcard $(ELECTRON_RPM_DIR)/electron41-*.rpm))

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
	@test -n "$(ELECTRON_RPMS)" || (echo "electron41 RPMs not found in $(ELECTRON_RPM_DIR); set ELECTRON_RPM_DIR" >&2; exit 1)
	mkdir -p rpm-results
	mock --no-clean --enable-network \
		-r fedora-$(FEDORA_VERSION)-$(ARCH) \
		--install $(ELECTRON_RPMS)
	mock --no-clean --enable-network \
		-r fedora-$(FEDORA_VERSION)-$(ARCH) \
		--resultdir=rpm-results \
		$(PROJECTTMPDIR)/$(PACKAGE_NAME)-$(RPM_VERSION).src.rpm
	$(MAKE) rpmlint

rpmlint:
	rpmlint --config $(RPMLINT_CONFIG) $(RPM) > $(RPMLINT_REPORT)
	@echo "rpmlint report: $(RPMLINT_REPORT)"

clean:
	rm -rf $(PROJECTTMPDIR) rpm-results $(SOURCE)
