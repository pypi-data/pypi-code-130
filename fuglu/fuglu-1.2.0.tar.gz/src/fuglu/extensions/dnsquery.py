# -*- coding: utf-8 -*-
#   Copyright 2009-2022 Fumail Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#

class _DummyExc(Exception):
    pass


import ipaddress

STATUS = "not loaded"
_NXDOMAIN = _DummyExc
DNS_TIMEOUT = TimeoutError
_PYDNSEXC = _DummyExc
_NONAMESERVER = _DummyExc
_NOANSWER = _DummyExc
try:
    from dns import resolver, exception
    HAVE_DNSPYTHON=True
    STATUS = "available"
    _NXDOMAIN = resolver.NXDOMAIN
    DNS_TIMEOUT = exception.Timeout
    _NONAMESERVER = resolver.NoNameservers
    _NOANSWER = resolver.NoAnswer
except ImportError:
    resolver = None
    HAVE_DNSPYTHON=False

HAVE_PYDNS=False
if not HAVE_DNSPYTHON:
    try:
        import DNS
        HAVE_PYDNS=True
        DNS.DiscoverNameServers()
        STATUS = "available"
        _PYDNSEXC = DNS.Base.ServerError
    except ImportError:
        DNS = None
        STATUS = "DNS not installed"

ENABLED = DNSQUERY_EXTENSION_ENABLED = HAVE_DNSPYTHON or HAVE_PYDNS



QTYPE_A = 'A'
QTYPE_AAAA = 'AAAA'
QTYPE_MX = 'MX'
QTYPE_NS = 'NS'
QTYPE_TXT = 'TXT'
QTYPE_PTR = 'PTR'
QTYPE_CNAME = 'CNAME'
QTYPE_SPF = 'SPF'
QTYPE_SRV = 'SRV'
QTYPE_SOA = 'SOA'
QTYPE_CAA = 'CAA'
QTYPE_DS = 'DS'
QTYPE_DNSKEY = 'DNSKEY'
QTYPE_SSHFP = 'SSHFP'
QTYPE_TLSA = 'TLSA'



class FuNXDOMAIN(Exception):
    pass

class FuTIMEOUT(Exception):
    pass

class FuSERVFAIL(Exception):
    pass

class FuNoNameserver(Exception):
    pass

class FuNoAnswer(Exception):
    pass


def lookup(hostname, qtype=QTYPE_A, reraise=False):
    try:
        if HAVE_DNSPYTHON:
            arecs = []
            arequest = resolver.resolve(hostname, qtype)
            for rec in arequest:
                arecs.append(rec.to_text())
            return arecs

        elif HAVE_PYDNS:
            return DNS.dnslookup(hostname, qtype)
    
    except _NXDOMAIN:
        if reraise:
            raise FuNXDOMAIN
    except DNS_TIMEOUT:
        if reraise:
            raise FuTIMEOUT
    except _NONAMESERVER:
        if reraise:
            raise FuNoNameserver
    except _NOANSWER:
        if reraise:
            raise FuNoAnswer
    except _PYDNSEXC as e:
        if reraise and 'NXDOMAIN' in e.message:
            raise FuNXDOMAIN
        if reraise and 'SERVFAIL' in e.message:
            raise FuSERVFAIL
    except Exception:
        if reraise:
            raise

    return None



def mxlookup(domain):
    try:
        if HAVE_DNSPYTHON:
            mxrecs = []
            mxrequest = resolver.resolve(domain, QTYPE_MX)
            for rec in mxrequest:
                mxrecs.append(rec.to_text())
            mxrecs.sort()  # automatically sorts by priority
            return [x.split(None, 1)[-1] for x in mxrecs]

        elif HAVE_PYDNS:
            mxrecs = []
            mxrequest = DNS.mxlookup(domain)
            for dataset in mxrequest:
                if type(dataset) == tuple:
                    mxrecs.append(dataset)

            mxrecs.sort()  # automatically sorts by priority
            return [x[1] for x in mxrecs]

    except Exception:
        return None

    return None



def revlookup(ip, reraise=False):
    ipaddr = ipaddress.ip_address(ip)
    revip = ipaddr.reverse_pointer
    return lookup(revip, qtype=QTYPE_PTR, reraise=reraise)
