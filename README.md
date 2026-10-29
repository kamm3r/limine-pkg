# Limine packages for Fedora

Independent RPM packaging for [kammer/limine](https://copr.fedorainfracloud.org/coprs/kammer/limine/), targeting Fedora 44 x86_64. Sources live here rather than in omadora-pkg.

## Packages

- `limine`: upstream 12.9.6 firmware binaries, with the host tool compiled on Fedora. Version 12.9.6 sorts above Terra's 12.9.4 package. No installation script deploys firmware or changes UEFI entries.
- `limine-entry-tool`: upstream 1.40.0 entry management and EFI deployment commands. Gradle and GraalVM downloads are pinned and checked; binary builds require network access for Maven dependencies.
- `limine-snapper-sync`: upstream 1.32.1 snapshot/restore integration, imported from kamm3r/omadora-pkg with its checksum manifest and build history. Fedora wrappers and native binaries use upstream's `/usr/lib/limine` paths.
- `limine-dracut` 0.2.0: Fedora dracut compatibility commands, UKI generation and kernel-install plugins. RPM transaction file triggers replace upstream ALPM triggers for boot-image refresh and EFI deployment. Fedora versioned kernels retain recovery entries while preferring the newest installed version. This is our package name; it is not Arch's mkinitcpio hook package.

Omadora-specific boot-menu defaults, branding, hardware quirks, and Snapper/dracut policy remain in Omadora. The generic integration pins kernel-install to Fedora's `/boot` layout and delegates nonmatching layouts to Fedora's dracut plugin.

## Build

```bash
make -f .copr/Makefile srpm spec=packages/limine/limine.spec outdir=/tmp/limine-srpm
rpmbuild --rebuild /tmp/limine-srpm/*.src.rpm
```

Other recipes use the same `packages/<name>/<name>.spec` convention. The dracut source archive is assembled from the checked-in `helpers/` directory; upstream archives use `sources.sha256`. No source archive is downloaded without checksum validation.

## Existing Omadora installations

Do not switch all packages blindly: existing source-installed `/usr/local/bin/limine-*` commands shadow RPM commands, and unowned `/usr/lib/limine` files may be replaced by RPM payloads. Back up those files and the existing kernel-install configuration before migration. Inventory actual files with `rpm -qf` and compare packaged contents; do not remove a whole directory that might contain other tools.

The existing `/etc/kernel/install.d/96-limine.install` also overrides the packaged `/usr/lib/kernel/install.d/96-limine.install`; retire the old override explicitly after comparison. Review `.rpmnew` files for `/etc/kernel/install.conf` and `/etc/kernel/install.d/50-dracut.install`. Configuration uses `%config(noreplace)`.

Installing these packages does not migrate `/usr/local` files or enable the Snapper service. With `limine-dracut` 0.2.0 and an existing `/etc/default/limine` on a UEFI system, RPM file triggers regenerate configured images and deploy Limine. Review the configuration, ensure sufficient ESP space, and back up boot files before upgrading from the split-image-only 0.1.0 integration. The package requires Fedora's `systemd-boot-unsigned` stub for UKIs. Keep your current working bootloader until validation completes.

## Source provenance

The initial Snapper recipe is from kamm3r/omadora-pkg at `e53038407a3df63ff53ad9429eb5885ab9542e49`. Fedora helper scripts are from kamm3r/omadora (`install/fedora/`) at `becc224a03f1b974aeee61b05e4d34c8cfb21f57`, under the included MIT license, with absolute entry-tool paths updated to `/usr/bin` for RPM installation. Upstream projects retain their own licenses.

The October 28 bootloader update passed local RPM build and version checks. COPR build [11220306](https://copr.fedorainfracloud.org/coprs/build/11220306) succeeded and version 12.9.6-1.fc44 is present in repository metadata. Companion packages remain unchanged.
