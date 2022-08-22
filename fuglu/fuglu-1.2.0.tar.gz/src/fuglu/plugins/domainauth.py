# -*- coding: UTF-8 -*-
#   Copyright 2009-2022 Oli Schacher, Fumail Project
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
"""
Antiphish / Forging Plugins (DKIM / SPF / SRS etc)

requires: dkimpy (not pydkim!!)
requires: pyspf
requires: pydns (or alternatively dnspython if only dkim is used)
requires: pysrs
requires: pynacl (rare dependeny of dkimpy)
requires: dmarc
"""
import ipaddress
import logging
import os
import re
import time
import traceback
import typing as tp
import fnmatch
import socket

import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm

from fuglu.shared import ScannerPlugin, apply_template, DUNNO, FileList, string_to_actioncode, get_default_cache, \
    extract_domain, Suspect, Cache, actioncode_to_string, deprecated, get_outgoing_helo
from fuglu.mshared import BMPMailFromMixin, BMPRCPTMixin, BMPEOBMixin, BasicMilterPlugin, EOM, retcode2milter
from fuglu.extensions.sql import get_session, SQL_EXTENSION_ENABLED, get_domain_setting
from fuglu.extensions.dnsquery import DNSQUERY_EXTENSION_ENABLED, lookup, QTYPE_TXT, DNS_TIMEOUT, revlookup, FuSERVFAIL
from fuglu.stringencode import force_bString, force_uString
from fuglu.logtools import PrependLoggerMsg

DKIMPY_AVAILABLE = False
ARCSIGN_AVAILABLE = False
PYSPF_AVAILABLE = False
DMARC_AVAILABLE = False
SRS_AVAILABLE = False

try:
    import dkim
    from dkim import DKIM, ARC
    if DNSQUERY_EXTENSION_ENABLED:
        DKIMPY_AVAILABLE = True
        try:
            import authres
            ARCSIGN_AVAILABLE = True
        except ImportError:
            pass
except ImportError:
    dkim = None
    DKIM = None
    ARC = None

try:
    import spf
    HAVE_SPF = True
    if DNSQUERY_EXTENSION_ENABLED:
        PYSPF_AVAILABLE = True
except ImportError:
    spf = None
    HAVE_SPF = False

try:
    from domainmagic.tld import TLDMagic
    from domainmagic.mailaddr import domain_from_mail
    from domainmagic.validators import is_ipv6
    DOMAINMAGIC_AVAILABLE = True
except ImportError:
    DOMAINMAGIC_AVAILABLE = False
    TLDMagic = None
    def domain_from_mail(address, **kwargs):
        if address and "@" in address:
            return address.rsplit("@", 1)[-1]
        return address
    def is_ipv6(ipaddr):
        return ipaddr and ':' in ipaddr

try:
    import dmarc
    DMARC_AVAILABLE = True
    if DNSQUERY_EXTENSION_ENABLED and DOMAINMAGIC_AVAILABLE:
        DMARC_AVAILABLE = True
except ImportError:
    dmarc = None

try:
    import SRS
    SRS_AVAILABLE = True
except ImportError:
    SRS = None

ARC_SAHEADER = 'X-ARCVerify'
DKIM_SAHEADER = 'X-DKIMVerify'
DKIM_PASS_AUTHOR = 'passauthor'  # dkim record is valid and in authors/from hdr domain
DKIM_PASS_SENDER = 'passsender'  # dkim record is valid and in envelope sender domain
DKIM_PASS = 'pass'
DKIM_FAIL = 'fail'
DKIM_NONE = 'none'
DKIM_POLICY = 'policy'
DKIM_NEUTRAL = 'neutral'
DKIM_TEMPFAIL = 'tempfail'
DKIM_PERMFAIL = 'permfail'
DMARC_SAHEADER_RESULT = 'X-DMARC-Result'
DMARC_SAHEADER_DISPO = 'X-DMARC-Dispo'
DMARC_REJECT = 'reject'
DMARC_QUARANTINE = 'quarantine'
DMARC_SKIP = 'skip'
DMARC_NONE = 'none'
DMARC_PASS = 'pass'
DMARC_FAIL = 'fail'
DMARC_RECORDFAIL = 'recordfail'


_re_at = re.compile(r"(?<=[@＠])[\w.-]+")
def extract_from_domains(suspect, header='From', get_display_part=False):
    """
    Returns a list of all domains found in From header
    :param suspect: Suspect
    :param header: name of header to extract, defaults to From
    :param get_display_part: set to True to search and extract domains found in display part, not the actual addresses
    :return: list of domain names or None in case of errors
    """

    # checking display part there's no need checking for the validity of the associated
    # mail address
    from_addresses = suspect.parse_from_type_header(header=header, validate_mail=(not get_display_part))
    if len(from_addresses) < 1:
        return None

    from_doms = []
    for item in from_addresses:
        if get_display_part:
            domain_match = _re_at.search(item[0])
            if domain_match is None:
                continue
            from_doms.append(domain_match.group())
        else:
            try:
                from_doms.append(extract_domain(item[1]))
            except Exception as e:
                logging.getLogger("fuglu.extract_from_domains").exception(e)

    from_addrs = list(set(from_doms))
    return from_addrs


def extract_from_domain(suspect, header='From', get_display_part=False):
    """
    Returns the most significant domain found in From header.
    Usually this means the last domain that can be found.
    :param suspect: Suspect object
    :param header: name of header to extract, defaults to From
    :param get_display_part: set to True to search and extract domains found in display part, not the actual addresses
    :return: string with domain name or None if nothing found
    """
    from_doms = extract_from_domains(suspect, header, get_display_part)
    if from_doms and from_doms[-1]:
        from_dom = from_doms[-1].lower()
    else:
        from_dom = None
    return from_dom


class ARCVerifyPlugin(ScannerPlugin):
    """
    Experimental: This plugin checks the ARC signature of the message and sets tags.
    """

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()

    def __str__(self):
        return "ARC Verify"
    
    dkim_dns_func = None

    def examine(self, suspect):
        suspect.set_tag("ARCVerify.cv", 'none')
        if not DKIMPY_AVAILABLE:
            suspect.debug("dkimpy not available, can not check ARC")
            suspect.set_tag('ARCVerify.skipreason', 'dkimpy library not available')
            return DUNNO

        msgrep = suspect.get_message_rep()
        for hdrname in ARC.ARC_HEADERS:
            hdrname = force_uString(hdrname)
            if hdrname not in msgrep:
                suspect.set_tag('ARCVerify.skipreason', 'not ARC signed')
                suspect.write_sa_temp_header(ARC_SAHEADER, 'none')
                suspect.debug("ARC signature header %s not found" % hdrname)
                return DUNNO

        source = suspect.get_source()
        try:
            cv = 'none'
            message = 'Message validation error'
            # use the local logger of the plugin but prepend the fuglu id
            d = ARC(source, logger=PrependLoggerMsg(self.logger, prepend=suspect.id, maxlevel=logging.INFO))
            try:
                if self.dkim_dns_func is not None:
                    data = d.verify(dnsfunc=self.dkim_dns_func)
                else:
                    data = d.verify()
                if len(data) != 3:
                    self.logger.warning("%s: ARC validation with unexpected data: %s" % (suspect.id, data))
                else:
                    self.logger.debug("%s: ARC result %s" % (suspect.id, data))
                    cv, result, message = data
            except Exception as de:
                self.logger.warning("%s: ARC validation failed: %s %s" % (suspect.id, de.__class__.__name__, str(de)))
            suspect.set_tag("ARCVerify.cv", force_uString(cv))
            suspect.set_tag("ARCVerify.message", message)
            suspect.write_sa_temp_header(ARC_SAHEADER, force_uString(cv))
        except dkim.MessageFormatError as e:
            self.logger.warning("%s: ARC validation failed: Message format error" % suspect.id)
            self.logger.debug("%s: %s" % (suspect.id, str(e)))
            suspect.set_tag('ARCVerify.skipreason', 'plugin error')
            suspect.set_tag("ARCVerify.cv", 'fail')
            
        except NameError as e:
            self.logger.warning("%s: ARC validation failed due to missing dependency: %s" % (suspect.id, str(e)))
            suspect.set_tag('ARCVerify.skipreason', 'plugin error')
        except Exception as e:
            self.logger.warning("%s: ARC validation failed: %s %s" % (suspect.id, e.__class__.__name__, str(e)))
            suspect.set_tag('ARCVerify.skipreason', 'plugin error')

        return DUNNO

    def lint(self):
        all_ok = self.check_config()

        if not DKIMPY_AVAILABLE:
            print("Missing dependency: dkimpy https://launchpad.net/dkimpy")
            all_ok = False

        if not DNSQUERY_EXTENSION_ENABLED:
            print("Missing dependency: no supported DNS libary found: pydns or dnspython")
            all_ok = False

        return all_ok


