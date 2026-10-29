Name:           limine-dracut
Version:        0.2.0
Release:        2%{?dist}
Summary:        Fedora dracut and kernel-install integration for Limine
License:        MIT
URL:            https://github.com/kamm3r/limine-pkg
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       limine-entry-tool >= 1.39
Requires:       dracut systemd systemd-boot-unsigned bash coreutils binutils

%description
Fedora helpers for rebuilding initramfs images and registering kernels in
Limine. Includes the limine-mkinitcpio compatibility command used by Omadora.
Does not rebuild images or deploy the bootloader during package installation.

%prep
%autosetup

%build

%install
install -D -m 0755 limine-mkinitcpio %{buildroot}%{_bindir}/limine-mkinitcpio
install -D -m 0755 limine-update %{buildroot}%{_bindir}/limine-update
install -D -m 0755 limine.install %{buildroot}%{_prefix}/lib/kernel/install.d/96-limine.install
# This override delegates to Fedora's /usr/lib plugin for other layouts.
install -D -m 0755 dracut.install %{buildroot}%{_sysconfdir}/kernel/install.d/50-dracut.install
install -D -m 0644 kernel-install.conf %{buildroot}%{_sysconfdir}/kernel/install.conf

%check
bash -n limine-mkinitcpio limine-update limine.install dracut.install

# RPM equivalents of upstream's 80-limine-efi-deploy and
# 90-limine-dracut-install ALPM hooks. Kernel RPMs already call kernel-install.
%transfiletriggerin -P 1000100 -- /usr/share/limine
if [ -f /etc/default/limine ] && [ -d /sys/firmware/efi ]; then
  /usr/bin/limine-install --no-efi-register
fi

%transfiletriggerin -P 1000200 -- /usr/lib/dracut /usr/lib/firmware /usr/lib/systemd/systemd /usr/bin/cryptsetup /usr/bin/lvm /usr/src /usr/lib/modules
if [ -f /etc/default/limine ] && [ -d /sys/firmware/efi ]; then
  /usr/bin/limine-mkinitcpio
fi

%transfiletriggerpostun -P 1000200 -- /usr/lib/dracut /usr/lib/firmware /usr/lib/systemd/systemd /usr/bin/cryptsetup /usr/bin/lvm /usr/src /usr/lib/modules
if [ -f /etc/default/limine ] && [ -d /sys/firmware/efi ] && [ -x /usr/bin/limine-mkinitcpio ]; then
  /usr/bin/limine-mkinitcpio
fi

%files
%license LICENSE
%ghost %{_sysconfdir}/limine-entry-tool.d/zz-fedora-kernel.conf
%{_bindir}/limine-mkinitcpio
%{_bindir}/limine-update
%{_prefix}/lib/kernel/install.d/96-limine.install
%config(noreplace) %{_sysconfdir}/kernel/install.d/50-dracut.install
%config(noreplace) %{_sysconfdir}/kernel/install.conf
