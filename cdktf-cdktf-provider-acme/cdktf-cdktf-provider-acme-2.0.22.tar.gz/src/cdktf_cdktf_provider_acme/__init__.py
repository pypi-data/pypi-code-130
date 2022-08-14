'''
# Terraform CDK acme Provider ~> 2.10

This repo builds and publishes the Terraform acme Provider bindings for [CDK for Terraform](https://cdk.tf).

## Available Packages

### NPM

The npm package is available at [https://www.npmjs.com/package/@cdktf/provider-acme](https://www.npmjs.com/package/@cdktf/provider-acme).

`npm install @cdktf/provider-acme`

### PyPI

The PyPI package is available at [https://pypi.org/project/cdktf-cdktf-provider-acme](https://pypi.org/project/cdktf-cdktf-provider-acme).

`pipenv install cdktf-cdktf-provider-acme`

### Nuget

The Nuget package is available at [https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Acme](https://www.nuget.org/packages/HashiCorp.Cdktf.Providers.Acme).

`dotnet add package HashiCorp.Cdktf.Providers.Acme`

### Maven

The Maven package is available at [https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-acme](https://mvnrepository.com/artifact/com.hashicorp/cdktf-provider-acme).

```
<dependency>
    <groupId>com.hashicorp</groupId>
    <artifactId>cdktf-provider-acme</artifactId>
    <version>[REPLACE WITH DESIRED VERSION]</version>
</dependency>
```

### Go

The go package is generated into the [`github.com/hashicorp/cdktf-provider-acme-go`](https://github.com/hashicorp/cdktf-provider-acme-go) package.

`go get github.com/hashicorp/cdktf-provider-acme-go/acme`

## Docs

Find auto-generated docs for this provider here: [./API.md](./API.md)
You can also visit a hosted version of the documentation on [constructs.dev](https://constructs.dev/packages/@cdktf/provider-acme).

## Versioning

This project is explicitly not tracking the Terraform acme Provider version 1:1. In fact, it always tracks `latest` of `~> 2.10` with every release. If there are scenarios where you explicitly have to pin your provider version, you can do so by generating the [provider constructs manually](https://cdk.tf/imports).

These are the upstream dependencies:

* [Terraform CDK](https://cdk.tf)
* [Terraform acme Provider](https://github.com/terraform-providers/terraform-provider-acme)
* [Terraform Engine](https://terraform.io)

If there are breaking changes (backward incompatible) in any of the above, the major version of this project will be bumped.

## Features / Issues / Bugs

Please report bugs and issues to the [terraform cdk](https://cdk.tf) project:

* [Create bug report](https://cdk.tf/bug)
* [Create feature request](https://cdk.tf/feature)

## Contributing

### projen

This is mostly based on [projen](https://github.com/eladb/projen), which takes care of generating the entire repository.

### cdktf-provider-project based on projen

There's a custom [project builder](https://github.com/hashicorp/cdktf-provider-project) which encapsulate the common settings for all `cdktf` providers.

### Provider Version

The provider version can be adjusted in [./.projenrc.js](./.projenrc.js).

### Repository Management

The repository is managed by [Repository Manager](https://github.com/hashicorp/cdktf-repository-manager/)
'''
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from typeguard import check_type

from ._jsii import *

import cdktf
import constructs