class ARCSignPlugin(ScannerPlugin):
    """
    EXPERiMENTAL: This plugin creates the ARC signature headers of the message.
    """
    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'privatekeyfile': {
                'default': "${confdir}/dkim/${header_from_domain}.key",
                'description': "Location of the private key file. supports standard template variables plus additional ${header_from_domain} which extracts the domain name from the From: -Header",
            },

            'selector': {
                'default': 'default',
                'description': 'selector to use when signing, supports templates',
            },

            'signheaders': {
                'default': 'From,Reply-To,Subject,Date,To,CC,Resent-Date,Resent-From,Resent-To,Resent-CC,In-Reply-To,References,List-Id,List-Help,List-Unsubscribe,List-Subscribe,List-Post,List-Owner,List-Archive',
                'description': 'comma separated list of headers to sign. empty string=sign all headers',
            },
            
            'signdomain': {
                'default': 'header:From',
                'description': 'which domain to use in signature? use header:headername or static:example.com or tmpl:${template_var}',
            },
            
            'trust_authres_rgx': {
                'default': '',
                'description': 'do not create own but use authentication-results header of previous host if ptr matches given regex'
            },
            
            'reuse_authres_tag': {
                'default': '',
                'description': 'name of suspect tag that must be set to True to enable authenetication-results header reuse (as per trust_authres_rgx). if empty no tag is checked.'
            },
        }
    
    
    def __str__(self):
        return "ARC Sign"
    
    
    def _get_source(self, suspect:Suspect) -> bytes:
        """
        get source and patch/remove invalid authres headers (e.g. from microsoft)
        :param suspect: Suspect
        :return: message source as bytes
        """
        clientinfo = suspect.get_client_info(self.config)
        helo = clientinfo[0].lower() if clientinfo else None
        ptr = clientinfo[2].lower() if clientinfo else None
        msgrep = suspect.get_message_rep()
        authres_hdrs = msgrep.get_all('Authentication-Results', [])
        if authres_hdrs:
            ok_hdrs = []
            for hdr in authres_hdrs:
                try:
                    try:
                        authres.AuthenticationResultsHeader.parse(f'Authentication-Results: {hdr}')
                        ok_hdrs.append(hdr)
                    except authres.core.SyntaxError:
                        if helo and ptr and ptr.endswith('.outlook.com'):
                            helohdr = f'{helo}; {hdr}'
                            authres.AuthenticationResultsHeader.parse(f'Authentication-Results: {helohdr}')
                            ok_hdrs.append(helohdr)
                            self.logger.debug(f'{suspect.id} patching invalid authres header {hdr}')
                        else:
                            self.logger.debug(f'{suspect.id} not patching invalid authres header from {helo}')
                            raise
                except authres.core.SyntaxError:
                    self.logger.debug(f'{suspect.id} dropping invalid authres header {hdr}')
            del msgrep['Authentication-Results']
            for hdr in ok_hdrs:
                msgrep.add_header('Authentication-Results', hdr)
            self.logger.debug(f'{suspect.id} using {len(ok_hdrs)} authres headers')
        return msgrep.as_bytes()
    
    
    def _authres_insert_arcpass(self, authres):
        fields = authres.split(';')
        has_arc = False
        for field in fields:
            if field.strip().startswith('arc='):
                has_arc = True
                break
        if not has_arc: # previous arc sig found but not mentioned in authres header
            fields.append('arc=pass')
        return ';'.join(fields)
    
    
    def _reuse_authres_header(self, suspect:Suspect, authhost:str) -> tp.Optional[str]:
        hdr = None
        ptrrgx = self.config.get(self.section, 'trust_authres_rgx')
        tag = self.config.get(self.section, 'reuse_authres_tag')
        reuse_tag = suspect.get_tag(tag, False) if tag else True
        if ptrrgx and reuse_tag==True:
            self.logger.debug(f'{suspect.id} ptrrgx is set and tag {tag} is {suspect.get_tag(tag)}')
            clientinfo = suspect.get_client_info(self.config)
            ptr = clientinfo[2].lower() if clientinfo else None
            if ptr and re.search(ptrrgx, ptr):
                msgrep = suspect.get_message_rep()
                hdr = msgrep.get('Authentication-Results', '').strip(';')
                if hdr:
                    try:
                        authres.AuthenticationResultsHeader.parse(f'Authentication-Results: {hdr}')
                    except authres.core.SyntaxError:
                        hdr = f'{authhost}; {hdr}'
                    else:
                        fields = hdr.split(';')
                        fields[0] = authhost
                        hdr = ';'.join(fields)
                    if msgrep.get('ARC-Seal'): # previous arc sig found. we trust it passed.
                        hdr = self._authres_insert_arcpass(hdr)
                    self.logger.debug(f'{suspect.id} using previous authres header {hdr}')
                else:
                    self.logger.debug(f'{suspect.id} no previous authres header found')
            else:
                self.logger.debug(f'{suspect.id} ptr {ptr} does not match regex {ptrrgx}')
        else:
            self.logger.debug(f'{suspect.id} ptrrgx is empty or tag {tag} is not True')
        return hdr
    
    
    def _iprev(self, suspect:Suspect):
        # see https://www.rfc-editor.org/rfc/rfc8601#section-2.7.3
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo:
            helo, ip, ptr = clientinfo
            if ptr and ptr != 'unknown':
                return 'pass'
            try:
                dnsptr = revlookup(ip, reraise=True)
                dnsip = lookup(dnsptr, reraise=True)
                if dnsip and ip in dnsip:
                    return 'pass'
                else:
                    return 'fail'
            except FuSERVFAIL:
                return 'temperror'
            except Exception:
                return 'permerror'
        return None
    
    
    def _create_authres_header(self, suspect:Suspect, headerfromdom:str, authhost:str) -> bytes:
        """
        create authentication result header value
        :param suspect: Suspect object
        :param headerfromdom: sender domain as extracted from From header
        :param authhost: name of authentication host (first field of authres header)
        :return: bytes string of authentication header, at least host.example.com;none
        """
        values = [authhost, ]
        spfstate = suspect.get_tag('SPF.status')
        if spfstate and spfstate != 'skipped':
            values.append(f'spf={spfstate} smtp.mailfrom={suspect.from_domain}')
        dkimstate = suspect.get_tag("DKIMVerify.result")
        if dkimstate:
            dkimdomain = suspect.get_tag("DKIMVerify.dkimdomain")
            values.append(f'dkim={dkimstate} header.d={dkimdomain} header.from={headerfromdom}')
        dmarcstate = suspect.get_tag('dmarc.result')
        if dmarcstate and dmarcstate != DMARC_SKIP:
            values.append(f'dmarc={dmarcstate}')
        arcstate = suspect.get_tag('ARCVerify.cv')
        if arcstate:
            values.append(f'arc={arcstate}')
        iprev = self._iprev(suspect)
        if iprev:
            values.append(f'iprev={iprev}')
        if len(values)==1:
            values.append('none')
        hdr = ';'.join(values)
        return force_bString(hdr)
    
    
    def _get_sign_domain(self, suspect:Suspect, headerfromdomain:str) -> str:
        domain = None
        sigkey = self.config.get(self.section, 'signdomain')
        if ':' in sigkey:
            key, value = sigkey.split(':',1)
            if key == 'header' and value.lower() == 'from':
                domain = headerfromdomain
            elif key == 'header':
                domain = extract_from_domain(suspect, header=value)
            elif key == 'static':
                domain = value
            elif key == 'tmpl':
                domain = apply_template(value, suspect, dict(header_from_domain=headerfromdomain))
        return domain
    
    
    def examine(self, suspect):
        if not ARCSIGN_AVAILABLE:
            suspect.debug("dkimpy or authres not available, can not sign ARC")
            self.logger.debug("ARC signing skipped - missing dkimpy or authres library")
            return DUNNO
        
        headerfromdomain = extract_from_domain(suspect)
        domain = self._get_sign_domain(suspect, headerfromdomain)
        selector = apply_template(self.config.get(self.section, 'selector'), suspect, dict(header_from_domain=headerfromdomain))
    
        if domain is None:
            self.logger.debug("%s: Failed to extract From-header domain for ARC signing" % suspect.id)
            return DUNNO
    
        privkeyfile = apply_template(self.config.get(self.section, 'privatekeyfile'), suspect, dict(header_from_domain=headerfromdomain))
        if not os.path.isfile(privkeyfile):
            self.logger.debug("%s: ARC signing failed for domain %s, private key not found: %s" % (suspect.id, headerfromdomain, privkeyfile))
            return DUNNO
    
        with open(privkeyfile, 'br') as f:
            privkeycontent = f.read()
        
        headerconfig = self.config.get(self.section, 'signheaders')
        if headerconfig is None or headerconfig.strip() == '':
            inc_headers = None
        else:
            inc_headers = [force_bString(h.strip().lower()) for h in headerconfig.split(',')]
        
        authhost = get_outgoing_helo(self.config)
        authres_hdr = self._reuse_authres_header(suspect, authhost)
        if authres_hdr is None: # if empty string we use hdr from previous host but none was set
            authres_hdr = self._create_authres_header(suspect, headerfromdomain, authhost)
        suspect.add_header('Authentication-Results', authres_hdr, immediate=True)
        
        source = self._get_source(suspect)
        d = ARC(source, logger=PrependLoggerMsg(self.logger, prepend=suspect.id, maxlevel=logging.INFO))
        try:
            arc_set = d.sign(force_bString(selector), force_bString(domain), privkeycontent, force_bString(authhost), include_headers=inc_headers)
            if not arc_set:
                self.logger.warning(f'{suspect.id} empty ARC signature set')
            else:
                arc_set.reverse()
                for item in arc_set:
                    hdr, val = item.split(b':', 1)
                    suspect.add_header(force_uString(hdr.strip()), force_uString(val.strip()), immediate=True)
        except Exception as de:
            self.logger.warning("%s: ARC signing failed: %s %s" % (suspect.id, de.__class__.__name__, str(de)))
            self.logger.debug(traceback.format_exc())
            
        return DUNNO
    
    
    def lint(self):
        all_ok = self.check_config()
    
        if not DKIMPY_AVAILABLE:
            print("Missing dependency: dkimpy https://launchpad.net/dkimpy")
            all_ok = False
        elif not ARCSIGN_AVAILABLE:
            print("Missing dependency: authres")
        if not DNSQUERY_EXTENSION_ENABLED:
            print("Missing dependency: no supported DNS libary found. pydns or dnspython")
            all_ok = False
    
        # if privkey is a filename (no placeholders) check if it exists
        privkeytemplate = self.config.get(self.section, 'privatekeyfile')
        if '{' not in privkeytemplate and not os.path.exists(privkeytemplate):
            print("Private key file %s not found" % privkeytemplate)
            all_ok = False
        elif os.path.exists(privkeytemplate):
            try:
                with open(privkeytemplate, 'br') as f:
                    privkeycontent = f.read()
            except Exception as e:
                print(f'failed to read private key due to {e.__class__.__name__}: {str(e)}')
                all_ok = False
        
        sigkey = self.config.get(self.section, 'signdomain')
        if not ':' in sigkey:
            print(f'Invalid signdomain config value: {sigkey}')
            all_ok = False
        else:
            key, value = sigkey.split(':',1)
            if key not in ['header', 'static', 'tmpl']:
                print(f'Invalid signdomain value: {sigkey} - {key} should be one of header, static')
                all_ok = False
            elif key == 'static' and not '.' in value:
                print(f'Invalid signdomain value: {sigkey} - {value} should be a valid domain name')
                all_ok = False
            
        return all_ok
    


