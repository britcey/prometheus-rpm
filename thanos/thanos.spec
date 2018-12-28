%define debug_package %{nil}

Name:		 thanos
Version: 0.2.1
Release: 1%{?dist}
Summary: Highly available Prometheus setup with long term storage capabilities.
License: ASL 2.0
URL:     https://github.com/improbable-eng/thanos

Source0: https://github.com/improbable-eng/thanos/releases/download/v%{version}/thanos-%version.linux-amd64.tar.gz
Source1: thanos_sidecar.service
Source2: thanos_query.service
Source3: thanos_sidecar.default
Source4: thanos_query.default
Source5: thanos_store_nodes.yml

%{?systemd_requires}
Requires(pre): shadow-utils

%description

Thanos is a set of components that can be composed into a highly available
metric system with unlimited storage capacity. It can be added seamlessly on top
of existing Prometheus deployments and leverages the Prometheus 2.0 storage
format to cost-efficiently store historical metric data in any object storage
while retaining fast query latencies. Additionally, it provides a global query
view across all Prometheus installations and can merge data from Prometheus HA
pairs on the fly.

%prep
%setup -q -n thanos-%{version}.linux-amd64

%build
/bin/true

%install
mkdir -vp %{buildroot}%{_sharedstatedir}/thanos
mkdir -vp %{buildroot}%{_sysconfdir}/thanos
install -D -m 755 thanos %{buildroot}%{_bindir}/thanos
install -D -m 644 %{SOURCE1} %{buildroot}%{_unitdir}/thanos_sidecar.service
install -D -m 644 %{SOURCE2} %{buildroot}%{_unitdir}/thanos_query.service
install -D -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/default/thanos_sidecar
install -D -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/default/thanos_query
install -D -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/thanos/thanos_store_nodes.yml

%pre
getent group prometheus >/dev/null || groupadd -r prometheus
getent passwd prometheus >/dev/null || \
  useradd -r -g prometheus -d %{_sharedstatedir}/prometheus -s /sbin/nologin \
          -c "Prometheus services" prometheus
exit 0

%post
%systemd_post thanos_sidecar.service
%systemd_post thanos_query.service

%preun
%systemd_preun thanos_sidecar.service
%systemd_preun thanos_query.service

%postun
%systemd_postun thanos_sidecar.service
%systemd_postun thanos_query.service

%files
%defattr(-,root,root,-)
%{_bindir}/thanos
%config(noreplace) %{_sysconfdir}/thanos/thanos_store_nodes.yml
%{_unitdir}/thanos_sidecar.service
%{_unitdir}/thanos_query.service
%config(noreplace) %{_sysconfdir}/default/thanos_sidecar
%config(noreplace) %{_sysconfdir}/default/thanos_query