class AcmeProvider(
    cdktf.TerraformProvider,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.AcmeProvider",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/acme acme}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        server_url: builtins.str,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/acme acme} Resource.

        :param scope: The scope in which to define this construct.
        :param id: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param server_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme#server_url AcmeProvider#server_url}.
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme#alias AcmeProvider#alias}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AcmeProvider.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        config = AcmeProviderConfig(server_url=server_url, alias=alias)

        jsii.create(self.__class__, self, [scope, id, config])

    @jsii.member(jsii_name="resetAlias")
    def reset_alias(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetAlias", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="aliasInput")
    def alias_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "aliasInput"))

    @builtins.property
    @jsii.member(jsii_name="serverUrlInput")
    def server_url_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverUrlInput"))

    @builtins.property
    @jsii.member(jsii_name="alias")
    def alias(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "alias"))

    @alias.setter
    def alias(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AcmeProvider, "alias").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "alias", value)

    @builtins.property
    @jsii.member(jsii_name="serverUrl")
    def server_url(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "serverUrl"))

    @server_url.setter
    def server_url(self, value: typing.Optional[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(AcmeProvider, "server_url").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "serverUrl", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.AcmeProviderConfig",
    jsii_struct_bases=[],
    name_mapping={"server_url": "serverUrl", "alias": "alias"},
)
class AcmeProviderConfig:
    def __init__(
        self,
        *,
        server_url: builtins.str,
        alias: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param server_url: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme#server_url AcmeProvider#server_url}.
        :param alias: Alias name. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme#alias AcmeProvider#alias}
        '''
        if __debug__:
            type_hints = typing.get_type_hints(AcmeProviderConfig.__init__)
            check_type(argname="argument server_url", value=server_url, expected_type=type_hints["server_url"])
            check_type(argname="argument alias", value=alias, expected_type=type_hints["alias"])
        self._values: typing.Dict[str, typing.Any] = {
            "server_url": server_url,
        }
        if alias is not None:
            self._values["alias"] = alias

    @builtins.property
    def server_url(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme#server_url AcmeProvider#server_url}.'''
        result = self._values.get("server_url")
        assert result is not None, "Required property 'server_url' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def alias(self) -> typing.Optional[builtins.str]:
        '''Alias name.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme#alias AcmeProvider#alias}
        '''
        result = self._values.get("alias")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AcmeProviderConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class Certificate(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.Certificate",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/acme/r/certificate acme_certificate}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        account_key_pem: builtins.str,
        certificate_p12_password: typing.Optional[builtins.str] = None,
        certificate_request_pem: typing.Optional[builtins.str] = None,
        common_name: typing.Optional[builtins.str] = None,
        disable_complete_propagation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        dns_challenge: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CertificateDnsChallenge", typing.Dict[str, typing.Any]]]]] = None,
        http_challenge: typing.Optional[typing.Union["CertificateHttpChallenge", typing.Dict[str, typing.Any]]] = None,
        http_memcached_challenge: typing.Optional[typing.Union["CertificateHttpMemcachedChallenge", typing.Dict[str, typing.Any]]] = None,
        http_webroot_challenge: typing.Optional[typing.Union["CertificateHttpWebrootChallenge", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        min_days_remaining: typing.Optional[jsii.Number] = None,
        must_staple: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        pre_check_delay: typing.Optional[jsii.Number] = None,
        preferred_chain: typing.Optional[builtins.str] = None,
        recursive_nameservers: typing.Optional[typing.Sequence[builtins.str]] = None,
        revoke_certificate_on_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        tls_challenge: typing.Optional[typing.Union["CertificateTlsChallenge", typing.Dict[str, typing.Any]]] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/acme/r/certificate acme_certificate} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_key_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#account_key_pem Certificate#account_key_pem}.
        :param certificate_p12_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#certificate_p12_password Certificate#certificate_p12_password}.
        :param certificate_request_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#certificate_request_pem Certificate#certificate_request_pem}.
        :param common_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#common_name Certificate#common_name}.
        :param disable_complete_propagation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#disable_complete_propagation Certificate#disable_complete_propagation}.
        :param dns_challenge: dns_challenge block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#dns_challenge Certificate#dns_challenge}
        :param http_challenge: http_challenge block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#http_challenge Certificate#http_challenge}
        :param http_memcached_challenge: http_memcached_challenge block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#http_memcached_challenge Certificate#http_memcached_challenge}
        :param http_webroot_challenge: http_webroot_challenge block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#http_webroot_challenge Certificate#http_webroot_challenge}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#id Certificate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#key_type Certificate#key_type}.
        :param min_days_remaining: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#min_days_remaining Certificate#min_days_remaining}.
        :param must_staple: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#must_staple Certificate#must_staple}.
        :param pre_check_delay: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#pre_check_delay Certificate#pre_check_delay}.
        :param preferred_chain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#preferred_chain Certificate#preferred_chain}.
        :param recursive_nameservers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#recursive_nameservers Certificate#recursive_nameservers}.
        :param revoke_certificate_on_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#revoke_certificate_on_destroy Certificate#revoke_certificate_on_destroy}.
        :param subject_alternative_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#subject_alternative_names Certificate#subject_alternative_names}.
        :param tls_challenge: tls_challenge block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#tls_challenge Certificate#tls_challenge}
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Certificate.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = CertificateConfig(
            account_key_pem=account_key_pem,
            certificate_p12_password=certificate_p12_password,
            certificate_request_pem=certificate_request_pem,
            common_name=common_name,
            disable_complete_propagation=disable_complete_propagation,
            dns_challenge=dns_challenge,
            http_challenge=http_challenge,
            http_memcached_challenge=http_memcached_challenge,
            http_webroot_challenge=http_webroot_challenge,
            id=id,
            key_type=key_type,
            min_days_remaining=min_days_remaining,
            must_staple=must_staple,
            pre_check_delay=pre_check_delay,
            preferred_chain=preferred_chain,
            recursive_nameservers=recursive_nameservers,
            revoke_certificate_on_destroy=revoke_certificate_on_destroy,
            subject_alternative_names=subject_alternative_names,
            tls_challenge=tls_challenge,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putDnsChallenge")
    def put_dns_challenge(
        self,
        value: typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CertificateDnsChallenge", typing.Dict[str, typing.Any]]]],
    ) -> None:
        '''
        :param value: -
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Certificate.put_dns_challenge)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        return typing.cast(None, jsii.invoke(self, "putDnsChallenge", [value]))

    @jsii.member(jsii_name="putHttpChallenge")
    def put_http_challenge(
        self,
        *,
        port: typing.Optional[jsii.Number] = None,
        proxy_header: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#port Certificate#port}.
        :param proxy_header: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#proxy_header Certificate#proxy_header}.
        '''
        value = CertificateHttpChallenge(port=port, proxy_header=proxy_header)

        return typing.cast(None, jsii.invoke(self, "putHttpChallenge", [value]))

    @jsii.member(jsii_name="putHttpMemcachedChallenge")
    def put_http_memcached_challenge(
        self,
        *,
        hosts: typing.Sequence[builtins.str],
    ) -> None:
        '''
        :param hosts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#hosts Certificate#hosts}.
        '''
        value = CertificateHttpMemcachedChallenge(hosts=hosts)

        return typing.cast(None, jsii.invoke(self, "putHttpMemcachedChallenge", [value]))

    @jsii.member(jsii_name="putHttpWebrootChallenge")
    def put_http_webroot_challenge(self, *, directory: builtins.str) -> None:
        '''
        :param directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#directory Certificate#directory}.
        '''
        value = CertificateHttpWebrootChallenge(directory=directory)

        return typing.cast(None, jsii.invoke(self, "putHttpWebrootChallenge", [value]))

    @jsii.member(jsii_name="putTlsChallenge")
    def put_tls_challenge(self, *, port: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#port Certificate#port}.
        '''
        value = CertificateTlsChallenge(port=port)

        return typing.cast(None, jsii.invoke(self, "putTlsChallenge", [value]))

    @jsii.member(jsii_name="resetCertificateP12Password")
    def reset_certificate_p12_password(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateP12Password", []))

    @jsii.member(jsii_name="resetCertificateRequestPem")
    def reset_certificate_request_pem(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCertificateRequestPem", []))

    @jsii.member(jsii_name="resetCommonName")
    def reset_common_name(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetCommonName", []))

    @jsii.member(jsii_name="resetDisableCompletePropagation")
    def reset_disable_complete_propagation(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDisableCompletePropagation", []))

    @jsii.member(jsii_name="resetDnsChallenge")
    def reset_dns_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetDnsChallenge", []))

    @jsii.member(jsii_name="resetHttpChallenge")
    def reset_http_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpChallenge", []))

    @jsii.member(jsii_name="resetHttpMemcachedChallenge")
    def reset_http_memcached_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpMemcachedChallenge", []))

    @jsii.member(jsii_name="resetHttpWebrootChallenge")
    def reset_http_webroot_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetHttpWebrootChallenge", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="resetKeyType")
    def reset_key_type(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetKeyType", []))

    @jsii.member(jsii_name="resetMinDaysRemaining")
    def reset_min_days_remaining(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMinDaysRemaining", []))

    @jsii.member(jsii_name="resetMustStaple")
    def reset_must_staple(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetMustStaple", []))

    @jsii.member(jsii_name="resetPreCheckDelay")
    def reset_pre_check_delay(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreCheckDelay", []))

    @jsii.member(jsii_name="resetPreferredChain")
    def reset_preferred_chain(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPreferredChain", []))

    @jsii.member(jsii_name="resetRecursiveNameservers")
    def reset_recursive_nameservers(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRecursiveNameservers", []))

    @jsii.member(jsii_name="resetRevokeCertificateOnDestroy")
    def reset_revoke_certificate_on_destroy(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetRevokeCertificateOnDestroy", []))

    @jsii.member(jsii_name="resetSubjectAlternativeNames")
    def reset_subject_alternative_names(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetSubjectAlternativeNames", []))

    @jsii.member(jsii_name="resetTlsChallenge")
    def reset_tls_challenge(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetTlsChallenge", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="certificateDomain")
    def certificate_domain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateDomain"))

    @builtins.property
    @jsii.member(jsii_name="certificateP12")
    def certificate_p12(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateP12"))

    @builtins.property
    @jsii.member(jsii_name="certificatePem")
    def certificate_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificatePem"))

    @builtins.property
    @jsii.member(jsii_name="certificateUrl")
    def certificate_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateUrl"))

    @builtins.property
    @jsii.member(jsii_name="dnsChallenge")
    def dns_challenge(self) -> "CertificateDnsChallengeList":
        return typing.cast("CertificateDnsChallengeList", jsii.get(self, "dnsChallenge"))

    @builtins.property
    @jsii.member(jsii_name="httpChallenge")
    def http_challenge(self) -> "CertificateHttpChallengeOutputReference":
        return typing.cast("CertificateHttpChallengeOutputReference", jsii.get(self, "httpChallenge"))

    @builtins.property
    @jsii.member(jsii_name="httpMemcachedChallenge")
    def http_memcached_challenge(
        self,
    ) -> "CertificateHttpMemcachedChallengeOutputReference":
        return typing.cast("CertificateHttpMemcachedChallengeOutputReference", jsii.get(self, "httpMemcachedChallenge"))

    @builtins.property
    @jsii.member(jsii_name="httpWebrootChallenge")
    def http_webroot_challenge(
        self,
    ) -> "CertificateHttpWebrootChallengeOutputReference":
        return typing.cast("CertificateHttpWebrootChallengeOutputReference", jsii.get(self, "httpWebrootChallenge"))

    @builtins.property
    @jsii.member(jsii_name="issuerPem")
    def issuer_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "issuerPem"))

    @builtins.property
    @jsii.member(jsii_name="privateKeyPem")
    def private_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "privateKeyPem"))

    @builtins.property
    @jsii.member(jsii_name="tlsChallenge")
    def tls_challenge(self) -> "CertificateTlsChallengeOutputReference":
        return typing.cast("CertificateTlsChallengeOutputReference", jsii.get(self, "tlsChallenge"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyPemInput")
    def account_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountKeyPemInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateP12PasswordInput")
    def certificate_p12_password_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateP12PasswordInput"))

    @builtins.property
    @jsii.member(jsii_name="certificateRequestPemInput")
    def certificate_request_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "certificateRequestPemInput"))

    @builtins.property
    @jsii.member(jsii_name="commonNameInput")
    def common_name_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "commonNameInput"))

    @builtins.property
    @jsii.member(jsii_name="disableCompletePropagationInput")
    def disable_complete_propagation_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "disableCompletePropagationInput"))

    @builtins.property
    @jsii.member(jsii_name="dnsChallengeInput")
    def dns_challenge_input(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CertificateDnsChallenge"]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CertificateDnsChallenge"]]], jsii.get(self, "dnsChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="httpChallengeInput")
    def http_challenge_input(self) -> typing.Optional["CertificateHttpChallenge"]:
        return typing.cast(typing.Optional["CertificateHttpChallenge"], jsii.get(self, "httpChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="httpMemcachedChallengeInput")
    def http_memcached_challenge_input(
        self,
    ) -> typing.Optional["CertificateHttpMemcachedChallenge"]:
        return typing.cast(typing.Optional["CertificateHttpMemcachedChallenge"], jsii.get(self, "httpMemcachedChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="httpWebrootChallengeInput")
    def http_webroot_challenge_input(
        self,
    ) -> typing.Optional["CertificateHttpWebrootChallenge"]:
        return typing.cast(typing.Optional["CertificateHttpWebrootChallenge"], jsii.get(self, "httpWebrootChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="keyTypeInput")
    def key_type_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyTypeInput"))

    @builtins.property
    @jsii.member(jsii_name="minDaysRemainingInput")
    def min_days_remaining_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "minDaysRemainingInput"))

    @builtins.property
    @jsii.member(jsii_name="mustStapleInput")
    def must_staple_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "mustStapleInput"))

    @builtins.property
    @jsii.member(jsii_name="preCheckDelayInput")
    def pre_check_delay_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "preCheckDelayInput"))

    @builtins.property
    @jsii.member(jsii_name="preferredChainInput")
    def preferred_chain_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "preferredChainInput"))

    @builtins.property
    @jsii.member(jsii_name="recursiveNameserversInput")
    def recursive_nameservers_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "recursiveNameserversInput"))

    @builtins.property
    @jsii.member(jsii_name="revokeCertificateOnDestroyInput")
    def revoke_certificate_on_destroy_input(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], jsii.get(self, "revokeCertificateOnDestroyInput"))

    @builtins.property
    @jsii.member(jsii_name="subjectAlternativeNamesInput")
    def subject_alternative_names_input(
        self,
    ) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "subjectAlternativeNamesInput"))

    @builtins.property
    @jsii.member(jsii_name="tlsChallengeInput")
    def tls_challenge_input(self) -> typing.Optional["CertificateTlsChallenge"]:
        return typing.cast(typing.Optional["CertificateTlsChallenge"], jsii.get(self, "tlsChallengeInput"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyPem")
    def account_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountKeyPem"))

    @account_key_pem.setter
    def account_key_pem(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "account_key_pem").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountKeyPem", value)

    @builtins.property
    @jsii.member(jsii_name="certificateP12Password")
    def certificate_p12_password(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateP12Password"))

    @certificate_p12_password.setter
    def certificate_p12_password(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "certificate_p12_password").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateP12Password", value)

    @builtins.property
    @jsii.member(jsii_name="certificateRequestPem")
    def certificate_request_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "certificateRequestPem"))

    @certificate_request_pem.setter
    def certificate_request_pem(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "certificate_request_pem").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "certificateRequestPem", value)

    @builtins.property
    @jsii.member(jsii_name="commonName")
    def common_name(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "commonName"))

    @common_name.setter
    def common_name(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "common_name").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "commonName", value)

    @builtins.property
    @jsii.member(jsii_name="disableCompletePropagation")
    def disable_complete_propagation(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "disableCompletePropagation"))

    @disable_complete_propagation.setter
    def disable_complete_propagation(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "disable_complete_propagation").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "disableCompletePropagation", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)

    @builtins.property
    @jsii.member(jsii_name="keyType")
    def key_type(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyType"))

    @key_type.setter
    def key_type(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "key_type").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyType", value)

    @builtins.property
    @jsii.member(jsii_name="minDaysRemaining")
    def min_days_remaining(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "minDaysRemaining"))

    @min_days_remaining.setter
    def min_days_remaining(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "min_days_remaining").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "minDaysRemaining", value)

    @builtins.property
    @jsii.member(jsii_name="mustStaple")
    def must_staple(self) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "mustStaple"))

    @must_staple.setter
    def must_staple(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "must_staple").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "mustStaple", value)

    @builtins.property
    @jsii.member(jsii_name="preCheckDelay")
    def pre_check_delay(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "preCheckDelay"))

    @pre_check_delay.setter
    def pre_check_delay(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "pre_check_delay").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preCheckDelay", value)

    @builtins.property
    @jsii.member(jsii_name="preferredChain")
    def preferred_chain(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "preferredChain"))

    @preferred_chain.setter
    def preferred_chain(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "preferred_chain").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "preferredChain", value)

    @builtins.property
    @jsii.member(jsii_name="recursiveNameservers")
    def recursive_nameservers(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "recursiveNameservers"))

    @recursive_nameservers.setter
    def recursive_nameservers(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "recursive_nameservers").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "recursiveNameservers", value)

    @builtins.property
    @jsii.member(jsii_name="revokeCertificateOnDestroy")
    def revoke_certificate_on_destroy(
        self,
    ) -> typing.Union[builtins.bool, cdktf.IResolvable]:
        return typing.cast(typing.Union[builtins.bool, cdktf.IResolvable], jsii.get(self, "revokeCertificateOnDestroy"))

    @revoke_certificate_on_destroy.setter
    def revoke_certificate_on_destroy(
        self,
        value: typing.Union[builtins.bool, cdktf.IResolvable],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "revoke_certificate_on_destroy").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "revokeCertificateOnDestroy", value)

    @builtins.property
    @jsii.member(jsii_name="subjectAlternativeNames")
    def subject_alternative_names(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "subjectAlternativeNames"))

    @subject_alternative_names.setter
    def subject_alternative_names(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Certificate, "subject_alternative_names").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "subjectAlternativeNames", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.CertificateConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_key_pem": "accountKeyPem",
        "certificate_p12_password": "certificateP12Password",
        "certificate_request_pem": "certificateRequestPem",
        "common_name": "commonName",
        "disable_complete_propagation": "disableCompletePropagation",
        "dns_challenge": "dnsChallenge",
        "http_challenge": "httpChallenge",
        "http_memcached_challenge": "httpMemcachedChallenge",
        "http_webroot_challenge": "httpWebrootChallenge",
        "id": "id",
        "key_type": "keyType",
        "min_days_remaining": "minDaysRemaining",
        "must_staple": "mustStaple",
        "pre_check_delay": "preCheckDelay",
        "preferred_chain": "preferredChain",
        "recursive_nameservers": "recursiveNameservers",
        "revoke_certificate_on_destroy": "revokeCertificateOnDestroy",
        "subject_alternative_names": "subjectAlternativeNames",
        "tls_challenge": "tlsChallenge",
    },
)
class CertificateConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
        account_key_pem: builtins.str,
        certificate_p12_password: typing.Optional[builtins.str] = None,
        certificate_request_pem: typing.Optional[builtins.str] = None,
        common_name: typing.Optional[builtins.str] = None,
        disable_complete_propagation: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        dns_challenge: typing.Optional[typing.Union[cdktf.IResolvable, typing.Sequence[typing.Union["CertificateDnsChallenge", typing.Dict[str, typing.Any]]]]] = None,
        http_challenge: typing.Optional[typing.Union["CertificateHttpChallenge", typing.Dict[str, typing.Any]]] = None,
        http_memcached_challenge: typing.Optional[typing.Union["CertificateHttpMemcachedChallenge", typing.Dict[str, typing.Any]]] = None,
        http_webroot_challenge: typing.Optional[typing.Union["CertificateHttpWebrootChallenge", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        key_type: typing.Optional[builtins.str] = None,
        min_days_remaining: typing.Optional[jsii.Number] = None,
        must_staple: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        pre_check_delay: typing.Optional[jsii.Number] = None,
        preferred_chain: typing.Optional[builtins.str] = None,
        recursive_nameservers: typing.Optional[typing.Sequence[builtins.str]] = None,
        revoke_certificate_on_destroy: typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]] = None,
        subject_alternative_names: typing.Optional[typing.Sequence[builtins.str]] = None,
        tls_challenge: typing.Optional[typing.Union["CertificateTlsChallenge", typing.Dict[str, typing.Any]]] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_key_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#account_key_pem Certificate#account_key_pem}.
        :param certificate_p12_password: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#certificate_p12_password Certificate#certificate_p12_password}.
        :param certificate_request_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#certificate_request_pem Certificate#certificate_request_pem}.
        :param common_name: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#common_name Certificate#common_name}.
        :param disable_complete_propagation: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#disable_complete_propagation Certificate#disable_complete_propagation}.
        :param dns_challenge: dns_challenge block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#dns_challenge Certificate#dns_challenge}
        :param http_challenge: http_challenge block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#http_challenge Certificate#http_challenge}
        :param http_memcached_challenge: http_memcached_challenge block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#http_memcached_challenge Certificate#http_memcached_challenge}
        :param http_webroot_challenge: http_webroot_challenge block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#http_webroot_challenge Certificate#http_webroot_challenge}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#id Certificate#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param key_type: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#key_type Certificate#key_type}.
        :param min_days_remaining: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#min_days_remaining Certificate#min_days_remaining}.
        :param must_staple: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#must_staple Certificate#must_staple}.
        :param pre_check_delay: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#pre_check_delay Certificate#pre_check_delay}.
        :param preferred_chain: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#preferred_chain Certificate#preferred_chain}.
        :param recursive_nameservers: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#recursive_nameservers Certificate#recursive_nameservers}.
        :param revoke_certificate_on_destroy: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#revoke_certificate_on_destroy Certificate#revoke_certificate_on_destroy}.
        :param subject_alternative_names: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#subject_alternative_names Certificate#subject_alternative_names}.
        :param tls_challenge: tls_challenge block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#tls_challenge Certificate#tls_challenge}
        '''
        if isinstance(lifecycle, dict):
            lifecycle = TerraformResourceLifecycle(**lifecycle)
        if isinstance(http_challenge, dict):
            http_challenge = CertificateHttpChallenge(**http_challenge)
        if isinstance(http_memcached_challenge, dict):
            http_memcached_challenge = CertificateHttpMemcachedChallenge(**http_memcached_challenge)
        if isinstance(http_webroot_challenge, dict):
            http_webroot_challenge = CertificateHttpWebrootChallenge(**http_webroot_challenge)
        if isinstance(tls_challenge, dict):
            tls_challenge = CertificateTlsChallenge(**tls_challenge)
        if __debug__:
            type_hints = typing.get_type_hints(CertificateConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_key_pem", value=account_key_pem, expected_type=type_hints["account_key_pem"])
            check_type(argname="argument certificate_p12_password", value=certificate_p12_password, expected_type=type_hints["certificate_p12_password"])
            check_type(argname="argument certificate_request_pem", value=certificate_request_pem, expected_type=type_hints["certificate_request_pem"])
            check_type(argname="argument common_name", value=common_name, expected_type=type_hints["common_name"])
            check_type(argname="argument disable_complete_propagation", value=disable_complete_propagation, expected_type=type_hints["disable_complete_propagation"])
            check_type(argname="argument dns_challenge", value=dns_challenge, expected_type=type_hints["dns_challenge"])
            check_type(argname="argument http_challenge", value=http_challenge, expected_type=type_hints["http_challenge"])
            check_type(argname="argument http_memcached_challenge", value=http_memcached_challenge, expected_type=type_hints["http_memcached_challenge"])
            check_type(argname="argument http_webroot_challenge", value=http_webroot_challenge, expected_type=type_hints["http_webroot_challenge"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
            check_type(argname="argument key_type", value=key_type, expected_type=type_hints["key_type"])
            check_type(argname="argument min_days_remaining", value=min_days_remaining, expected_type=type_hints["min_days_remaining"])
            check_type(argname="argument must_staple", value=must_staple, expected_type=type_hints["must_staple"])
            check_type(argname="argument pre_check_delay", value=pre_check_delay, expected_type=type_hints["pre_check_delay"])
            check_type(argname="argument preferred_chain", value=preferred_chain, expected_type=type_hints["preferred_chain"])
            check_type(argname="argument recursive_nameservers", value=recursive_nameservers, expected_type=type_hints["recursive_nameservers"])
            check_type(argname="argument revoke_certificate_on_destroy", value=revoke_certificate_on_destroy, expected_type=type_hints["revoke_certificate_on_destroy"])
            check_type(argname="argument subject_alternative_names", value=subject_alternative_names, expected_type=type_hints["subject_alternative_names"])
            check_type(argname="argument tls_challenge", value=tls_challenge, expected_type=type_hints["tls_challenge"])
        self._values: typing.Dict[str, typing.Any] = {
            "account_key_pem": account_key_pem,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if certificate_p12_password is not None:
            self._values["certificate_p12_password"] = certificate_p12_password
        if certificate_request_pem is not None:
            self._values["certificate_request_pem"] = certificate_request_pem
        if common_name is not None:
            self._values["common_name"] = common_name
        if disable_complete_propagation is not None:
            self._values["disable_complete_propagation"] = disable_complete_propagation
        if dns_challenge is not None:
            self._values["dns_challenge"] = dns_challenge
        if http_challenge is not None:
            self._values["http_challenge"] = http_challenge
        if http_memcached_challenge is not None:
            self._values["http_memcached_challenge"] = http_memcached_challenge
        if http_webroot_challenge is not None:
            self._values["http_webroot_challenge"] = http_webroot_challenge
        if id is not None:
            self._values["id"] = id
        if key_type is not None:
            self._values["key_type"] = key_type
        if min_days_remaining is not None:
            self._values["min_days_remaining"] = min_days_remaining
        if must_staple is not None:
            self._values["must_staple"] = must_staple
        if pre_check_delay is not None:
            self._values["pre_check_delay"] = pre_check_delay
        if preferred_chain is not None:
            self._values["preferred_chain"] = preferred_chain
        if recursive_nameservers is not None:
            self._values["recursive_nameservers"] = recursive_nameservers
        if revoke_certificate_on_destroy is not None:
            self._values["revoke_certificate_on_destroy"] = revoke_certificate_on_destroy
        if subject_alternative_names is not None:
            self._values["subject_alternative_names"] = subject_alternative_names
        if tls_challenge is not None:
            self._values["tls_challenge"] = tls_challenge

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[cdktf.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[cdktf.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]], result)

    @builtins.property
    def account_key_pem(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#account_key_pem Certificate#account_key_pem}.'''
        result = self._values.get("account_key_pem")
        assert result is not None, "Required property 'account_key_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def certificate_p12_password(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#certificate_p12_password Certificate#certificate_p12_password}.'''
        result = self._values.get("certificate_p12_password")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def certificate_request_pem(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#certificate_request_pem Certificate#certificate_request_pem}.'''
        result = self._values.get("certificate_request_pem")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def common_name(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#common_name Certificate#common_name}.'''
        result = self._values.get("common_name")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def disable_complete_propagation(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#disable_complete_propagation Certificate#disable_complete_propagation}.'''
        result = self._values.get("disable_complete_propagation")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def dns_challenge(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CertificateDnsChallenge"]]]:
        '''dns_challenge block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#dns_challenge Certificate#dns_challenge}
        '''
        result = self._values.get("dns_challenge")
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List["CertificateDnsChallenge"]]], result)

    @builtins.property
    def http_challenge(self) -> typing.Optional["CertificateHttpChallenge"]:
        '''http_challenge block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#http_challenge Certificate#http_challenge}
        '''
        result = self._values.get("http_challenge")
        return typing.cast(typing.Optional["CertificateHttpChallenge"], result)

    @builtins.property
    def http_memcached_challenge(
        self,
    ) -> typing.Optional["CertificateHttpMemcachedChallenge"]:
        '''http_memcached_challenge block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#http_memcached_challenge Certificate#http_memcached_challenge}
        '''
        result = self._values.get("http_memcached_challenge")
        return typing.cast(typing.Optional["CertificateHttpMemcachedChallenge"], result)

    @builtins.property
    def http_webroot_challenge(
        self,
    ) -> typing.Optional["CertificateHttpWebrootChallenge"]:
        '''http_webroot_challenge block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#http_webroot_challenge Certificate#http_webroot_challenge}
        '''
        result = self._values.get("http_webroot_challenge")
        return typing.cast(typing.Optional["CertificateHttpWebrootChallenge"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#id Certificate#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def key_type(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#key_type Certificate#key_type}.'''
        result = self._values.get("key_type")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def min_days_remaining(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#min_days_remaining Certificate#min_days_remaining}.'''
        result = self._values.get("min_days_remaining")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def must_staple(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#must_staple Certificate#must_staple}.'''
        result = self._values.get("must_staple")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def pre_check_delay(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#pre_check_delay Certificate#pre_check_delay}.'''
        result = self._values.get("pre_check_delay")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def preferred_chain(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#preferred_chain Certificate#preferred_chain}.'''
        result = self._values.get("preferred_chain")
        return typing.cast(typing.Optional[builtins.str], result)

    @builtins.property
    def recursive_nameservers(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#recursive_nameservers Certificate#recursive_nameservers}.'''
        result = self._values.get("recursive_nameservers")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def revoke_certificate_on_destroy(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#revoke_certificate_on_destroy Certificate#revoke_certificate_on_destroy}.'''
        result = self._values.get("revoke_certificate_on_destroy")
        return typing.cast(typing.Optional[typing.Union[builtins.bool, cdktf.IResolvable]], result)

    @builtins.property
    def subject_alternative_names(self) -> typing.Optional[typing.List[builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#subject_alternative_names Certificate#subject_alternative_names}.'''
        result = self._values.get("subject_alternative_names")
        return typing.cast(typing.Optional[typing.List[builtins.str]], result)

    @builtins.property
    def tls_challenge(self) -> typing.Optional["CertificateTlsChallenge"]:
        '''tls_challenge block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#tls_challenge Certificate#tls_challenge}
        '''
        result = self._values.get("tls_challenge")
        return typing.cast(typing.Optional["CertificateTlsChallenge"], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.CertificateDnsChallenge",
    jsii_struct_bases=[],
    name_mapping={"provider": "provider", "config": "config"},
)
class CertificateDnsChallenge:
    def __init__(
        self,
        *,
        provider: builtins.str,
        config: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
    ) -> None:
        '''
        :param provider: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#provider Certificate#provider}.
        :param config: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#config Certificate#config}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateDnsChallenge.__init__)
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument config", value=config, expected_type=type_hints["config"])
        self._values: typing.Dict[str, typing.Any] = {
            "provider": provider,
        }
        if config is not None:
            self._values["config"] = config

    @builtins.property
    def provider(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#provider Certificate#provider}.'''
        result = self._values.get("provider")
        assert result is not None, "Required property 'provider' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def config(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#config Certificate#config}.'''
        result = self._values.get("config")
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateDnsChallenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateDnsChallengeList(
    cdktf.ComplexList,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.CertificateDnsChallengeList",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        wraps_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param wraps_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateDnsChallengeList.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument wraps_set", value=wraps_set, expected_type=type_hints["wraps_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, wraps_set])

    @jsii.member(jsii_name="get")
    def get(self, index: jsii.Number) -> "CertificateDnsChallengeOutputReference":
        '''
        :param index: the index of the item to return.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateDnsChallengeList.get)
            check_type(argname="argument index", value=index, expected_type=type_hints["index"])
        return typing.cast("CertificateDnsChallengeOutputReference", jsii.invoke(self, "get", [index]))

    @builtins.property
    @jsii.member(jsii_name="terraformAttribute")
    def _terraform_attribute(self) -> builtins.str:
        '''The attribute on the parent resource this class is referencing.'''
        return typing.cast(builtins.str, jsii.get(self, "terraformAttribute"))

    @_terraform_attribute.setter
    def _terraform_attribute(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateDnsChallengeList, "_terraform_attribute").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformAttribute", value)

    @builtins.property
    @jsii.member(jsii_name="terraformResource")
    def _terraform_resource(self) -> cdktf.IInterpolatingParent:
        '''The parent resource.'''
        return typing.cast(cdktf.IInterpolatingParent, jsii.get(self, "terraformResource"))

    @_terraform_resource.setter
    def _terraform_resource(self, value: cdktf.IInterpolatingParent) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateDnsChallengeList, "_terraform_resource").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "terraformResource", value)

    @builtins.property
    @jsii.member(jsii_name="wrapsSet")
    def _wraps_set(self) -> builtins.bool:
        '''whether the list is wrapping a set (will add tolist() to be able to access an item via an index).'''
        return typing.cast(builtins.bool, jsii.get(self, "wrapsSet"))

    @_wraps_set.setter
    def _wraps_set(self, value: builtins.bool) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateDnsChallengeList, "_wraps_set").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "wrapsSet", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CertificateDnsChallenge]]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CertificateDnsChallenge]]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, typing.List[CertificateDnsChallenge]]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateDnsChallengeList, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class CertificateDnsChallengeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.CertificateDnsChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
        complex_object_index: jsii.Number,
        complex_object_is_from_set: builtins.bool,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        :param complex_object_index: the index of this item in the list.
        :param complex_object_is_from_set: whether the list is wrapping a set (will add tolist() to be able to access an item via an index).
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateDnsChallengeOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
            check_type(argname="argument complex_object_index", value=complex_object_index, expected_type=type_hints["complex_object_index"])
            check_type(argname="argument complex_object_is_from_set", value=complex_object_is_from_set, expected_type=type_hints["complex_object_is_from_set"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute, complex_object_index, complex_object_is_from_set])

    @jsii.member(jsii_name="resetConfig")
    def reset_config(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetConfig", []))

    @builtins.property
    @jsii.member(jsii_name="configInput")
    def config_input(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        return typing.cast(typing.Optional[typing.Mapping[builtins.str, builtins.str]], jsii.get(self, "configInput"))

    @builtins.property
    @jsii.member(jsii_name="providerInput")
    def provider_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "providerInput"))

    @builtins.property
    @jsii.member(jsii_name="config")
    def config(self) -> typing.Mapping[builtins.str, builtins.str]:
        return typing.cast(typing.Mapping[builtins.str, builtins.str], jsii.get(self, "config"))

    @config.setter
    def config(self, value: typing.Mapping[builtins.str, builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateDnsChallengeOutputReference, "config").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "config", value)

    @builtins.property
    @jsii.member(jsii_name="provider")
    def provider(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "provider"))

    @provider.setter
    def provider(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateDnsChallengeOutputReference, "provider").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "provider", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(
        self,
    ) -> typing.Optional[typing.Union[cdktf.IResolvable, CertificateDnsChallenge]]:
        return typing.cast(typing.Optional[typing.Union[cdktf.IResolvable, CertificateDnsChallenge]], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[typing.Union[cdktf.IResolvable, CertificateDnsChallenge]],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateDnsChallengeOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.CertificateHttpChallenge",
    jsii_struct_bases=[],
    name_mapping={"port": "port", "proxy_header": "proxyHeader"},
)
class CertificateHttpChallenge:
    def __init__(
        self,
        *,
        port: typing.Optional[jsii.Number] = None,
        proxy_header: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#port Certificate#port}.
        :param proxy_header: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#proxy_header Certificate#proxy_header}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateHttpChallenge.__init__)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
            check_type(argname="argument proxy_header", value=proxy_header, expected_type=type_hints["proxy_header"])
        self._values: typing.Dict[str, typing.Any] = {}
        if port is not None:
            self._values["port"] = port
        if proxy_header is not None:
            self._values["proxy_header"] = proxy_header

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#port Certificate#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def proxy_header(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#proxy_header Certificate#proxy_header}.'''
        result = self._values.get("proxy_header")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateHttpChallenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateHttpChallengeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.CertificateHttpChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateHttpChallengeOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @jsii.member(jsii_name="resetProxyHeader")
    def reset_proxy_header(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetProxyHeader", []))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="proxyHeaderInput")
    def proxy_header_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "proxyHeaderInput"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateHttpChallengeOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property
    @jsii.member(jsii_name="proxyHeader")
    def proxy_header(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "proxyHeader"))

    @proxy_header.setter
    def proxy_header(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateHttpChallengeOutputReference, "proxy_header").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "proxyHeader", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CertificateHttpChallenge]:
        return typing.cast(typing.Optional[CertificateHttpChallenge], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[CertificateHttpChallenge]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateHttpChallengeOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.CertificateHttpMemcachedChallenge",
    jsii_struct_bases=[],
    name_mapping={"hosts": "hosts"},
)
class CertificateHttpMemcachedChallenge:
    def __init__(self, *, hosts: typing.Sequence[builtins.str]) -> None:
        '''
        :param hosts: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#hosts Certificate#hosts}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateHttpMemcachedChallenge.__init__)
            check_type(argname="argument hosts", value=hosts, expected_type=type_hints["hosts"])
        self._values: typing.Dict[str, typing.Any] = {
            "hosts": hosts,
        }

    @builtins.property
    def hosts(self) -> typing.List[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#hosts Certificate#hosts}.'''
        result = self._values.get("hosts")
        assert result is not None, "Required property 'hosts' is missing"
        return typing.cast(typing.List[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateHttpMemcachedChallenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateHttpMemcachedChallengeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.CertificateHttpMemcachedChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateHttpMemcachedChallengeOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="hostsInput")
    def hosts_input(self) -> typing.Optional[typing.List[builtins.str]]:
        return typing.cast(typing.Optional[typing.List[builtins.str]], jsii.get(self, "hostsInput"))

    @builtins.property
    @jsii.member(jsii_name="hosts")
    def hosts(self) -> typing.List[builtins.str]:
        return typing.cast(typing.List[builtins.str], jsii.get(self, "hosts"))

    @hosts.setter
    def hosts(self, value: typing.List[builtins.str]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateHttpMemcachedChallengeOutputReference, "hosts").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hosts", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CertificateHttpMemcachedChallenge]:
        return typing.cast(typing.Optional[CertificateHttpMemcachedChallenge], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CertificateHttpMemcachedChallenge],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateHttpMemcachedChallengeOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.CertificateHttpWebrootChallenge",
    jsii_struct_bases=[],
    name_mapping={"directory": "directory"},
)
class CertificateHttpWebrootChallenge:
    def __init__(self, *, directory: builtins.str) -> None:
        '''
        :param directory: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#directory Certificate#directory}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateHttpWebrootChallenge.__init__)
            check_type(argname="argument directory", value=directory, expected_type=type_hints["directory"])
        self._values: typing.Dict[str, typing.Any] = {
            "directory": directory,
        }

    @builtins.property
    def directory(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#directory Certificate#directory}.'''
        result = self._values.get("directory")
        assert result is not None, "Required property 'directory' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateHttpWebrootChallenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateHttpWebrootChallengeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.CertificateHttpWebrootChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateHttpWebrootChallengeOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="directoryInput")
    def directory_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "directoryInput"))

    @builtins.property
    @jsii.member(jsii_name="directory")
    def directory(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "directory"))

    @directory.setter
    def directory(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateHttpWebrootChallengeOutputReference, "directory").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "directory", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CertificateHttpWebrootChallenge]:
        return typing.cast(typing.Optional[CertificateHttpWebrootChallenge], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[CertificateHttpWebrootChallenge],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateHttpWebrootChallengeOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.CertificateTlsChallenge",
    jsii_struct_bases=[],
    name_mapping={"port": "port"},
)
class CertificateTlsChallenge:
    def __init__(self, *, port: typing.Optional[jsii.Number] = None) -> None:
        '''
        :param port: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#port Certificate#port}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateTlsChallenge.__init__)
            check_type(argname="argument port", value=port, expected_type=type_hints["port"])
        self._values: typing.Dict[str, typing.Any] = {}
        if port is not None:
            self._values["port"] = port

    @builtins.property
    def port(self) -> typing.Optional[jsii.Number]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/certificate#port Certificate#port}.'''
        result = self._values.get("port")
        return typing.cast(typing.Optional[jsii.Number], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CertificateTlsChallenge(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CertificateTlsChallengeOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.CertificateTlsChallengeOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(CertificateTlsChallengeOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @jsii.member(jsii_name="resetPort")
    def reset_port(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetPort", []))

    @builtins.property
    @jsii.member(jsii_name="portInput")
    def port_input(self) -> typing.Optional[jsii.Number]:
        return typing.cast(typing.Optional[jsii.Number], jsii.get(self, "portInput"))

    @builtins.property
    @jsii.member(jsii_name="port")
    def port(self) -> jsii.Number:
        return typing.cast(jsii.Number, jsii.get(self, "port"))

    @port.setter
    def port(self, value: jsii.Number) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateTlsChallengeOutputReference, "port").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "port", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[CertificateTlsChallenge]:
        return typing.cast(typing.Optional[CertificateTlsChallenge], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(self, value: typing.Optional[CertificateTlsChallenge]) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(CertificateTlsChallengeOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


class Registration(
    cdktf.TerraformResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.Registration",
):
    '''Represents a {@link https://www.terraform.io/docs/providers/acme/r/registration acme_registration}.'''

    def __init__(
        self,
        scope: constructs.Construct,
        id_: builtins.str,
        *,
        account_key_pem: builtins.str,
        email_address: builtins.str,
        external_account_binding: typing.Optional[typing.Union["RegistrationExternalAccountBinding", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
    ) -> None:
        '''Create a new {@link https://www.terraform.io/docs/providers/acme/r/registration acme_registration} Resource.

        :param scope: The scope in which to define this construct.
        :param id_: The scoped construct ID. Must be unique amongst siblings in the same scope
        :param account_key_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#account_key_pem Registration#account_key_pem}.
        :param email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#email_address Registration#email_address}.
        :param external_account_binding: external_account_binding block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#external_account_binding Registration#external_account_binding}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#id Registration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        '''
        if __debug__:
            type_hints = typing.get_type_hints(Registration.__init__)
            check_type(argname="argument scope", value=scope, expected_type=type_hints["scope"])
            check_type(argname="argument id_", value=id_, expected_type=type_hints["id_"])
        config = RegistrationConfig(
            account_key_pem=account_key_pem,
            email_address=email_address,
            external_account_binding=external_account_binding,
            id=id,
            connection=connection,
            count=count,
            depends_on=depends_on,
            for_each=for_each,
            lifecycle=lifecycle,
            provider=provider,
            provisioners=provisioners,
        )

        jsii.create(self.__class__, self, [scope, id_, config])

    @jsii.member(jsii_name="putExternalAccountBinding")
    def put_external_account_binding(
        self,
        *,
        hmac_base64: builtins.str,
        key_id: builtins.str,
    ) -> None:
        '''
        :param hmac_base64: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#hmac_base64 Registration#hmac_base64}.
        :param key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#key_id Registration#key_id}.
        '''
        value = RegistrationExternalAccountBinding(
            hmac_base64=hmac_base64, key_id=key_id
        )

        return typing.cast(None, jsii.invoke(self, "putExternalAccountBinding", [value]))

    @jsii.member(jsii_name="resetExternalAccountBinding")
    def reset_external_account_binding(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetExternalAccountBinding", []))

    @jsii.member(jsii_name="resetId")
    def reset_id(self) -> None:
        return typing.cast(None, jsii.invoke(self, "resetId", []))

    @jsii.member(jsii_name="synthesizeAttributes")
    def _synthesize_attributes(self) -> typing.Mapping[builtins.str, typing.Any]:
        return typing.cast(typing.Mapping[builtins.str, typing.Any], jsii.invoke(self, "synthesizeAttributes", []))

    @jsii.python.classproperty
    @jsii.member(jsii_name="tfResourceType")
    def TF_RESOURCE_TYPE(cls) -> builtins.str:
        return typing.cast(builtins.str, jsii.sget(cls, "tfResourceType"))

    @builtins.property
    @jsii.member(jsii_name="externalAccountBinding")
    def external_account_binding(
        self,
    ) -> "RegistrationExternalAccountBindingOutputReference":
        return typing.cast("RegistrationExternalAccountBindingOutputReference", jsii.get(self, "externalAccountBinding"))

    @builtins.property
    @jsii.member(jsii_name="registrationUrl")
    def registration_url(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "registrationUrl"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyPemInput")
    def account_key_pem_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "accountKeyPemInput"))

    @builtins.property
    @jsii.member(jsii_name="emailAddressInput")
    def email_address_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "emailAddressInput"))

    @builtins.property
    @jsii.member(jsii_name="externalAccountBindingInput")
    def external_account_binding_input(
        self,
    ) -> typing.Optional["RegistrationExternalAccountBinding"]:
        return typing.cast(typing.Optional["RegistrationExternalAccountBinding"], jsii.get(self, "externalAccountBindingInput"))

    @builtins.property
    @jsii.member(jsii_name="idInput")
    def id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "idInput"))

    @builtins.property
    @jsii.member(jsii_name="accountKeyPem")
    def account_key_pem(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "accountKeyPem"))

    @account_key_pem.setter
    def account_key_pem(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Registration, "account_key_pem").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "accountKeyPem", value)

    @builtins.property
    @jsii.member(jsii_name="emailAddress")
    def email_address(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "emailAddress"))

    @email_address.setter
    def email_address(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Registration, "email_address").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "emailAddress", value)

    @builtins.property
    @jsii.member(jsii_name="id")
    def id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "id"))

    @id.setter
    def id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(Registration, "id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "id", value)


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.RegistrationConfig",
    jsii_struct_bases=[cdktf.TerraformMetaArguments],
    name_mapping={
        "connection": "connection",
        "count": "count",
        "depends_on": "dependsOn",
        "for_each": "forEach",
        "lifecycle": "lifecycle",
        "provider": "provider",
        "provisioners": "provisioners",
        "account_key_pem": "accountKeyPem",
        "email_address": "emailAddress",
        "external_account_binding": "externalAccountBinding",
        "id": "id",
    },
)
class RegistrationConfig(cdktf.TerraformMetaArguments):
    def __init__(
        self,
        *,
        connection: typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]] = None,
        count: typing.Optional[jsii.Number] = None,
        depends_on: typing.Optional[typing.Sequence[cdktf.ITerraformDependable]] = None,
        for_each: typing.Optional[cdktf.ITerraformIterator] = None,
        lifecycle: typing.Optional[typing.Union[cdktf.TerraformResourceLifecycle, typing.Dict[str, typing.Any]]] = None,
        provider: typing.Optional[cdktf.TerraformProvider] = None,
        provisioners: typing.Optional[typing.Sequence[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]] = None,
        account_key_pem: builtins.str,
        email_address: builtins.str,
        external_account_binding: typing.Optional[typing.Union["RegistrationExternalAccountBinding", typing.Dict[str, typing.Any]]] = None,
        id: typing.Optional[builtins.str] = None,
    ) -> None:
        '''
        :param connection: 
        :param count: 
        :param depends_on: 
        :param for_each: 
        :param lifecycle: 
        :param provider: 
        :param provisioners: 
        :param account_key_pem: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#account_key_pem Registration#account_key_pem}.
        :param email_address: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#email_address Registration#email_address}.
        :param external_account_binding: external_account_binding block. Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#external_account_binding Registration#external_account_binding}
        :param id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#id Registration#id}. Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2. If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        if isinstance(lifecycle, dict):
            lifecycle = TerraformResourceLifecycle(**lifecycle)
        if isinstance(external_account_binding, dict):
            external_account_binding = RegistrationExternalAccountBinding(**external_account_binding)
        if __debug__:
            type_hints = typing.get_type_hints(RegistrationConfig.__init__)
            check_type(argname="argument connection", value=connection, expected_type=type_hints["connection"])
            check_type(argname="argument count", value=count, expected_type=type_hints["count"])
            check_type(argname="argument depends_on", value=depends_on, expected_type=type_hints["depends_on"])
            check_type(argname="argument for_each", value=for_each, expected_type=type_hints["for_each"])
            check_type(argname="argument lifecycle", value=lifecycle, expected_type=type_hints["lifecycle"])
            check_type(argname="argument provider", value=provider, expected_type=type_hints["provider"])
            check_type(argname="argument provisioners", value=provisioners, expected_type=type_hints["provisioners"])
            check_type(argname="argument account_key_pem", value=account_key_pem, expected_type=type_hints["account_key_pem"])
            check_type(argname="argument email_address", value=email_address, expected_type=type_hints["email_address"])
            check_type(argname="argument external_account_binding", value=external_account_binding, expected_type=type_hints["external_account_binding"])
            check_type(argname="argument id", value=id, expected_type=type_hints["id"])
        self._values: typing.Dict[str, typing.Any] = {
            "account_key_pem": account_key_pem,
            "email_address": email_address,
        }
        if connection is not None:
            self._values["connection"] = connection
        if count is not None:
            self._values["count"] = count
        if depends_on is not None:
            self._values["depends_on"] = depends_on
        if for_each is not None:
            self._values["for_each"] = for_each
        if lifecycle is not None:
            self._values["lifecycle"] = lifecycle
        if provider is not None:
            self._values["provider"] = provider
        if provisioners is not None:
            self._values["provisioners"] = provisioners
        if external_account_binding is not None:
            self._values["external_account_binding"] = external_account_binding
        if id is not None:
            self._values["id"] = id

    @builtins.property
    def connection(
        self,
    ) -> typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("connection")
        return typing.cast(typing.Optional[typing.Union[cdktf.ISSHProvisionerConnection, cdktf.IWinrmProvisionerConnection]], result)

    @builtins.property
    def count(self) -> typing.Optional[jsii.Number]:
        '''
        :stability: experimental
        '''
        result = self._values.get("count")
        return typing.cast(typing.Optional[jsii.Number], result)

    @builtins.property
    def depends_on(self) -> typing.Optional[typing.List[cdktf.ITerraformDependable]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("depends_on")
        return typing.cast(typing.Optional[typing.List[cdktf.ITerraformDependable]], result)

    @builtins.property
    def for_each(self) -> typing.Optional[cdktf.ITerraformIterator]:
        '''
        :stability: experimental
        '''
        result = self._values.get("for_each")
        return typing.cast(typing.Optional[cdktf.ITerraformIterator], result)

    @builtins.property
    def lifecycle(self) -> typing.Optional[cdktf.TerraformResourceLifecycle]:
        '''
        :stability: experimental
        '''
        result = self._values.get("lifecycle")
        return typing.cast(typing.Optional[cdktf.TerraformResourceLifecycle], result)

    @builtins.property
    def provider(self) -> typing.Optional[cdktf.TerraformProvider]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provider")
        return typing.cast(typing.Optional[cdktf.TerraformProvider], result)

    @builtins.property
    def provisioners(
        self,
    ) -> typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]]:
        '''
        :stability: experimental
        '''
        result = self._values.get("provisioners")
        return typing.cast(typing.Optional[typing.List[typing.Union[cdktf.IFileProvisioner, cdktf.ILocalExecProvisioner, cdktf.IRemoteExecProvisioner]]], result)

    @builtins.property
    def account_key_pem(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#account_key_pem Registration#account_key_pem}.'''
        result = self._values.get("account_key_pem")
        assert result is not None, "Required property 'account_key_pem' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def email_address(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#email_address Registration#email_address}.'''
        result = self._values.get("email_address")
        assert result is not None, "Required property 'email_address' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def external_account_binding(
        self,
    ) -> typing.Optional["RegistrationExternalAccountBinding"]:
        '''external_account_binding block.

        Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#external_account_binding Registration#external_account_binding}
        '''
        result = self._values.get("external_account_binding")
        return typing.cast(typing.Optional["RegistrationExternalAccountBinding"], result)

    @builtins.property
    def id(self) -> typing.Optional[builtins.str]:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#id Registration#id}.

        Please be aware that the id field is automatically added to all resources in Terraform providers using a Terraform provider SDK version below 2.
        If you experience problems setting this value it might not be settable. Please take a look at the provider documentation to ensure it should be settable.
        '''
        result = self._values.get("id")
        return typing.cast(typing.Optional[builtins.str], result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistrationConfig(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@cdktf/provider-acme.RegistrationExternalAccountBinding",
    jsii_struct_bases=[],
    name_mapping={"hmac_base64": "hmacBase64", "key_id": "keyId"},
)
class RegistrationExternalAccountBinding:
    def __init__(self, *, hmac_base64: builtins.str, key_id: builtins.str) -> None:
        '''
        :param hmac_base64: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#hmac_base64 Registration#hmac_base64}.
        :param key_id: Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#key_id Registration#key_id}.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(RegistrationExternalAccountBinding.__init__)
            check_type(argname="argument hmac_base64", value=hmac_base64, expected_type=type_hints["hmac_base64"])
            check_type(argname="argument key_id", value=key_id, expected_type=type_hints["key_id"])
        self._values: typing.Dict[str, typing.Any] = {
            "hmac_base64": hmac_base64,
            "key_id": key_id,
        }

    @builtins.property
    def hmac_base64(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#hmac_base64 Registration#hmac_base64}.'''
        result = self._values.get("hmac_base64")
        assert result is not None, "Required property 'hmac_base64' is missing"
        return typing.cast(builtins.str, result)

    @builtins.property
    def key_id(self) -> builtins.str:
        '''Docs at Terraform Registry: {@link https://www.terraform.io/docs/providers/acme/r/registration#key_id Registration#key_id}.'''
        result = self._values.get("key_id")
        assert result is not None, "Required property 'key_id' is missing"
        return typing.cast(builtins.str, result)

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegistrationExternalAccountBinding(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class RegistrationExternalAccountBindingOutputReference(
    cdktf.ComplexObject,
    metaclass=jsii.JSIIMeta,
    jsii_type="@cdktf/provider-acme.RegistrationExternalAccountBindingOutputReference",
):
    def __init__(
        self,
        terraform_resource: cdktf.IInterpolatingParent,
        terraform_attribute: builtins.str,
    ) -> None:
        '''
        :param terraform_resource: The parent resource.
        :param terraform_attribute: The attribute on the parent resource this class is referencing.
        '''
        if __debug__:
            type_hints = typing.get_type_hints(RegistrationExternalAccountBindingOutputReference.__init__)
            check_type(argname="argument terraform_resource", value=terraform_resource, expected_type=type_hints["terraform_resource"])
            check_type(argname="argument terraform_attribute", value=terraform_attribute, expected_type=type_hints["terraform_attribute"])
        jsii.create(self.__class__, self, [terraform_resource, terraform_attribute])

    @builtins.property
    @jsii.member(jsii_name="hmacBase64Input")
    def hmac_base64_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "hmacBase64Input"))

    @builtins.property
    @jsii.member(jsii_name="keyIdInput")
    def key_id_input(self) -> typing.Optional[builtins.str]:
        return typing.cast(typing.Optional[builtins.str], jsii.get(self, "keyIdInput"))

    @builtins.property
    @jsii.member(jsii_name="hmacBase64")
    def hmac_base64(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "hmacBase64"))

    @hmac_base64.setter
    def hmac_base64(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(RegistrationExternalAccountBindingOutputReference, "hmac_base64").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "hmacBase64", value)

    @builtins.property
    @jsii.member(jsii_name="keyId")
    def key_id(self) -> builtins.str:
        return typing.cast(builtins.str, jsii.get(self, "keyId"))

    @key_id.setter
    def key_id(self, value: builtins.str) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(RegistrationExternalAccountBindingOutputReference, "key_id").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "keyId", value)

    @builtins.property
    @jsii.member(jsii_name="internalValue")
    def internal_value(self) -> typing.Optional[RegistrationExternalAccountBinding]:
        return typing.cast(typing.Optional[RegistrationExternalAccountBinding], jsii.get(self, "internalValue"))

    @internal_value.setter
    def internal_value(
        self,
        value: typing.Optional[RegistrationExternalAccountBinding],
    ) -> None:
        if __debug__:
            type_hints = typing.get_type_hints(getattr(RegistrationExternalAccountBindingOutputReference, "internal_value").fset)
            check_type(argname="argument value", value=value, expected_type=type_hints["value"])
        jsii.set(self, "internalValue", value)


__all__ = [
    "AcmeProvider",
    "AcmeProviderConfig",
    "Certificate",
    "CertificateConfig",
    "CertificateDnsChallenge",
    "CertificateDnsChallengeList",
    "CertificateDnsChallengeOutputReference",
    "CertificateHttpChallenge",
    "CertificateHttpChallengeOutputReference",
    "CertificateHttpMemcachedChallenge",
    "CertificateHttpMemcachedChallengeOutputReference",
    "CertificateHttpWebrootChallenge",
    "CertificateHttpWebrootChallengeOutputReference",
    "CertificateTlsChallenge",
    "CertificateTlsChallengeOutputReference",
    "Registration",
    "RegistrationConfig",
    "RegistrationExternalAccountBinding",
    "RegistrationExternalAccountBindingOutputReference",
]

publication.publish()