class DKIMVerifyPlugin(ScannerPlugin):
    """
This plugin checks the DKIM signature of the message and sets tags...
DKIMVerify.sigvalid : True if there was a valid DKIM signature, False if there was an invalid DKIM signature
the tag is not set if there was no dkim header at all

DKIMVerify.skipreason: set if the verification has been skipped

The plugin does not take any action based on the DKIM test result since a failed DKIM validation by itself
should not cause a message to be treated any differently. Other plugins might use the DKIM result
in combination with other factors to take action (for example a "DMARC" plugin could use this information)

It is currently recommended to leave both header and body canonicalization as 'relaxed'. Using 'simple' can cause the signature to fail.
    """

    # set as class variable for simple unit test monkey patching
    DKIM = DKIM
    dkim_dns_func = None

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.skiplist = FileList(filename=None, strip=True, skip_empty=True, skip_comments=True, lowercase=True)
        self.requiredvars = {
            'skiplist': {
                'default': '',
                'description': 'File containing a list of domains (one per line) which are not checked'
            },
        }
    
    
    def __str__(self):
        return "DKIM Verify"
    
    
    def examine(self, suspect):
        if not DKIMPY_AVAILABLE:
            suspect.debug("dkimpy not available, can not check DKIM")
            suspect.set_tag('DKIMVerify.skipreason', 'dkimpy library not available')
            return DUNNO

        hdr_from_domain = extract_from_domain(suspect)
        if not hdr_from_domain:
            self.logger.debug('%s DKIM Verification skipped, no header from address')
            suspect.set_tag("DKIMVerify.skipreason", 'no header from address')
            return DUNNO

        self.skiplist.filename = self.config.get(self.section, 'skiplist')
        skiplist = self.skiplist.get_list()
        if hdr_from_domain in skiplist:
            self.logger.debug('%s DKIM Verification skipped, sender domain skiplisted')
            suspect.set_tag("DKIMVerify.skipreason", 'sender domain skiplisted')
            return DUNNO

        dkimhdrs = suspect.get_message_rep().get_all('dkim-signature')
        if not dkimhdrs:
            self.logger.debug('%s DKIM Verification skipped, no dkim-signature header found')
            suspect.set_tag('DKIMVerify.skipreason', 'not dkim signed')
            suspect.set_tag("DKIMVerify.result", DKIM_NONE)
            suspect.write_sa_temp_header(DKIM_SAHEADER, DKIM_NONE)
            suspect.debug("No dkim signature header found")
            return DUNNO

        valid = False
        dkimdomain = ''
        selector = ''
        is_authordomain = False
        is_senderdomain = False
        dkimval = DKIM_NEUTRAL
        saval = None
        
        source = suspect.get_source()
        env_from_domain = suspect.from_domain.lower()
        try:
            # use the local logger of the plugin but prepend the fuglu id
            d = self.DKIM(source, logger=PrependLoggerMsg(self.logger, prepend=suspect.id, maxlevel=logging.INFO))
            try:
                # one dkim header has to be valid
                # trust priority: d=hdr_from, d=env_from, d=3rdparty
                for i in range(0, len(dkimhdrs)):
                    tags = dkim.util.parse_tag_value(force_bString(dkimhdrs[i]))
                    # wants bytes, returns dict of bytes
                    record_domain = tags.get(b'd', b'').decode().lower()
                    record_selector = tags.get(b's', b'').decode().lower()
                    if self.dkim_dns_func is not None:
                        record_valid = d.verify(idx=i, dnsfunc=self.dkim_dns_func) # in unit tests as dkim module cannot be patched with mock
                    else:
                        record_valid = d.verify(idx=i)
                    if record_valid:
                        valid = True
                        if record_domain == hdr_from_domain or record_domain.endswith(f'.{hdr_from_domain}'):
                            is_authordomain = True
                            dkimval = DKIM_PASS
                            saval = DKIM_PASS_AUTHOR
                            dkimdomain = record_domain
                            selector = record_selector
                            break # highest level of trust, finish evaluation
                        elif not is_authordomain and suspect.from_domain and \
                                (record_domain == env_from_domain or record_domain.endswith(f'.{env_from_domain}')
                            ):
                            is_senderdomain = True
                            dkimval = DKIM_PASS
                            saval = DKIM_PASS_SENDER
                            dkimdomain = record_domain
                            selector = record_selector
                        elif not is_authordomain and not is_senderdomain:
                            dkimval = DKIM_PASS
                            dkimdomain = record_domain
                            selector = record_selector
                    elif not valid:
                        dkimval = DKIM_FAIL
                        dkimdomain = record_domain
                        selector = record_selector
                    self.logger.debug(f"{suspect.id}: DKIM idx={i} valid={valid} domain={record_domain} selector={record_selector} authordomain={is_authordomain} senderdomain={is_senderdomain}")
            except dkim.DKIMException as de:
                self.logger.warning("%s: DKIM validation failed: %s" % (suspect.id, str(de)))
                dkimval = DKIM_PERMFAIL
        except dkim.MessageFormatError as e:
            dkimval = DKIM_NEUTRAL
            self.logger.warning("%s: DKIM validation failed: Message format error" % suspect.id)
            self.logger.debug("%s: %s" % (suspect.id, str(e)))
            suspect.set_tag('DKIMVerify.skipreason', 'plugin error')
        except (TimeoutError, DNS_TIMEOUT) as e:
            dkimval = DKIM_TEMPFAIL
            self.logger.warning("%s: DKIM validation failed due to: %s" % (suspect.id, str(e)))
            suspect.set_tag('DKIMVerify.skipreason', 'plugin error')
        except NameError as e:
            self.logger.warning("%s: DKIM validation failed due to missing dependency: %s" % (suspect.id, str(e)))
            suspect.set_tag('DKIMVerify.skipreason', 'plugin error')
        except Exception as e:
            self.logger.warning("%s: DKIM validation failed: %s %s" % (suspect.id, e.__class__.__name__, str(e)))
            import traceback
            self.logger.debug(f'{suspect.id} {traceback.format_exc()}')
            suspect.set_tag('DKIMVerify.skipreason', 'plugin error')
        
        # also needed e.g. in dmarc
        suspect.set_tag("DKIMVerify.sigvalid", valid)
        suspect.set_tag("DKIMVerify.result", dkimval)
        suspect.set_tag("DKIMVerify.dkimdomain", dkimdomain)
        suspect.set_tag("DKIMVerify.selector", selector)
        suspect.set_tag("DKIMVerify.sigvalidauthor", is_authordomain)
        suspect.set_tag("DKIMVerify.sigvalidsender", is_senderdomain)
        suspect.write_sa_temp_header(DKIM_SAHEADER, saval or dkimval)
        self.logger.debug(f'{suspect.id} DKIM validation complete: valid={valid} domain={dkimdomain} selector={selector} result={saval}')
        return DUNNO
    
    
    def lint(self):
        all_ok = self.check_config()

        if not DKIMPY_AVAILABLE:
            print("Missing dependency: dkimpy https://launchpad.net/dkimpy")
            all_ok = False

        if not DNSQUERY_EXTENSION_ENABLED:
            print("Missing dependency: no supported DNS libary found: pydns or dnspython")
            all_ok = False

        return all_ok


# test:
# plugdummy.py -p ...  domainauth.DKIMSignPlugin -s <sender> -o canonicalizeheaders:relaxed -o canonicalizebody:simple -o signbodylength:False
# cat /tmp/fuglu_dummy_message_out.eml | swaks -f <sender>  -s <server>
# -au <username> -ap <password> -4 -p 587 -tls -d -  -t
# <someuser>@gmail.com


class DKIMSignPlugin(ScannerPlugin):
    """
Add DKIM Signature to outgoing mails

Setting up your keys:

::

    mkdir -p /etc/fuglu/dkim
    domain=example.com
    openssl genrsa -out /etc/fuglu/dkim/${domain}.key 1024
    openssl rsa -in /etc/fuglu/dkim/${domain}.key -out /etc/fuglu/dkim/${domain}.pub -pubout -outform PEM
    # print out the DNS record:
    echo -n "default._domainkey TXT  \\"v=DKIM1; k=rsa; p=" ; cat /etc/fuglu/dkim/${domain}.pub | grep -v 'PUBLIC KEY' | tr -d '\\n' ; echo ";\\""


If fuglu handles both incoming and outgoing mails you should make sure that this plugin is skipped for incoming mails

    """

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.requiredvars = {
            'privatekeyfile': {
                'description': "Location of the private key file. supports standard template variables plus additional ${header_from_domain} which extracts the domain name from the From: -Header",
                'default': "${confdir}/dkim/${header_from_domain}.key",
            },

            'canonicalizeheaders': {
                'description': "Type of header canonicalization (simple or relaxed)",
                'default': "relaxed",
            },

            'canonicalizebody': {
                'description': "Type of body canonicalization (simple or relaxed)",
                'default': "relaxed",
            },

            'selector': {
                'description': 'selector to use when signing, supports templates',
                'default': 'default',
            },

            'signheaders': {
                'description': 'comma separated list of headers to sign. empty string=sign all headers',
                'default': 'From,Reply-To,Subject,Date,To,CC,Resent-Date,Resent-From,Resent-To,Resent-CC,In-Reply-To,References,List-Id,List-Help,List-Unsubscribe,List-Subscribe,List-Post,List-Owner,List-Archive',
            },

            'signbodylength': {
                'description': 'include l= tag in dkim header',
                'default': 'False',
            },
        }

    def __str__(self):
        return "DKIM Sign"

    def examine(self, suspect):
        if not DKIMPY_AVAILABLE:
            suspect.debug("dkimpy not available, can not sign DKIM")
            self.logger.error("DKIM signing skipped - missing dkimpy library")
            return DUNNO

        message = suspect.get_source()
        domain = extract_from_domain(suspect)
        addvalues = dict(header_from_domain=domain)
        selector = apply_template(self.config.get(self.section, 'selector'), suspect, addvalues)

        if domain is None:
            self.logger.debug("%s: Failed to extract From-header domain for DKIM signing" % suspect.id)
            return DUNNO

        privkeyfile = apply_template(self.config.get(self.section, 'privatekeyfile'), suspect, addvalues)
        if not os.path.isfile(privkeyfile):
            self.logger.debug("%s: DKIM signing failed for domain %s, private key not found: %s" % (suspect.id, domain, privkeyfile))
            return DUNNO

        with open(privkeyfile, 'br') as f:
            privkeycontent = f.read()

        canH = dkim.Simple
        canB = dkim.Simple

        if self.config.get(self.section, 'canonicalizeheaders').lower() == 'relaxed':
            canH = dkim.Relaxed
        if self.config.get(self.section, 'canonicalizebody').lower() == 'relaxed':
            canB = dkim.Relaxed
        canon = (canH, canB)
        headerconfig = self.config.get(self.section, 'signheaders')
        if headerconfig is None or headerconfig.strip() == '':
            inc_headers = None
        else:
            inc_headers = headerconfig.strip().split(',')

        blength = self.config.getboolean(self.section, 'signbodylength')

        dkimhdr = dkim.sign(message, force_bString(selector), force_bString(domain), privkeycontent,
                       canonicalize=canon, include_headers=inc_headers, length=blength,
                       logger=suspect.get_tag('debugfile'))
        if dkimhdr.startswith(b'DKIM-Signature: '):
            dkimhdr = dkimhdr[16:]

        suspect.add_header('DKIM-Signature', dkimhdr, immediate=True)
        return DUNNO

    def lint(self):
        all_ok = self.check_config()

        if not DKIMPY_AVAILABLE:
            print("Missing dependency: dkimpy https://launchpad.net/dkimpy")
            all_ok = False
        if not DNSQUERY_EXTENSION_ENABLED:
            print("Missing dependency: no supported DNS libary found. pydns or dnspython")
            all_ok = False

        # if privkey is a filename (no placeholders) check if it exists
        privkeytemplate = self.config.get(self.section, 'privatekeyfile')
        if '{' not in privkeytemplate and not os.path.exists(privkeytemplate):
            print("Private key file %s not found" % privkeytemplate)
            all_ok = False

        return all_ok


class NetworkList(FileList):
    def _parse_lines(self, lines):
        lines = super()._parse_lines(lines)
        return [ipaddress.ip_network(x, False) for x in lines]
    
    def is_listed(self, addr):
        try:
            ipaddr = ipaddress.ip_address(addr)
            for net in self.get_list():
                if ipaddr in net:
                    return True
        except ValueError:
            pass
        return False


