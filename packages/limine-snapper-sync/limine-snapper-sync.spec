%global debug_package %{nil}

Name:           limine-snapper-sync
Version:        1.32.1
Release:        2%{?dist}
Summary:        Integrates Limine boot entries with Snapper snapshots
License:        GPL-3.0-or-later
URL:            https://gitlab.com/Zesko/limine-snapper-sync
Source0:        %{url}/-/archive/%{version}/%{name}-%{version}.tar.gz#/%{name}-%{version}.tar.gz
ExclusiveArch:  x86_64 aarch64
# Upstream builds a GraalVM native image with Gradle 9.7.1 plus GraalVM CE
# JDK 25.0.2. Bundle Gradle because Fedora 44 has no Gradle RPM. The GraalVM
# bootstrap tarball is fetched in %%build, mirroring the PKGBUILD
# source_x86_64/source_aarch64 entries.
BuildRequires:  unzip
BuildRequires:  gettext
%global gradle_version 9.7.1
Source1:        https://services.gradle.org/distributions/gradle-%{gradle_version}-bin.zip
BuildRequires:  java-25-openjdk-devel
BuildRequires:  gcc
BuildRequires:  curl
BuildRequires:  systemd-rpm-macros
BuildRequires:  glibc-devel
BuildRequires:  zlib-devel
# Runtime follows the PKGBUILD depends plus a dracut-compatible boot stack:
# dracut provides initramfs images (Omadora builds them via dracut and
# registers kernels through kernel-install's 96-limine.install, see FEDORA.md),
# so there is deliberately no limine-mkinitcpio-hook Requirement.
Requires:       bash
Requires:       limine
Requires:       snapper
Requires:       btrfs-progs
Requires:       libnotify
Requires:       dracut
Requires:       systemd
# Upstream optdepends mapped to weak deps: inotify-tools backs the watcher
# fallback, rsync is one restore method, b3sum/xxhash are hash choices.
Recommends:     inotify-tools
Recommends:     rsync
Recommends:     b3sum
Recommends:     xxhash

%description
Limine-Snapper-Sync synchronizes snapshot boot entries with Btrfs snapshots,
updating the Limine bootloader configuration when Snapper snapshots are
created, deleted, or restored.

%prep
%autosetup
# Native-image otherwise sizes its heap and thread pool from the entire host.
# Keep the compiler within the memory available on standard COPR builders.
sed -i '/buildArgs.add("-Os")/a\            buildArgs.add("-J-Xmx3g")\n            buildArgs.add("--parallelism=2")' build.gradle.kts

%build
# Bootstrap the exact GraalVM CE JDK the upstream PKGBUILD pins, since Fedora
# ships no GraalVM 25 native-image toolchain. URLs and hashes mirror the
# PKGBUILD source_x86_64/source_aarch64 entries. Use the same verified Gradle
# distribution on both architectures.
if [[ "%{_arch}" == "x86_64" ]]; then
  graal_url="https://github.com/graalvm/graalvm-ce-builds/releases/download/jdk-25.0.2/graalvm-community-jdk-25.0.2_linux-x64_bin.tar.gz"
  graal_sha="e0be791c8fda4d03b6b0a0cb824fef3149736170057b3a515252b44419606af0"
else
  graal_url="https://github.com/graalvm/graalvm-ce-builds/releases/download/jdk-25.0.2/graalvm-community-jdk-25.0.2_linux-aarch64_bin.tar.gz"
  graal_sha="b4580d9f223d0a4b3a1757e58b18ff4c1db950e67e105fc5cb741457d2384a71"
fi
curl -fsSL "$graal_url" -o graalvm.tar.gz
echo "$graal_sha  graalvm.tar.gz" | sha256sum -c -
rm -rf graalvm_ce_jdk25
mkdir graalvm_ce_jdk25
tar -xzf graalvm.tar.gz -C graalvm_ce_jdk25 --strip-components=1
export GRAALVM_HOME="$PWD/graalvm_ce_jdk25"
export JAVA_HOME="$GRAALVM_HOME"
export NATIVE_IMAGE_OPTIONS="-march=compatibility"
unzip -q %{SOURCE1}
./gradle-%{gradle_version}/bin/gradle --no-daemon --max-workers=4 clean nativeCompile -Dorg.gradle.java.home="${JAVA_HOME}"

