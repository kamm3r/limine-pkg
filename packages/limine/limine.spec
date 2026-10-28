Name:           limine
Version:        12.9.6
Release:        1%{?dist}
Summary:        Portable multiprotocol bootloader
License:        BSD-2-Clause
URL:            https://github.com/Limine-Bootloader/Limine
Source0:        %{url}/releases/download/v%{version}/limine-binary.tar.gz#/limine-binary-%{version}.tar.gz
ExclusiveArch:  x86_64
BuildRequires:  gcc
BuildRequires:  make

%description
Limine bootloader firmware binaries and the native host installation tool.
Installing this package does not deploy firmware to the EFI System Partition
or change UEFI boot entries. Run limine-install separately when configured.

%prep
%autosetup -n limine-binary

%build
%set_build_flags
%make_build CC=gcc CFLAGS="$CFLAGS" LDFLAGS="$LDFLAGS"

%install
install -D -m 0755 limine %{buildroot}%{_bindir}/limine
install -d %{buildroot}%{_datadir}/limine
install -m 0644 *.EFI *.bin limine-bios.sys %{buildroot}%{_datadir}/limine/

%check
./limine --version

%files
%license LICENSE
%doc 3RDPARTY.md
%{_bindir}/limine
%{_datadir}/limine/