class SPFPlugin(ScannerPlugin, BasicMilterPlugin, BMPMailFromMixin, BMPRCPTMixin, BMPEOBMixin):
    """
    =====================
    = Milter RCPT stage =
    =====================
    This plugin performs SPF validation using the pyspf module https://pypi.python.org/pypi/pyspf/
    by default, it just logs the result (test mode)

    to enable actual rejection of messages, add a config option on_<resulttype> with a valid postfix action. eg:

    on_fail = REJECT

    on_{result} = ...
    valid {result} types are: 'pass', 'permerror', 'fail', 'temperror', 'softfail', 'none', and 'neutral'
    you probably want to define REJECT for fail and softfail


    operation mode examples
    -----------------------
    I want to reject all hard fails and accept all soft fails (case 1):
      - do not set domain_selective_spf_file
      - set selective_softfail to False
      - set on_fail to REJECT and on_softfail to DUNNO

    I want to reject all hard fails and all soft fails (case 2):
      - do not set domain selective_spf_file
      - set selective_softfail to False
      - set on_fail to REJECT and on_softfail to REJECT

    I only want to reject select hard and soft fails (case 3):
      - set a domain_selective_spf_file and list the domains to be tested
      - set selective_softfail to False
      - set on_fail to REJECT and on_softfail to REJECT

    I want to reject all hard fails and only selected soft fails (case 4):
      - set a domain_selective_spf_file and list the domains to be tested for soft fail
      - set selective_softfail to True
      - set on_fail to REJECT and on_softfail to REJECT

    I want to reject select hard fails and accept all soft fails (case 5):
      - do not set domain selective_spf_file
      - set selective_softfail to False
      - set on_fail to REJECT and on_softfail to DUNNO

    ==========================
    = NON-Milter stage (EOM) =
    ==========================
    This plugin checks the SPF status and sets tag 'SPF.status' to one of the official states 'pass', 'fail', 'neutral',
    'softfail, 'permerror', 'temperror' or 'skipped' if the SPF check could not be peformed.
    Tag 'SPF.explanation' contains a human readable explanation of the result.
    Additionally information to be used by SA plugin is added

    The plugin does not take any action based on the SPF test result since. Other plugins might use the SPF result
    in combination with other factors to take action (for example a "DMARC" plugin could use this information)

    However, if mark_milter_check=True then the message is marked as spam if the milter stage
    check would reject this (fail or softfail). This feature is to avoid rejecting at milter stage
    but mark later in post-queue mode as spam.
    """

    def __init__(self, config, section=None):
        super().__init__(config, section)
        self.logger = self._logger()
        self.check_cache = Cache()

        self.requiredvars = {
            'ip_whitelist_file': {
                'default': '',
                'description': 'file containing a list of IP adresses or CIDR ranges to be exempted from SPF checks. 127.0.0.0/8 is always exempted',
            },
            'domain_whitelist_file': {
                'default': '',
                'description': 'if this is non-empty, all except sender domains in this file will be checked for SPF. define exceptions by prefixing with ! (e.g. example.com !foo.example.com). define TLD wildcards using * (e.g. example.*)',
            },
            'domain_selective_spf_file': {
                'default': '',
                'description': 'if this is non-empty, only sender domains in this file will be checked for SPF. define exceptions by prefixing with ! (e.g. example.com !foo.example.com). define TLD wildcards using * (e.g. example.*)',
            },
            'ip_selective_spf_file': {
                'default': '',
                'description': 'if this is non-empty, only sender IPs in this file will be checked for SPF. If IP also whitelisted, this is ignored: no check. This has precedence over domain_selective_spf_file',
            },
            'selective_softfail': {
                'default': 'False',
                'description': 'evaluate all senders for hard fails (unless listed in domain_whitelist_file) and only evaluate softfail for domains listed in domain_selective_spf_file',
            },
            'check_subdomain': {
                'default': 'False',
                'description': 'apply checks to subdomain of whitelisted/selective domains',
            },
            'dbconnection': {
                'default': '',
                'description': 'SQLAlchemy Connection string, e.g. mysql://root@localhost/spfcheck?charset=utf8. Leave empty to disable SQL lookups',
            },
            'domain_sql_query': {
                'default': "SELECT check_spf from domain where domain_name=:domain",
                'description': 'get from sql database :domain will be replaced with the actual domain name. must return field check_spf',
            },
            'on_fail': {
                'default': 'DUNNO',
                'description': 'Action for SPF fail. (DUNNO, DEFER, REJECT)',
            },
            'on_fail_dunnotag': {
                'default': '',
                'description': 'If Suspect/Session tag is set, return DUNNO on fail',
            },
            'on_softfail': {
                'default': 'DUNNO',
                'description': 'Action for SPF softfail. (DUNNO, DEFER, REJECT)',
            },
            'on_softfail_dunnotag': {
                'default': '',
                'description': 'If Suspect/Session tag is set, return DUNNO on softfail',
            },
            'messagetemplate': {
                'default': 'SPF ${result} for domain ${from_domain} from ${client_address} : ${explanation}',
                'description': 'reject message template for policy violators'
            },
            'max_lookups': {
                'default': '10',
                'description': 'maximum number of lookups (RFC defaults to 10)',
            },
            'max_lookup_time': {
                'default': '20',
                'description': 'maximum time per DNS lookup (RFC defaults to 20 seconds)',
            },
            'hoster_mx_exception': {
                'default': '.google.com .protection.outlook.com',
                'description': 'always consider pass if mail is sent from servers specified, MX points to this server, and SPF record contains MX directive',
            },
            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },
            'temperror_retries': {
                'default': '3',
                'description': 'maximum number of retries on temp error',
            },
            'temperror_sleep': {
                'default': '3',
                'description': 'waiting interval between retries on temp error',
            },
            'mark_milter_check': {
                'default': 'False',
                'description': '(eom) check milter setup criterias, mark as spam on hit',
            },
            'skip_on_tag': {
                'default': 'welcomelisted.confirmed',
                'description': 'skip check if any of the tags listed evaluates to True',
            },
        }

        self.ip_skiplist_loader = None
        self.selective_ip_loader = None

        self.selective_domain_loader = None
        self.domain_skiplist_loader = None
    
    
    def __check_domain(self, domain, listentry, check_subdomain):
        listed = False
        if listentry == domain:
            listed = True
        elif check_subdomain and domain.endswith(f'.{listentry}'):
            listed = True
        elif listentry.endswith('.*') and fnmatch.fnmatch(domain, listentry):
            listed = True
        elif check_subdomain and listentry.endswith('.*') and fnmatch.fnmatch(domain, f'*.{listentry}'):
            listed = True
        return listed
    
    
    def _domain_in_list(self, domain, domain_list, check_subdomain):
        listed = False

        # check if listed
        for item in domain_list:
            # skip exceptions
            if item.startswith('!'):
                continue
            listed = self.__check_domain(domain, item, check_subdomain)
            if listed:
                break

        # if previous loop said listed, check for exceptions
        if listed:
            for item in domain_list:
                if item.startswith('!'):
                    item = item[1:]
                    listed = not self.__check_domain(domain, item, check_subdomain)
                    if not listed:
                        break

        return listed
    
    
    def _check_domain_skiplist(self, domain: str):
        domain_skiplist_file = self.config.get(self.section, 'domain_whitelist_file').strip()
        if self.domain_skiplist_loader is None:
            if domain_skiplist_file and os.path.exists(domain_skiplist_file):
                self.domain_skiplist_loader = FileList(domain_skiplist_file, lowercase=True)
        if self.domain_skiplist_loader is not None:
            check_subdomain = self.config.getboolean(self.section, 'check_subdomain')
            return self._domain_in_list(domain, self.domain_skiplist_loader.get_list(), check_subdomain)
        return False
    
    
    def _check_domain_selective(self, from_domain: str, sessid: str = "<sessionid>", logmsgs: bool = True) -> bool:
        do_check = self.check_cache.get_cache(from_domain)
        if do_check is not None:
            if logmsgs:
                self.logger.debug(f"{sessid} domain {from_domain} in cache -> set do_check to {do_check}")
            return do_check

        do_check = None
        check_subdomain = self.config.getboolean(self.section, 'check_subdomain')

        domain_skiplist_file = self.config.get(self.section, 'domain_whitelist_file').strip()
        if domain_skiplist_file:
            skiplisted = self._check_domain_skiplist(from_domain)
            if skiplisted:
                do_check = False
            self.logger.debug(f"{sessid} domain {from_domain} skiplisted {skiplisted} -> set do_check to {do_check}")

        if do_check is None:
            selective_sender_domain_file = self.config.get(self.section, 'domain_selective_spf_file').strip()
            if self.selective_domain_loader is None:
                if selective_sender_domain_file and os.path.exists(selective_sender_domain_file):
                    self.selective_domain_loader = FileList(selective_sender_domain_file, lowercase=True)
            if self.selective_domain_loader is not None:
                if self._domain_in_list(from_domain, self.selective_domain_loader.get_list(), check_subdomain):
                    if logmsgs:
                        self.logger.debug(f"{sessid} domain {from_domain} in domain_selective_spf_file -> set do_check to True")
                    do_check = True
            #elif not selective_sender_domain_file:
            #    do_check = True

        if do_check is not False:
            dbconnection = self.config.get(self.section, 'dbconnection').strip()
            sqlquery = self.config.get(self.section, 'domain_sql_query')

            # use DBConfig instead of get_domain_setting
            if dbconnection and SQL_EXTENSION_ENABLED:
                cache = get_default_cache()
                if get_domain_setting(from_domain, dbconnection, sqlquery, cache, self.section, False, self.logger):
                    if logmsgs:
                        self.logger.debug(f"{sessid} domain {from_domain} has spf-dbsetting -> set do_check to True")
                    do_check = True

            elif dbconnection and not SQL_EXTENSION_ENABLED:
                self.logger.error(f'{sessid} dbconnection specified but sqlalchemy not available - skipping db lookup')

        if do_check is None:
            do_check = False

        self.check_cache.put_cache(from_domain, do_check)
        return do_check
    
    
    def _check_ip_skipisted(self, addr):
        if not addr:
            return False
        try:
            ipaddr = ipaddress.ip_address(addr)
        except ValueError:
            self.logger.warning(f'not an ip address: {addr}')
            return False
        
        if not ipaddr.is_global:
            return True

        # check ip whitelist
        ip_skiplist_file = self.config.get(self.section, 'ip_whitelist_file', fallback='').strip()
        if self.ip_skiplist_loader is None:
            if ip_skiplist_file and os.path.exists(ip_skiplist_file):
                self.ip_skiplist_loader = NetworkList(ip_skiplist_file, lowercase=True)
        
        if self.ip_skiplist_loader is not None:
            return self.ip_skiplist_loader.is_listed(addr)
        return False
    
    
    def _check_ip_selective(self, addr):
        ip_selective_file = self.config.get(self.section, 'ip_selective_spf_file', fallback='').strip()
        if self.selective_ip_loader is None:
            if ip_selective_file and os.path.exists(ip_selective_file):
                self.selective_ip_loader = NetworkList(ip_selective_file, lowercase=True)
        
        if self.selective_ip_loader is not None:
            return self.selective_ip_loader.is_listed(addr)
        return False
    
    
    def _check_skip_on_tag(self, suspect):
        tags = self.config.getlist(self.section, 'skip_on_tag')
        for tag in tags:
            if suspect.get_tag(tag, False):
                return tag
        return None

    
    _re_mx = re.compile(r'\s\+?mx(?:/[0-9]{1,3})?\s')
    def _hoster_mx_exception(self, query: spf.query, hosters: tp.List[str], client_name: str) -> bool:
        client_name = client_name.lower().rstrip('.')
        mxrec = None
        spfrec = query.dns_spf(query.d)
        for hoster in hosters:
            hoster_mx = False
            if client_name and client_name.endswith(hoster):
                try:
                    if mxrec is None:
                        mxrec = [mx[1].to_text(True) for mx in query.dns(query.d, 'MX')]
                
                    for mx in mxrec:
                        if mx.endswith(hoster):
                            hoster_mx = True
                            self.logger.debug(f'{query.d} got mx {mx} in hoster {hoster}')
                            break
                except Exception as e:
                    self.logger.error(f'failed to lookup mx record for domain {query.d}: {e.__class__.__name__}: {str(e)}')
            
                if hoster_mx and self._re_mx.search(spfrec):
                    return True
        return False
    
    
    def _spf_lookup(self, query, retries=3):
        result, _, explanation = query.check()
        if result == 'temperror' and retries > 0:
            time.sleep(self.config.getint(self.section, 'temperror_sleep'))
            retries -= 1
            result, explanation = self._spf_lookup(query, retries=retries)
        return result, explanation
    
    
    def run_all_spf_tests(self,
                          sender: tp.Optional[str],
                          helo_name: tp.Optional[str],
                          client_address: tp.Optional[str],
                          client_name: tp.Optional[str],
                          sessid: str = "<sessionid>",
                          catch_exceptions: bool = True,
                          ) -> tp.Tuple[str, str]:
        """run spf check and apply hoster exceptions"""
        
        result = 'none'
        explanation = ''
        query = spf.query(client_address, sender, helo_name)
        try:
            retries = self.config.getint(self.section, 'temperror_retries')
            maxlookups = self.config.getint(self.section, 'max_lookups')
            spf.MAX_LOOKUP = maxlookups
            maxlookuptime = self.config.getint(self.section, 'max_lookup_time')
            spf.MAX_PER_LOOKUP_TIME = maxlookuptime
            if is_ipv6(client_address):
                # ugly hack, but only very few hosts have aaaa records and result in too many permerrors
                spf.MAX_VOID_LOOKUPS = maxlookups
            if client_address and sender:
                result, explanation = self._spf_lookup(query, retries=retries)
                self.logger.debug(f"{sessid} lookup result={result}")
            elif sender:
                self.logger.debug(f'{sessid} skipped SPF check for {sender} because client_address is empty')
            else:
                self.logger.debug(f'{sessid} skipped SPF check because sender is empty')
        except Exception as e:
            if "SERVFAIL" in str(e): # this may be obsolete now
                # info level is enough
                self.logger.info(f'{sessid} failed to check SPF for {sender} due to: {e.__class__.__name__}: {str(e)}')
            else:
                self.logger.error(f'{sessid} failed to check SPF for {sender} due to: {e.__class__.__name__}: {str(e)}')
                self.logger.debug(traceback.format_exc())
            if not catch_exceptions:
                raise Exception(str(e)).with_traceback(e.__traceback__)
        
        hoster_mx_exception = self.config.getlist(self.section, 'hoster_mx_exception', separators=' ', lower=True)
        if hoster_mx_exception and result in ['fail', 'softfail'] and helo_name and helo_name.endswith(tuple(hoster_mx_exception)):
            self.logger.debug(f'{sessid} testing hoster mx exception')
            if self._hoster_mx_exception(query=query, hosters=hoster_mx_exception, client_name=client_name):
                self.logger.debug(f'{sessid} overriding {result} for {sender} due to hoster mx exception')
                result = 'pass'
                explanation = 'hoster mx permit'
        
        if result != 'none':
            self.logger.info(f'{sessid} SPF client={client_address}, sender={sender}, h={helo_name} result={result} : {explanation}')
        return result, explanation
    
    
    def _get_clientinfo(self, suspect):
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is None:
            suspect.debug(f"{suspect.id} client info not available for SPF check")
            helo = ip = revdns = None
        else:
            helo, ip, revdns = clientinfo
        return ip, helo, revdns
    
    
    def _run(self, suspect: Suspect):
        action = DUNNO
        message = None
        suspect.set_tag('SPF.status', 'skipped')
        suspect.set_tag("SPF.explanation", 'no SPF check performed')
        
        if not HAVE_SPF:
            suspect.set_tag("SPF.explanation", 'missing dependency')
            self.logger.debug(f'{suspect.id}: SPF Check skipped, missing dependency')
            return DUNNO, message
        
        skip_tag = self._check_skip_on_tag(suspect)
        if skip_tag is not None:
            suspect.set_tag("SPF.explanation", f'skip on tag {skip_tag}')
            self.logger.debug(f'{suspect.id}: SPF Check skipped, tag {skip_tag} is True')
            return DUNNO, message
        
        if not suspect.from_address:
            suspect.set_tag("SPF.explanation", 'skipped bounce')
            self.logger.debug(f'{suspect.id}: SPF Check skipped, bounce')
            return DUNNO, message
        
        clientip, helo_name, clienthostname = self._get_clientinfo(suspect)
        if clientip is None:
            suspect.set_tag("SPF.explanation", 'could not extract client information')
            self.logger.debug(f"{suspect.id} SPF Check skipped, could not extract client information")
            return DUNNO, message
        
        clientip = force_uString(clientip)
        if self._check_ip_skipisted(clientip):
            suspect.set_tag("SPF.explanation", 'IP skiplisted')
            self.logger.debug(f'{suspect.id}: SPF Check skipped, IP skiplist')
            return DUNNO, message
        
        sender = force_uString(suspect.from_address)
        senderdomain = domain_from_mail(sender).lower()
        
        ip_selective = self._check_ip_selective(clientip)
        domain_skiplisted = self._check_domain_skiplist(senderdomain)
        if domain_skiplisted and not ip_selective:
            suspect.set_tag("SPF.explanation", 'Domain skiplisted')
            self.logger.debug(f'{suspect.id}: SPF Check skipped, Domain skiplist')
            return DUNNO, message
        elif domain_skiplisted and ip_selective:
            self.logger.info(f'{suspect.id} sender={senderdomain} is skiplisted, but ip={clientip} is selective')
        
        domain_selective = self._check_domain_selective(senderdomain)
        selective_softfail = self.config.getboolean(self.section, 'selective_softfail')
        check_selective = self.config.get(self.section, 'domain_selective_spf_file').strip() != ''
        do_check = False
        do_eval = False
        
        if not check_selective and not selective_softfail: # case 1&2 check all domains
            self.logger.debug(f'{suspect.id} sender={senderdomain} check=all softfail=all selected=yes')
            do_check = True
        elif check_selective and not selective_softfail: # case 3&5 check only select domains
            if ip_selective:
                self.logger.debug(f'{suspect.id} sender={senderdomain} check=select softfail=all selected=ip')
                do_check = True
            elif domain_selective:
                self.logger.debug(f'{suspect.id} sender={senderdomain} check=select softfail=all selected=dom')
                do_check = True
            else:
                self.logger.info(f'{suspect.id} sender={senderdomain} check=select softfail=all selected=no')
        elif check_selective and selective_softfail: # case 4 check every domain, evaluate select softfails later
            self.logger.debug(f'{suspect.id} sender={senderdomain} check=select softfail=select selected=yes')
            do_check = True
            do_eval = True
        elif not check_selective and selective_softfail: # this wouldn't make sense
            self.logger.warning(f'{suspect.id} sender={senderdomain} check=all softfail=select selected=no')
        else:
            self.logger.info(f'{suspect.id} sender={senderdomain} check=n/a softfail=n/a selected=no')
        
        result = 'none'
        explanation = 'SPF not checked'
        if do_check:
            helo_name = force_uString(helo_name or '')
            clienthostname = force_uString(clienthostname)
            result, explanation = self.run_all_spf_tests(sender=sender, helo_name=helo_name, client_address=clientip,
                                       client_name=clienthostname, sessid=suspect.id, catch_exceptions=False)
        if do_eval:
            if result == 'softfail' and not domain_selective:
                result = 'none'
                self.logger.debug(f'{suspect.id} resetting SPF softfail for non-selective domain {senderdomain}')
        
        suspect.set_tag("SPF.status", result)
        suspect.set_tag("spf.result", result) # obsolete?
        suspect.set_tag("SPF.explanation", explanation)
        suspect.write_sa_temp_header('X-SPFCheck', result)
        suspect.debug(f"SPF status: {result} ({explanation})")
        self.logger.info(f"{suspect.id} SPF status: {result} ({explanation})")
        
        if self.config.has_option(self.section, f'on_{result}'):
            action = string_to_actioncode(self.config.get(self.section, f'on_{result}'))
            action = self._check_dunnotag(suspect, result, action)
        elif result != 'none':
            self.logger.debug(f'{suspect.id} no config option on_{result}')
        message = apply_template(self.config.get(self.section, 'messagetemplate'), suspect, dict(result=result, explanation=explanation, client_address=clientip))
        
        return action, message
    
    
    def _check_dunnotag(self, suspect, result, action):
        on_softfail_dunnotag = self.config.get(self.section, 'on_softfail_dunnotag')
        if on_softfail_dunnotag and action != DUNNO and result == 'softfail':
            on_softfail_dunnotag_value = suspect.get_tag(on_softfail_dunnotag, None)
            if on_softfail_dunnotag_value:
                self.logger.info(f"{suspect.id} Change from softfail action to DUNNO/CONTINUE due to WL:{on_softfail_dunnotag_value}")
                action = DUNNO
                
        on_fail_dunnotag = self.config.get(self.section, 'on_fail_dunnotag')
        if on_fail_dunnotag and action != DUNNO and result == 'fail':
            on_fail_dunnotag_value = suspect.get_tag(on_fail_dunnotag, None)
            if on_fail_dunnotag_value:
                self.logger.info(f"{suspect.id} Change from fail action to DUNNO/CONTINUE due to WL:{on_fail_dunnotag_value}")
                action = DUNNO
        return action
        
        
    def _run_milter(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], sender: tp.Union[str, bytes], recipient: tp.Union[str, bytes], state: str = None):
        suspect = Suspect(force_uString(sender), force_uString(recipient), '/dev/null', id=sess.id,
                          sasl_login=sess.sasl_login, sasl_sender=sess.sasl_sender, sasl_method=sess.sasl_method,
                          queue_id=sess.queueid,)
        suspect.clientinfo = force_uString(sess.heloname), force_uString(sess.addr), force_uString(sess.ptr)
        suspect.timestamp = sess.timestamp
        suspect.tags = sess.tags
        
        action, message = self._run(suspect)
        
        if state == asm.EOB and action != DUNNO:
            action = self._eob_block_on_reject(suspect, action, message)
        
        outaction = retcode2milter.get(action, None)
        if outaction is None:
            outaction = sm.TEMPFAIL
            message = "temporary SPF evaluation error"
            self.logger.error(f"{sess.id} Couldn't convert return from normal out:{action}({actioncode_to_string(action)}) to milter return!")
        sess.tags['SPF.mresponse'] = (outaction, message)
        return outaction, message
    
    
    def _eob_block_on_reject(self, suspect, action, message):
        if self.config.getboolean(self.section, 'mark_milter_check') and action != DUNNO:
            self.logger.warning(f"{suspect.id} Block because SPF would reject with: {message}")
            blockinfo = {'SPFCheck': message}
            self._blockreport(suspect, blockinfo, enginename='SPFPlugin')
            action = DUNNO
        return action
    
    
    def examine(self, suspect: Suspect) -> tp.Union[int, tp.Tuple[int, tp.Optional[str]]]:
        action, message = self._run(suspect)
        action = self._eob_block_on_reject(suspect, action, message)
        return action, message
    
    def examine_mailfrom(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], sender: str) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._run_milter(sess, sender, b'root@localhost', asm.MAILFROM)
    
    def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        resp = sess.tags.get('SPF.mresponse')
        if resp and len(resp)==2: # reuse result from previous recipient. test result is purely sender based.
            return resp
        return self._run_milter(sess, sess.sender, recipient, asm.RCPT)
    
    def examine_eob(self, sess: tp.Union[asm.MilterSession, sm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._run_milter(sess, sess.sender, sess.to_address, asm.EOB)
    

    def lint(self, state=EOM) -> bool:
        from fuglu.funkyconsole import FunkyConsole
        if state and state not in self.state and state != EOM:
            # not active in current state
            return True

        lint_ok = True
        fc = FunkyConsole()

        if not DNSQUERY_EXTENSION_ENABLED:
            print(fc.strcolor("ERROR: ", "red"), "no dns module installed")
            lint_ok = False

        if not HAVE_SPF:
            print(fc.strcolor("ERROR: ", "red"), "pyspf or dnspython module not installed - this plugin will do nothing")
            lint_ok = False

        if not self.check_config():
            print(fc.strcolor("ERROR: ", "red"), "Error checking config")
            lint_ok = False

        if self.config.has_option(self.section, 'skiplist'):
            print(fc.strcolor("WARNING: ", "yellow"), 'skiplist configured - this is obsolete, use ip_whitelist_file instead')
        
        import configparser
        for result in ["fail", "softfail", "none", "neutral", "pass", "permerr", "temperr"]:
            try:
                configaction = self.config.get(self.section, f'on_{result}')
                if configaction:
                    action = string_to_actioncode(configaction)
                    action = retcode2milter.get(action, None)
                    if not action:
                        lint_ok = False
                        print(fc.strcolor("ERROR: ", "red"), f"'on_{result}'-Action value {configaction}' not in allowed choices: 'DUNNO', 'DEFER', 'REJECT'")
            except configparser.NoOptionError:
                pass
            except Exception as e:
                lint_ok = False
                print(fc.strcolor("ERROR: ", "red"), f'failed to evaluate check result due to {e.__class__.__name__}: {str(e)}')

        domain_skiplist_file = self.config.get(self.section, 'domain_whitelist_file').strip()
        if domain_skiplist_file and not os.path.exists(domain_skiplist_file):
            print(fc.strcolor("WARNING: ", "yellow"), f"domain_whitelist_file {domain_skiplist_file} does not exist")
            lint_ok = False

        selective_sender_domain_file = self.config.get(self.section, 'domain_selective_spf_file').strip()
        if selective_sender_domain_file and not os.path.exists(selective_sender_domain_file):
            print(fc.strcolor("WARNING: ", "yellow"), f"domain_selective_spf_file {selective_sender_domain_file} does not exist")
            lint_ok = False

        if domain_skiplist_file and selective_sender_domain_file:
            print(fc.strcolor("WARNING: ", "yellow"),
                  'domain_whitelist_file and domain_selective_spf_file specified - whitelist '
                  'has precedence, will check all domains and ignore domain_selective_spf_file')

        ip_skiplist_file = self.config.get(self.section, 'ip_whitelist_file').strip()
        if ip_skiplist_file and not os.path.exists(ip_skiplist_file):
            print(fc.strcolor("WARNING: ", "yellow"), f"ip_whitelist_file {ip_skiplist_file} does not exist - IP whitelist is disabled")
            lint_ok = False

        sqlquery = self.config.get(self.section, 'domain_sql_query')
        dbconnection = self.config.get(self.section, 'dbconnection').strip()
        if not SQL_EXTENSION_ENABLED and dbconnection:
            print(fc.strcolor("WARNING: ", "yellow"), "SQLAlchemy not available, cannot use SQL backend")
            lint_ok = False
        elif not dbconnection:
            print(fc.strcolor("INFO: ", "blue"), "No DB connection defined. Disabling SQL backend")
        else:
            if not sqlquery.lower().startswith('select '):
                lint_ok = False
                print(fc.strcolor("ERROR: ", "red"), f"SQL statement must be a SELECT query, got {sqlquery.split()[0]} instead")
            if lint_ok:
                try:
                    conn = get_session(dbconnection)
                    conn.execute(sqlquery, {'domain': 'example.com'})
                except Exception as e:
                    lint_ok = False
                    print(fc.strcolor("ERROR: ", "red"), f'{e.__class__.__name__}: {str(e)}')

        return lint_ok


class DMARCPlugin(ScannerPlugin):
    """
    **EXPERIMENTAL**
    This plugin evaluates DMARC policy of the sender domain.
    
    This plugin depends on tags written by SPFPlugin and DKIMVerifyPlugin, so they must run beforehand.
    """

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        if DOMAINMAGIC_AVAILABLE:
            self.tldmagic = TLDMagic()
        else:
            self.tldmagic = None

        self.requiredvars = {
            'on_reject': {
                'default': 'DUNNO',
                'description': 'Action if DMARC disposition evaluates to "reject". Set to DUNNO if running in after-queue mode.',
            },
            'messagetemplate': {
                'default': 'DMARC diposition of ${header_from_domain} recommends rejection',
                'description': 'reject message template for policy violators'
            },
        }
    
    
    def _query_dmarc(self, domain):
        records = []
        if self.tldmagic is not None:
            domain = self.tldmagic.get_domain(domain)

        hostname = '_dmarc.%s' % domain
        result = lookup(hostname, QTYPE_TXT)
        if result is None:
            return records
        
        for item in result:
            item = item.strip('"')
            if item.lower().startswith('v=dmarc1'):
                record = ' '.join(i.strip('"') for i in item.split()) # fix records like "v=DMARC1;" "p=none;"
                records.append(record)

        return records
    
    
    def _get_dkim_result(self, suspect):
        value = suspect.get_tag("DKIMVerify.result")

        # unsigned should return None
        dkim_value_map = {
            DKIM_PASS: dmarc.DKIM_PASS,
            DKIM_PASS_AUTHOR: dmarc.DKIM_PASS,
            DKIM_PASS_SENDER: dmarc.DKIM_PASS,
            DKIM_FAIL: dmarc.DKIM_FAIL,
            DKIM_PERMFAIL: dmarc.DKIM_PERMFAIL,
            DKIM_TEMPFAIL: dmarc.DKIM_TEMPFAIL,
            DKIM_NEUTRAL: dmarc.DKIM_NEUTRAL,
            DKIM_POLICY: dmarc.DKIM_NEUTRAL,
        }
        dkim_result = dkim_value_map.get(value)
        
        if dkim_result is None:
            dkim_domain = dkim_selector = None
        else:
            dkim_domain = suspect.get_tag("DKIMVerify.dkimdomain")
            dkim_selector = suspect.get_tag("DKIMVerify.selector")
            
        self.logger.debug(f'{suspect.id} dkim result={dkim_result} status={value} domain={dkim_domain} selector={dkim_selector}')
        return dkim_result, dkim_domain, dkim_selector
    
    
    def _get_spf_result(self, suspect):
        status = suspect.get_tag('SPF.status', 'unknown')

        # skipped, unkonwn, none should return None
        spf_value_map = {
            'pass': dmarc.SPF_PASS,
            'softfail': dmarc.SPF_FAIL,
            'fail': dmarc.SPF_FAIL,
            'neutral': dmarc.SPF_NEUTRAL,
            'temperror': dmarc.SPF_TEMPFAIL,
            'permerror': dmarc.SPF_PERMFAIL,
        }
        spf_result = spf_value_map.get(status)
        self.logger.debug('%s spf result=%s status=%s' % (suspect.id, spf_result, status))
        return spf_result
    
    
    def _mk_aspf(self, from_domain, spf_result):
        if spf_result is None:
            aspf = None
        else:
            aspf = dmarc.SPF(domain=from_domain, result=spf_result)
        return aspf
    
    
    def _mk_adkim(self, dkim_domain, dkim_result, dkim_selector):
        if dkim_result is None:
            adkim = None
        else:
            adkim = dmarc.DKIM(domain=dkim_domain, result=dkim_result, selector=dkim_selector)
        return adkim
    
    
    def _do_dmarc_check(self, dmarc_record, header_from_domain, aspf, adkim, suspectid):
        result = None
        dispo = None
        try:
            d = dmarc.DMARC()
            p = d.parse_record(record=dmarc_record, domain=header_from_domain)
            r = d.get_result(p, spf=aspf, dkim=adkim)
            result = r.result
            dispo = r.disposition
        except dmarc.RecordSyntaxError as e:
            self.logger.info('%s invalid DMARC record: %s' % (suspectid, str(e)))
        except ValueError:
            if aspf is not None:
                dbgaspf = '%s;%s' % (aspf.domain, aspf.result)
            else:
                dbgaspf = 'none'
            if adkim is not None:
                dbgadkim = '%s;%s;%s' % (adkim.domain, adkim.result, adkim.selector)
            else:
                dbgadkim = None
            self.logger.error('%s DMARC ValueError: header_from_domain=%s aspf=%s adkim=%s dmarc_record=%s' % (
            suspectid, header_from_domain, dbgaspf, dbgadkim, dmarc_record))
        return result, dispo
    
    
    def examine(self, suspect):
        if not DMARC_AVAILABLE:
            self.logger.debug('%s DMARC check skipped. dmarc library unavailable' % suspect.id)
            return DUNNO
        
        header_from_domain = extract_from_domain(suspect)
        if not header_from_domain:
            suspect.write_sa_temp_header(DMARC_SAHEADER_RESULT, DMARC_SKIP)
            suspect.set_tag('dmarc.result', DMARC_SKIP)
            self.logger.debug('%s no valid domain found in From header' % suspect.id)
            return DUNNO
        
        dmarc_records = self._query_dmarc(header_from_domain)
        dmarc_records_len = len(dmarc_records)
        if dmarc_records_len == 0:
            suspect.write_sa_temp_header(DMARC_SAHEADER_RESULT, DMARC_NONE)
            suspect.set_tag('dmarc.result', DMARC_NONE)
            self.logger.debug('%s no DMARC record found' % suspect.id)
            return DUNNO
        elif dmarc_records_len > 1:
            suspect.write_sa_temp_header(DMARC_SAHEADER_RESULT, DMARC_SKIP)
            suspect.set_tag('dmarc.result', DMARC_RECORDFAIL)
            self.logger.debug(f'{suspect.id} DMARC check failed. too many records count={dmarc_records_len}')
            return DUNNO
        
        spf_result = self._get_spf_result(suspect)
        dkim_result, dkim_domain, dkim_selector = self._get_dkim_result(suspect)

        aspf = self._mk_aspf(suspect.from_domain, spf_result)
        adkim = self._mk_adkim(dkim_domain, dkim_result, dkim_selector)
        result, dispo = self._do_dmarc_check(dmarc_records[0], header_from_domain, aspf, adkim, suspect.id)
        self.logger.debug(f'{suspect.id} dmarc eval with result={result} and dispo={dispo} input spf={spf_result} dkim_result={dkim_result} dkim_domain={dkim_domain} dkim_selector={dkim_selector} ')
        
        if result is None:
            suspect.set_tag('dmarc.result', DMARC_RECORDFAIL)
            suspect.write_sa_temp_header(DMARC_SAHEADER_RESULT, DMARC_RECORDFAIL)
        elif result == dmarc.POLICY_PASS:
            suspect.set_tag('dmarc.result', DMARC_PASS)
            suspect.write_sa_temp_header(DMARC_SAHEADER_RESULT, DMARC_PASS)
        elif result == dmarc.POLICY_FAIL:
            suspect.set_tag('dmarc.result', DMARC_FAIL)
            suspect.write_sa_temp_header(DMARC_SAHEADER_RESULT, DMARC_FAIL)
        
        action = DUNNO
        message = None
        if dispo == dmarc.POLICY_DIS_REJECT:
            action = string_to_actioncode(self.config.get(self.section, 'on_reject'))
            message = apply_template(self.config.get(self.section, 'messagetemplate'), suspect,
                                     dict(header_from_domain=header_from_domain))
            suspect.write_sa_temp_header(DMARC_SAHEADER_DISPO, DMARC_REJECT)
        elif dispo == dmarc.POLICY_DIS_QUARANTINE:
            suspect.write_sa_temp_header(DMARC_SAHEADER_DISPO, DMARC_QUARANTINE)
        
        return action, message
    
    
    def __str__(self):
        return "DMARC"
    
    
    def lint(self):
        all_ok = self.check_config()

        if not DMARC_AVAILABLE:
            print("Missing dependency: dmarc")
            all_ok = False

        if not DNSQUERY_EXTENSION_ENABLED:
            print("Missing dependency: no supported DNS libary found: pydns or dnspython")
            all_ok = False

        return all_ok


class DomainAuthPlugin(ScannerPlugin):
    """
    **EXPERIMENTAL**
    This plugin checks the header from domain against a list of domains which must be authenticated by DKIM and/or SPF.
    This is somewhat similar to DMARC but instead of asking the sender domain for a DMARC policy record this plugin allows you to force authentication on the recipient side.
    
    This plugin depends on tags written by SPFPlugin and DKIMVerifyPlugin, so they must run beforehand.
    """

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section)
        self.requiredvars = {
            'domainsfile': {
                'description': "File containing a list of domains (one per line) which must be DKIM and/or SPF authenticated",
                'default': "${confdir}/auth_required_domains.txt",
            },
            'failaction': {
                'default': 'DUNNO',
                'description': "action if the message doesn't pass authentication (DUNNO, REJECT)",
            },

            'rejectmessage': {
                'default': 'sender domain ${header_from_domain} must pass DKIM and/or SPF authentication',
                'description': "reject message template if running in pre-queue mode",
            },
        }
        self.logger = self._logger()
        self.filelist = FileList(filename=None, strip=True, skip_empty=True, skip_comments=True, lowercase=True)

    def examine(self, suspect):
        self.filelist.filename = self.config.get(self.section, 'domainsfile')
        checkdomains = self.filelist.get_list()

        envelope_sender_domain = suspect.from_domain.lower()
        header_from_domain = extract_from_domain(suspect)
        if header_from_domain is None:
            return

        if header_from_domain not in checkdomains:
            return

        # TODO: do we need a tag from dkim to check if the verified dkim domain
        # actually matches the header from domain?
        dkimresult = suspect.get_tag('DKIMVerify.sigvalid', False)
        if dkimresult is True:
            return DUNNO

        # DKIM failed, check SPF if envelope senderdomain belongs to header
        # from domain
        spfresult = suspect.get_tag('SPF.status', 'unknown')
        if (envelope_sender_domain == header_from_domain or envelope_sender_domain.endswith(
                '.%s' % header_from_domain)) and spfresult == 'pass':
            return DUNNO
        
        actioncode = self._problemcode('failaction')
        values = dict(header_from_domain=header_from_domain)
        message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, values)
        return actioncode, message

    def flag_as_spam(self, suspect):
        suspect.tags['spam']['domainauth'] = True

    def __str__(self):
        return "DomainAuth"

    def lint(self):
        allok = self.check_config() and self.lint_file()
        return allok

    def lint_file(self):
        filename = self.config.get(self.section, 'domainsfile')
        if not os.path.exists(filename):
            print("domains file %s not found" % filename)
            return False
        return True