%install
# Native binary built above.
install -D -m 0755 build/native/nativeCompile/limine-snapper-sync %{buildroot}%{_prefix}/lib/limine/limine-snapper-sync
# Shell wrappers, mutex library, snapper plugin, systemd units, config, and
# desktop assets from the upstream install/arch-linux tree. The
# usr/share/libalpm hook and script are Arch-only (dnf has no libalpm;
# kernel add/remove is handled by kernel-install's 96-limine.install) and
# are intentionally dropped.
src="install/arch-linux"
install -d %{buildroot}%{_bindir} %{buildroot}%{_prefix}/lib/limine %{buildroot}%{_prefix}/lib/snapper/plugins
install -m 0755 "$src/usr/bin/"* %{buildroot}%{_bindir}/
install -m 0644 "$src/usr/lib/limine/limine-mutex" %{buildroot}%{_prefix}/lib/limine/limine-mutex
install -m 0755 "$src/usr/lib/snapper/plugins/10-limine-snapper-sync" %{buildroot}%{_prefix}/lib/snapper/plugins/10-limine-snapper-sync
install -D -m 0644 "$src/usr/lib/systemd/system/limine-snapper-sync.service" %{buildroot}%{_unitdir}/limine-snapper-sync.service
install -D -m 0644 "$src/usr/lib/systemd/system/snapper-cleanup.service.d/limine-snapper-override.conf" %{buildroot}%{_unitdir}/snapper-cleanup.service.d/limine-snapper-override.conf
install -D -m 0644 "$src/etc/limine-snapper-sync.conf" %{buildroot}%{_sysconfdir}/limine-snapper-sync.conf
install -D -m 0644 "$src/etc/xdg/autostart/limine-snapper-notify.desktop" %{buildroot}%{_sysconfdir}/xdg/autostart/limine-snapper-notify.desktop
install -D -m 0644 "$src/etc/xdg/autostart/limine-restore-notify.desktop" %{buildroot}%{_sysconfdir}/xdg/autostart/limine-restore-notify.desktop
install -D -m 0644 "$src/usr/share/applications/limine-snapper-restore.desktop" %{buildroot}%{_datadir}/applications/limine-snapper-restore.desktop
install -D -m 0644 "$src/usr/share/icons/hicolor/128x128/apps/LimineSnapperSync.png" %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/LimineSnapperSync.png
if [ -d "$src/usr/share/locale" ]; then
  cp -a "$src/usr/share/locale" %{buildroot}%{_datadir}/
fi
install -d %{buildroot}%{_docdir}/%{name}
install -m 0644 README.md CHANGELOG.md %{buildroot}%{_docdir}/%{name}/

%files
%license LICENSE
%doc %{_docdir}/%{name}/README.md
%doc %{_docdir}/%{name}/CHANGELOG.md
%config(noreplace) %{_sysconfdir}/limine-snapper-sync.conf
%{_sysconfdir}/xdg/autostart/limine-snapper-notify.desktop
%{_sysconfdir}/xdg/autostart/limine-restore-notify.desktop
%{_bindir}/limine-snapper-info
%{_bindir}/limine-snapper-list
%{_bindir}/limine-snapper-notify
%{_bindir}/limine-snapper-remove
%{_bindir}/limine-snapper-restore
%{_bindir}/limine-snapper-sync
%{_bindir}/limine-snapper-watcher
%{_prefix}/lib/limine/limine-snapper-sync
%{_prefix}/lib/limine/limine-mutex
%{_prefix}/lib/snapper/plugins/10-limine-snapper-sync
%{_unitdir}/limine-snapper-sync.service
%{_unitdir}/snapper-cleanup.service.d/limine-snapper-override.conf
%{_datadir}/applications/limine-snapper-restore.desktop
%{_datadir}/icons/hicolor/128x128/apps/LimineSnapperSync.png
%{_datadir}/locale/*/LC_MESSAGES/limine-snapper-sync.mo

%changelog
* Tue Oct 06 2026 kamm3r - 1.32.1-1
- Update to the release pinned on upstream master.
- Bundle upstream Gradle because Fedora 44 has no Gradle RPM.
- Limit native-image resources and include compiled translations.

* Sat Oct 03 2026 kamm3r - 1.32.0-2
- Declare the GraalVM download tool and systemd path macros.

* Wed Sep 30 2026 kamm3r - 1.32.0-1
- Port the upstream Omarchy recipe to Fedora (dracut boot stack, no ALPM hooks).
