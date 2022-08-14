import pem
from twisted.internet import ssl
from twisted.internet._sslverify import (
    OpenSSLCertificateAuthorities,
    PrivateCertificate,
    optionsForClientTLS,
)

from twisted.web.client import _requireSSL
from twisted.web.iweb import IPolicyForHTTPS
from zope.interface import implementer


def parseTrustRootFromBundle(pemFilePath: str) -> OpenSSLCertificateAuthorities:
    # parse PEM format
    trustRootPEMs = pem.parse_file(pemFilePath)

    # load certificates in the PEM bundle file
    trustedPeerAuthorities = []
    for trustedPeerCertificateAuthorityPEM in trustRootPEMs:
        trustedPeerAuthorities.append(
            ssl.Certificate.loadPEM(
                trustedPeerCertificateAuthorityPEM.as_text()
            )
        )

    return OpenSSLCertificateAuthorities(
        [auth.original for auth in trustedPeerAuthorities]
    )


def parsePrivateCertificateFromBundle(pemFilePath: str) -> PrivateCertificate:
    key, cert, ca = pem.parse_file(pemFilePath)
    return ssl.PrivateCertificate.loadPEM(key.as_text() + cert.as_text())


@implementer(IPolicyForHTTPS)
class MutualAuthenticationPolicyForHTTPS:
    def __init__(
        self,
        clientCertificate: PrivateCertificate = None,
        trustRoot=None,
    ):
        if clientCertificate:
            self._clientCertificate = clientCertificate
        self._trustRoot = trustRoot

    @_requireSSL
    def creatorForNetloc(self, hostname, port):
        return optionsForClientTLS(
            hostname.decode("ascii"),
            clientCertificate=self._clientCertificate,
            trustRoot=self._trustRoot,
            acceptableProtocols=[b"http/1.1"],
        )


def buildSSLContextFactoryForMutualTLS(
    sslClientCertificateBundleFilePath: str,
    sslTrustedPeerCertificateAuthorityBundleFilePath: str,
) -> MutualAuthenticationPolicyForHTTPS:
    trustRoot = parseTrustRootFromBundle(
        sslTrustedPeerCertificateAuthorityBundleFilePath
    )
    clientCertificate = parsePrivateCertificateFromBundle(
        sslClientCertificateBundleFilePath
    )
    return MutualAuthenticationPolicyForHTTPS(
        clientCertificate=clientCertificate,
        trustRoot=trustRoot,
    )
