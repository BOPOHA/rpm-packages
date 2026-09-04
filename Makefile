PROJECTNAME := $(notdir $(CURDIR))
SPEC := freelens.spec
PROJECTTMPDIR := /tmp/$(PROJECTNAME)
RPM_VERSION := $(shell rpmspec -q --srpm --qf '%{Version}-%{Release}' $(SPEC))
FEDORA_VERSION := $(shell rpm -E %fedora)

.PHONY: srpm fc clean

srpm:
	rm -rf $(PROJECTTMPDIR)
	mkdir -p $(PROJECTTMPDIR)
	spectool --get-files --directory $(PROJECTTMPDIR) $(SPEC)
	rpkg srpm --spec $(SPEC) --outdir $(PROJECTTMPDIR)
	@echo "SRPM: $(PROJECTTMPDIR)/freelens-$(RPM_VERSION).src.rpm"

fc: srpm
	mock --no-clean --dnf --enable-network -r fedora-$(FEDORA_VERSION)-x86_64 --resultdir=rpm-results $(PROJECTTMPDIR)/freelens-$(RPM_VERSION).src.rpm

clean:
	rm -rf $(PROJECTTMPDIR) rpm-results
