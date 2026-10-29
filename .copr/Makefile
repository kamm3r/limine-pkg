# COPR make-srpm entry point for the pinned Omadora pair and local RPM recipes.

spec ?= packaging/rpm/omarchy/omarchy.spec
outdir ?= $(CURDIR)/srpm

.PHONY: srpm
srpm:
	@set -e; \
	command -v git >/dev/null || dnf -y install git; \
	spec='$(spec)'; \
	case "$$spec" in \
	  packages/limine-dracut/limine-dracut.spec) \
	    command -v rpmbuild >/dev/null || dnf -y install rpm-build; \
	    mkdir -p '$(outdir)'; \
	    tar -czf '$(outdir)/limine-dracut-0.2.0.tar.gz' --transform='s,^,limine-dracut-0.2.0/,' -C packages/limine-dracut/helpers .; \
	    rpmbuild -bs --define '_sourcedir $(abspath $(outdir))' --define '_srcrpmdir $(abspath $(outdir))' packages/limine-dracut/limine-dracut.spec; \
	    exit 0 ;; \
	  packages/*/*.spec | */packages/*/*.spec) \
	    name=$$(basename "$$spec" .spec); \
	    recipe="$(CURDIR)/packages/$$name/$$name.spec"; \
	    checksum="$(CURDIR)/packages/$$name/sources.sha256"; \
	    if [ ! -f "$$recipe" ] || [ ! -f "$$checksum" ]; then \
	      echo "Unknown Omadora package spec: $$spec" >&2; exit 1; \
	    fi; \
	    command -v spectool >/dev/null && command -v rpmbuild >/dev/null || dnf -y install rpmdevtools rpm-build; \
	    mkdir -p '$(outdir)'; \
	    cp "$$recipe" '$(outdir)/'; \
	    spectool -g -C '$(outdir)' "$(outdir)/$$name.spec"; \
	    if [ -s "$$checksum" ]; then (cd '$(outdir)' && sha256sum -c "$$checksum"); fi; \
	    if [ -f "$(CURDIR)/packages/$$name/cargo-vendor" ]; then \
	      command -v cargo >/dev/null || dnf -y install cargo; \
	      version=$$(rpmspec -q --srpm --qf '%{VERSION}' "$$recipe"); \
	      vendor_root="$$name-$$version"; \
	      if [ -s "$(CURDIR)/packages/$$name/cargo-vendor" ]; then \
	        vendor_root=$$(sed "s/%version/$$version/g" "$(CURDIR)/packages/$$name/cargo-vendor"); \
	      fi; \
	      vendor_tmp=$$(mktemp -d); \
	      trap 'rm -rf "$$vendor_tmp"' EXIT; \
	      tar -xzf "$(outdir)/$$name-$$version.tar.gz" -C "$$vendor_tmp"; \
	      if [ -f "$(CURDIR)/packages/$$name/vendor-prep" ]; then \
	        (cd "$$vendor_tmp/$$vendor_root" && sh "$(CURDIR)/packages/$$name/vendor-prep" "$(abspath $(outdir))"); \
	      fi; \
	      (cd "$$vendor_tmp/$$vendor_root" && \
	        mkdir -p .cargo && \
	        cargo vendor --locked --versioned-dirs cargo-vendor >.cargo/config.toml && \
	        tar -czf "$(abspath $(outdir))/$$name-vendor-$$version.tar.gz" cargo-vendor .cargo); \
	    fi; \
	    if [ -f "$(CURDIR)/packages/$$name/go-vendor" ]; then \
	      command -v go >/dev/null || dnf -y install golang; \
	      version=$$(rpmspec -q --srpm --qf '%{VERSION}' "$$recipe"); \
	      vendor_root="$$name-$$version"; \
	      if [ -s "$(CURDIR)/packages/$$name/go-vendor" ]; then \
	        vendor_root=$$(sed "s/%version/$$version/g" "$(CURDIR)/packages/$$name/go-vendor"); \
	      fi; \
	      vendor_tmp=$$(mktemp -d); \
	      trap 'rm -rf "$$vendor_tmp"' EXIT; \
	      tar -xzf "$(outdir)/$$name-$$version.tar.gz" -C "$$vendor_tmp"; \
	      if [ ! -d "$$vendor_tmp/$$vendor_root" ]; then \
	        tops=$$(ls -1 "$$vendor_tmp" | wc -l); \
	        if [ "$$tops" = "1" ]; then vendor_root=$$(ls -1 "$$vendor_tmp"); fi; \
	      fi; \
	      (cd "$$vendor_tmp/$$vendor_root" && \
	        GOTOOLCHAIN=auto go mod vendor && \
	        tar -czf "$(abspath $(outdir))/$$name-vendor-$$version.tar.gz" vendor); \
	    fi; \
	    rpmbuild -bs --define '_sourcedir $(abspath $(outdir))' --define '_srcrpmdir $(abspath $(outdir))' "$(outdir)/$$name.spec"; \
	    exit 0 ;; \
	  *) echo "Unknown Omadora package spec: $$spec" >&2; exit 1 ;; \
	esac; \
	:
