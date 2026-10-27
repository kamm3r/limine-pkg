%global debug_package %{nil}
Name:           limine-entry-tool
Version:        1.40.0
Release:        1%{?dist}
Summary:        Boot-entry automation for Limine
License:        GPL-3.0-or-later
URL:            https://gitlab.com/Zesko/limine-entry-tool
Source0:        %{url}/-/archive/%{version}/%{name}-%{version}.tar.gz
%global gradle_version 9.7.1
Source1:        https://services.gradle.org/distributions/gradle-%{gradle_version}-bin.zip
ExclusiveArch:  x86_64
BuildRequires:  unzip gcc curl java-25-openjdk-devel glibc-devel zlib-devel
Requires:       limine >= 8
Requires:       bash coreutils util-linux grep tar efibootmgr

%description
Manage Limine boot entries, kernel command lines, and EFI deployment.
Boot deployment is explicit; installing this RPM does not change the ESP.

%prep
%autosetup
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
# Upstream wrappers use /usr/lib/limine explicitly, even on x86_64.
install -d %{buildroot}%{_prefix}/lib/limine %{buildroot}%{_bindir}
install -m 0755 build/native/nativeCompile/limine-entry-tool %{buildroot}%{_prefix}/lib/limine/
src=install/arch-linux/limine-entry-tool
install -m 0755 "$src/usr/bin/"* %{buildroot}%{_bindir}/
install -m 0644 "$src/usr/lib/limine/"* %{buildroot}%{_prefix}/lib/limine/
install -D -m 0644 "$src/etc/limine-entry-tool.conf" %{buildroot}%{_sysconfdir}/limine-entry-tool.conf
# ALPM deployment hooks are Arch-specific; no implicit EFI deployment here.

%check
%{buildroot}%{_prefix}/lib/limine/limine-entry-tool --version

%files
%license LICENSE
%doc README.md
%config(noreplace) %{_sysconfdir}/limine-entry-tool.conf
%{_bindir}/limine-*
%{_prefix}/lib/limine/limine-entry-tool
%{_prefix}/lib/limine/auth-helper
%{_prefix}/lib/limine/limine-common-functions