class SpearPhishPlugin(ScannerPlugin):
    """Mark spear phishing mails as virus

    The spearphish plugin checks if the sender domain in the "From"-Header matches the envelope recipient Domain ("Mail
    from my own domain") but the message uses a different envelope sender domain. This blocks many spearphish attempts.

    Note that this plugin can cause blocks of legitimate mail , for example if the recipient domain is using a third party service
    to send newsletters in their name. Such services often set the customers domain in the from headers but use their own domains in the envelope for
    bounce processing. Use the 'Plugin Skipper' or any other form of whitelisting in such cases.
    """

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section=section)
        self.logger = self._logger()
        self.filelist = FileList(strip=True, skip_empty=True, skip_comments=True, lowercase=True,
                                 additional_filters=None, minimum_time_between_reloads=30)

        self.requiredvars = {
            'domainsfile': {
                'default': '${confdir}/spearphish-domains',
                'description': 'Filename where we load spearphish domains from. One domain per line. If this setting is empty, the check will be applied to all domains.',
            },
            'virusenginename': {
                'default': 'Fuglu SpearPhishing Protection',
                'description': 'Name of this plugins av engine',
            },
            'virusname': {
                'default': 'TRAIT.SPEARPHISH',
                'description': 'Name to use as virus signature',
            },
            'virusaction': {
                'default': 'DEFAULTVIRUSACTION',
                'description': "action if spear phishing attempt is detected (DUNNO, REJECT, DELETE)",
            },
            'rejectmessage': {
                'default': 'threat detected: ${virusname}',
                'description': "reject message template if running in pre-queue mode and virusaction=REJECT",
            },
            'dbconnection': {
                'default': "mysql://root@localhost/spfcheck?charset=utf8",
                'description': 'SQLAlchemy Connection string. Leave empty to disable SQL lookups',
            },
            'domain_sql_query': {
                'default': "SELECT check_spearphish from domain where domain_name=:domain",
                'description': 'get from sql database :domain will be replaced with the actual domain name. must return boolean field check_spearphish',
            },
            'check_display_part': {
                'default': 'False',
                'description': "set to True to also check display part of From header (else email part only)",
            },
            'checkbounces': {
                'default': 'True',
                'description': 'disable this if you want to exclude mail with empty envelope sender (bounces, NDRs, OOO) from being marked as spearphish'
            },
        }

    # this looks like a duplicate of get_domain_setting from extensions.sql
    @deprecated
    def get_domain_setting(self, domain, dbconnection, sqlquery, cache, cachename, default_value=None, logger=None):
        if logger is None:
            logger = logging.getLogger('fuglu.plugins.SpearPhishPlugin.sql')

        cachekey = '%s-%s' % (cachename, domain)
        cached = cache.get_cache(cachekey)
        if cached is not None:
            logger.debug("got cached setting for %s" % domain)
            return cached

        settings = default_value

        try:
            session = get_session(dbconnection)

            # get domain settings
            dom = session.execute(sqlquery, {'domain': domain}).fetchall()

            if not dom and not dom[0] and len(dom[0]) == 0:
                logger.warning(
                    "Can not load domain setting - domain %s not found. Using default settings." % domain)
            else:
                settings = dom[0][0]

            session.close()

        except Exception as e:
            logger.error("Exception while loading setting for %s : %s %s" % (domain, e.__class__.__name__, str(e)))

        cache.put_cache(cachekey, settings)
        logger.debug("refreshed setting for %s" % domain)
        return settings

    def should_we_check_this_domain(self, suspect):
        domainsfile = self.config.get(self.section, 'domainsfile')
        if domainsfile.strip() == '':  # empty config -> check all domains
            return True

        if not os.path.exists(domainsfile):
            return False

        self.filelist.filename = domainsfile
        envelope_recipient_domain = suspect.to_domain.lower()
        checkdomains = self.filelist.get_list()
        if envelope_recipient_domain in checkdomains:
            return True

        dbconnection = self.config.get(self.section, 'dbconnection').strip()
        sqlquery = self.config.get(self.section, 'domain_sql_query')
        do_check = False
        # use DBConfig instead of get_domain_setting
        if dbconnection:
            cache = get_default_cache()
            cachename = self.section
            do_check = self.get_domain_setting(suspect.to_domain, dbconnection, sqlquery, cache, cachename, False,
                                               self.logger)
        return do_check

    def examine(self, suspect):
        if not self.should_we_check_this_domain(suspect):
            return DUNNO
        envelope_recipient_domain = suspect.to_domain.lower()
        envelope_sender_domain = suspect.from_domain.lower()
        if envelope_sender_domain == envelope_recipient_domain or envelope_sender_domain.endswith(
                f'.{envelope_recipient_domain}'):
            return DUNNO  # we only check the message if the env_sender_domain differs. If it's the same it will be caught by other means (like SPF)

        if not self.config.getboolean(self.section, 'checkbounces') and not suspect.from_address:
            return DUNNO

        header_from_domains = extract_from_domains(suspect)
        if header_from_domains is None:
            header_from_domains = []
        self.logger.debug('%s: checking domain %s (source: From header address part)' % (suspect.id, ','.join(header_from_domains)))

        if self.config.getboolean(self.section, 'check_display_part'):
            display_from_domain = extract_from_domain(suspect, get_display_part=True)
            if display_from_domain is not None and display_from_domain not in header_from_domains:
                header_from_domains.append(display_from_domain)
                self.logger.debug('%s: checking domain %s (source: From header display part)' % (suspect.id, display_from_domain))

        actioncode = DUNNO
        message = None

        for header_from_domain in header_from_domains:
            if header_from_domain == envelope_recipient_domain:
                virusname = self.config.get(self.section, 'virusname')
                virusaction = self.config.get(self.section, 'virusaction')
                actioncode = string_to_actioncode(virusaction, self.config)

                logmsg = '%s: spear phish pattern detected, env_rcpt_domain=%s env_sender_domain=%s header_from_domain=%s' % \
                         (suspect.id, envelope_recipient_domain, envelope_sender_domain, header_from_domain)
                self.logger.info(logmsg)
                self.flag_as_phish(suspect, virusname)

                message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect, {'virusname': virusname})
                break

        return actioncode, message

    def flag_as_phish(self, suspect, virusname):
        suspect.tags['%s.virus' % self.config.get(self.section, 'virusenginename')] = {'message content': virusname}
        suspect.tags['virus'][self.config.get(self.section, 'virusenginename')] = True

    def __str__(self):
        return "Spearphish Check"

    def lint(self):
        allok = self.check_config() and self._lint_file() and self._lint_sql()
        return allok

    def _lint_file(self):
        filename = self.config.get(self.section, 'domainsfile')
        if not os.path.exists(filename):
            print("Spearphish domains file %s not found" % filename)
            return False
        return True

    def _lint_sql(self):
        lint_ok = True
        sqlquery = self.config.get(self.section, 'domain_sql_query')
        dbconnection = self.config.get(self.section, 'dbconnection').strip()
        if not SQL_EXTENSION_ENABLED and dbconnection:
            print('SQLAlchemy not available, cannot use SQL backend')
            lint_ok = False
        elif not dbconnection:
            print('No DB connection defined. Disabling SQL backend')
        else:
            if not sqlquery.lower().startswith('select '):
                lint_ok = False
                print('SQL statement must be a SELECT query')
            if lint_ok:
                try:
                    conn = get_session(dbconnection)
                    conn.execute(sqlquery, {'domain': 'example.com'})
                except Exception as e:
                    lint_ok = False
                    print(str(e))
        return lint_ok


