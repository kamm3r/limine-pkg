Name:           limine-dracut
Version:        0.1.0
Release:        1%{?dist}
Summary:        Fedora dracut and kernel-install integration for Limine
License:        MIT
URL:            https://github.com/kamm3r/limine-pkg
Source0:        %{name}-%{version}.tar.gz
BuildArch:      noarch
Requires:       limine-entry-tool >= 1.39
Requires:       dracut systemd bash coreutils

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

%files
%license LICENSE
%{_bindir}/limine-mkinitcpio
%{_bindir}/limine-update
%{_prefix}/lib/kernel/install.d/96-limine.install
%config(noreplace) %{_sysconfdir}/kernel/install.d/50-dracut.install
%config(noreplace) %{_sysconfdir}/kernel/install.conf