class SenderRewriteScheme(ScannerPlugin):
    """
    SRS (Sender Rewriting Scheme) Plugin
    This plugin encrypts envelope sender and decrypts bounce recpient addresses with SRS
    As opposed to postsrsd it decides by RECIPIENT address whether sender address should be rewritten.
    This plugin only works in after queue mode
    
    Required dependencies:
        - pysrs
    Recommended dependencies:
        - sqlalchemy
    """

    def __init__(self, config, section=None):
        ScannerPlugin.__init__(self, config, section=section)
        self.logger = self._logger()

        self.requiredvars = {
            'dbconnection': {
                'default': "mysql://root@localhost/spfcheck?charset=utf8",
                'description': 'SQLAlchemy Connection string. Leave empty to rewrite all senders',
            },

            'domain_sql_query': {
                'default': "SELECT use_srs from domain where domain_name=:domain",
                'description': 'get from sql database :domain will be replaced with the actual domain name. must return field use_srs',
            },

            'forward_domain': {
                'default': 'example.com',
                'description': 'the new envelope sender domain',
            },

            'secret': {
                'default': '',
                'description': 'cryptographic secret. set the same random value on all your machines',
            },

            'maxage': {
                'default': '8',
                'description': 'maximum lifetime of bounces',
            },

            'hashlength': {
                'default': '8',
                'description': 'size of auth code',
            },

            'separator': {
                'default': '=',
                'description': 'SRS token separator',
            },

            'rewrite_header_to': {
                'default': 'True',
                'description': 'set True to rewrite address in To: header in bounce messages (reverse/decrypt mode)',
            },
        }

    def get_sql_setting(self, domain, dbconnection, sqlquery, cache, cachename, default_value=None, logger=None):
        if logger is None:
            logger = logging.getLogger('fuglu.plugins.domainauth.SenderRewriteScheme.sql')

        cachekey = '%s-%s' % (cachename, domain)
        cached = cache.get_cache(cachekey)
        if cached is not None:
            logger.debug("got cached settings for %s" % domain)
            return cached

        settings = default_value

        try:
            session = get_session(dbconnection)

            # get domain settings
            dom = session.execute(sqlquery, {'domain': domain}).fetchall()

            if not dom or not dom[0] or len(dom[0]) == 0:
                logger.debug("Can not load domain settings - domain %s not found. Using default settings." % domain)
            else:
                settings = dom[0][0]

            session.close()

        except Exception as e:
            self.logger.error("Exception while loading settings for %s : %s: %s" % (domain, e.__class__.__name__, str(e)))

            cache.put_cache(cachekey, settings)
        logger.debug("refreshed settings for %s" % domain)
        return settings

    def should_we_rewrite_this_domain(self, suspect):
        forward_domain = self.config.get(self.section, 'forward_domain')
        if suspect.to_domain.lower() == forward_domain:
            return True  # accept for decryption

        dbconnection = self.config.get(self.section, 'dbconnection')
        sqlquery = self.config.get(self.section, 'domain_sql_query')

        if dbconnection.strip() == '':
            return True  # empty config -> rewrite all domains

        cache = get_default_cache()
        cachename = self.section
        setting = self.get_sql_setting(suspect.to_domain, dbconnection, sqlquery, cache, cachename, False, self.logger)
        return setting

    def _init_srs(self):
        secret = self.config.get(self.section, 'secret')
        maxage = self.config.getint(self.section, 'maxage')
        hashlength = self.config.getint(self.section, 'hashlength')
        separator = self.config.get(self.section, 'separator')
        srs = SRS.new(secret=secret, maxage=maxage, hashlength=hashlength, separator=separator, alwaysrewrite=True)
        return srs

    def _update_to_hdr(self, suspect, to_address):
        msgrep = suspect.get_message_rep()
        old_hdr = msgrep.get('To')
        if old_hdr and '<' in old_hdr:
            start = old_hdr.find('<')
            if start < 1:  # malformed header does not contain <> brackets
                start = old_hdr.find(':')  # start >= 0
            name = old_hdr[:start]
            new_hdr = '%s <%s>' % (name, to_address)
        else:
            new_hdr = '<%s>' % to_address

        suspect.set_header('To', new_hdr)

    def examine(self, suspect):
        if not SRS_AVAILABLE:
            return DUNNO

        if not self.should_we_rewrite_this_domain(suspect):
            self.logger.info('SRS: ignoring mail to %s' % suspect.to_address)
            return DUNNO

        if not suspect.from_address:
            self.logger.info('SRS: ignoring bounce message')
            return DUNNO

        srs = self._init_srs()
        forward_domain = self.config.get(self.section, 'forward_domain').lower()
        if suspect.from_domain.lower() == forward_domain and suspect.from_address.lower().startswith('srs'):
            self.logger.info('SRS %s: skipping already signed address %s' % (suspect.id, suspect.from_address))
        elif suspect.to_domain.lower() == forward_domain and suspect.to_address.lower().startswith('srs'):
            orig_rcpt = suspect.to_address
            try:
                recipient = srs.reverse(orig_rcpt)
                suspect.to_address = recipient
                new_rcpts = [recipient if x == orig_rcpt else x for x in suspect.recipients]
                suspect.recipients = new_rcpts
                if self.config.getboolean(self.section, 'rewrite_header_to'):
                    self._update_to_hdr(suspect, recipient)
                self.logger.info('SRS: decrypted bounce address %s to %s' % (orig_rcpt, recipient))
            except Exception as e:
                self.logger.error('SRS: Failed to decrypt %s reason: %s: %s' % (orig_rcpt, e.__class__.__name__, str(e)))
        else:
            orig_sender = suspect.from_address
            try:
                try:
                    sender = srs.forward(orig_sender, forward_domain)
                except AttributeError:
                    # python 3.9 -> deprecated encodestring has been replaced by encodcebytes
                    import base64
                    base64.encodestring = base64.encodebytes
                    sender = srs.forward(orig_sender, forward_domain)
                suspect.from_address = sender
                self.logger.info('SRS: signed %s to %s' % (orig_sender, sender))
            except Exception as e:
                self.logger.error('SRS: Failed to sign %s reason: %s %s' % (orig_sender, e.__class__.__name__, str(e)))

        del srs
        return DUNNO

    def __str__(self):
        return "Sender Rewrite Scheme"

    def lint(self):
        allok = self.check_config()
        if not SRS_AVAILABLE:
            allok = False
            print('SRS library not found')

        if not self.config.get(self.section, 'secret'):
            allok = False
            print('no secret set in config')

        if allok:
            srs = self._init_srs()
            forward_domain = self.config.get(self.section, 'forward_domain')
            try:
                srs.forward('foobar@example.com', forward_domain)
            except AttributeError:
                # python 3.9 -> deprecated encodestring has been replaced by encodcebytes
                import base64
                base64.encodestring = base64.encodebytes
                srs.forward('foobar@example.com', forward_domain)

        sqlquery = self.config.get(self.section, 'domain_sql_query')
        if not sqlquery.lower().startswith('select '):
            allok = False
            print('SQL statement must be a SELECT query')
        if not SQL_EXTENSION_ENABLED:
            allok = False
            print('SQLAlchemy not available, cannot use SQL backend')
        if allok:
            dbconnection = self.config.get(self.section, 'dbconnection')
            if dbconnection.strip() == '':
                print('No DB connection defined. Disabling SQL backend, all addresses will be rewritten.')
            else:
                try:
                    conn = get_session(dbconnection)
                    conn.execute(sqlquery, {'domain': 'example.com'})
                except Exception as e:
                    allok = False
                    print(f'ERROR: {e.__class__.__name__}: {str(e)}')

        return allok


_ipexclude = re.compile(r'^(127|0|10|192\.168|172\.(1[6-9]|[2-3][0-9]|4[0-1])|169\.254|100\.(6[4-9]|[7-9][0-9]|1[0-1][0-9]|12[0-7]))\.')
def get_host_ipaddr(inhostname: tp.Optional[str] = None) -> tp.Optional[str]:
    """
    guess local IP address (or from given host)
    :return: string with an IP address
    """
    dummyhost = "255.255.255.254"
    defaultip = '0.0.0.0'
    
    try:
        hostname = inhostname if inhostname else socket.getfqdn() # ore use get_outgoing_helo ?
        ipguess = [ip for ip in socket.gethostbyname_ex(hostname)[2] if not _ipexclude.match(ip)]
    except (socket.gaierror, UnicodeError):
        # name does not resolve or hostname is empty
        ipguess = []

    if not ipguess and not inhostname:
        ipguess = [[(s.connect((dummyhost, 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]

    myip = (ipguess + [defaultip])[0]
    return myip


class SPFOut(SPFPlugin):
    def __init__(self, config, section=None):
        super().__init__(config, section)

        self.requiredvars.update({
            'ip': {
                'default': '',
                'description': 'IP used for spf check (env: "$VARNAME", empty: from given hostname or extract from machine)',
            },
            'hostname': {
                'default': '',
                'description': 'hostname/helo used for spf check (env: "$VARNAME", empty: extract from machine)',
            },
        })

        self.requiredvars['hoster_mx_exception']['default'] = ''
        self.requiredvars['on_fail']['default'] = 'REJECT'
        self.requiredvars['on_softfail']['default'] = 'REJECT'
        self.requiredvars['messagetemplate']['default'] = 'SPF record for domain ${from_domain} does not include smarthost.'

        self._myip = None
        self._myhostname = None
        self._myhelo = None
        

    def _init_ipnames(self):
        self._myip = None

        inip = self.config.get(self.section, "ip", resolve_env=True)
        inhost = self.config.get(self.section, "hostname", resolve_env=True)
        if not inhost:
            inhost = get_outgoing_helo(self.config)

        if inhost:
            try:
                self._myhelo = inhost
                self._myhostname = inhost
                if inip:
                    self._myip = inip
                else:
                    # get ip from host
                    self._myip = get_host_ipaddr(inhostname=inhost)
                    self.logger.debug('detected local IP address %s from hostname %s' % (self._myip, inhost))
            except Exception as e:
                self.logger.debug(f'failed to detect host information due to {e.__class__.__name__}: {str(e)}')

        if self._myip is None:
            self._myip = get_host_ipaddr()
            self._myhostname = socket.getfqdn() # ore use get_outgoing_helo ?
            self._myhostname = self._myhostname
            self.logger.debug('detected local IP address %s' % self._myip)

    def _get_clientinfo(self, suspect):
        if self._myip is None:
            self._init_ipnames()
            if not self._myip:
                raise ValueError(f"Couldn't extract IP address!")

        return self._myip, self._myhelo, self._myhelo

    def lint(self, state=EOM) -> bool:
        ok = super().lint(state=state)
        self._init_ipnames()
        print(f'INFO: HELO: {self._myhelo} / IP: {self._myip}')
        return ok
