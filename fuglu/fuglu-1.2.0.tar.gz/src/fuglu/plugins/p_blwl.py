# -*- coding: UTF-8 -*-
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
#
import traceback
import typing as tp
from fuglu.shared import PrependerPlugin, AppenderPlugin, SuspectFilter, get_default_cache, Suspect, apply_template, \
    DUNNO, REJECT, DEFER, string_to_actioncode, utcnow
from fuglu.extensions.sql import SQL_EXTENSION_ENABLED, get_session, DBConfig, DeclarativeBase, RESTAPIError, RESTAPIConfig
from fuglu.extensions.redisext import ENABLED as REDIS_EXTENSION_ENABLED, RedisPooledConn, ExpiringCounter, redis
from fuglu.stringencode import force_uString
from fuglu.mshared import BMPRCPTMixin, BasicMilterPlugin, convert_return2milter
import fuglu.connectors.asyncmilterconnector as asm
import fuglu.connectors.milterconnector as sm
from .sa import UserPref, GLOBALSCOPE
from collections import OrderedDict
from operator import attrgetter
import logging
import fnmatch
import ipaddress
import configparser
import os

try:
    from domainmagic.mailaddr import email_normalise_ebl, strip_batv
    from domainmagic.validators import is_email
    DOMAINMAGIC_AVAILABLE = True
except ImportError:
    def is_email(value):
        return True
    DOMAINMAGIC_AVAILABLE = False

try:
    import requests
    requests.packages.urllib3.disable_warnings()
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False



class BlockWelcomeEntry(object):
    TYPE_BLOCK = 'block'
    TYPE_WELCOME = 'welcome'
    SCOPE_ANY = 'any'
    SCOPE_ENV = 'env'
    SCOPE_HDR = 'hdr'
    list_id = 0
    list_type = TYPE_WELCOME
    list_scope = SCOPE_ANY
    sender_addr = None
    sender_host = None
    netmask = -1
    scope = None
    
    block_before_welcome = True
    
    @staticmethod
    def _is_hostname(value):
        try:
            ipaddress.ip_network(value, False)
            return True
        except ValueError:
            return False
    
    def _is_wildcard(self, hostname):
        return hostname and self._is_hostname(hostname) and hostname.startswith('*')
    
    def __init__(self, **kw):
        for key in kw:
            if hasattr(self, key):
                setattr(self, key, kw[key])
    
    def __str__(self):
        return f'<BlockWelcomeEntry id={self.list_id} type={self.list_type} scope={self.scope} addr={self.sender_addr} host={self.sender_host}/{self.netmask}>'
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        if self.scope == other.scope \
            and self.list_type == other.list_type \
            and self.list_scope == other.list_scope \
            and self.sender_addr == other.sender_addr \
            and self.sender_host == other.sender_host \
            and self.scope == other.scope:
            return True
        return False
    
    def __gt__(self, other):
        if self.list_scope < other.list_scope: # 'any' < 'env' < 'hdr'
            return True
        elif self.list_scope > other.list_scope: # 'any' > 'env' > 'hdr'
            return False
        if self.scope is not None and other.scope is not None:
            if self.scope < other.scope: # '$GLOBAL' < '%domain' < 'user@domain'
                return True
            elif self.scope > other.scope: # '$GLOBAL' > '%domain' > 'user@domain'
                return False
        elif self.scope is not None and other.scope is None:
            return True
        elif self.scope is None and other.scope is not None:
            return False
        if self.list_type < other.list_type: # 'block' < 'welcome'
            return self.block_before_welcome
        elif self.list_type > other.list_type: # 'block' > 'welcome'
            return not self.block_before_welcome
        if self.netmask > other.netmask: # larger netmasks have precedence
            return True
        elif self.netmask < other.netmask:
            return False
        if not self._is_wildcard(self.sender_host) and self._is_wildcard(other.sender_host):
            return True
        elif self._is_wildcard(self.sender_host) and not self._is_wildcard(other.sender_host):
            return False
        if self.sender_addr is not None and other.sender_addr is not None:
            if self.sender_addr < other.sender_addr: # '$GLOBAL' < '%domain' < '*.wildcard' < 'user@domain'
                return True
            elif self.sender_addr > other.sender_addr: # '$GLOBAL' > '%domain' > '*.wildcard' > 'user@domain'
                return False
        elif self.sender_addr is not None and other.sender_addr is None:
            return True
        elif self.sender_addr is None and other.sender_addr is not None:
            return False
    
    def __ge__(self, other):
        return self.__eq__(other) or self.__gt__(other)
    
    def __lt__(self, other):
        return not self.__gt__(other)
    
    def __le__(self, other):
        return self.__eq__(other) or self.__lt__(other)
        
        
    
"""
    match algorithm:
    by default: more precise scope wins (and individual wl overrides global bl, but this should be configurable)
    within same scope: asc sort listtype: block before welcome (should be configurable)
    within same listtype: desc sort by bitmask first: prioritise fqdn with more labels and smaller cidr ranges
    within same bitmask: desc sort host: exact match before wildcard
    wichin same fqdn: desc sort sender: exact match before wildcard before bounce before global
    match scope + sender + host
    if sender and host are set: both must hit
    """

if SQL_EXTENSION_ENABLED:
    from sqlalchemy.sql.expression import desc, asc
    from sqlalchemy import Column
    from sqlalchemy.types import Unicode, Integer, TIMESTAMP
    
    class BlockWelcomeTable(DeclarativeBase, BlockWelcomeEntry):
        __tablename__ = 'fuglu_blwl'
        list_id = Column(Integer, primary_key=True)
        list_type = Column(Unicode(30),nullable=False)
        list_scope = Column(Unicode(30),nullable=False)
        sender_addr = Column(Unicode(255),nullable=True)
        sender_host = Column(Unicode(255),nullable=True)
        netmask = Column(Integer, nullable=False)
        scope = Column(Unicode(255),nullable=False)
        lasthit = Column(TIMESTAMP, nullable=True)
        hitcount = Column(Integer, default=0, nullable=False)
        
        def __str__(self):
            return f'<BlockWelcomeTable id={self.list_id} type={self.list_type} scope={self.scope} addr={self.sender_addr} host={self.sender_host}/{self.netmask}>'
else:
    class BlockWelcomeTable(BlockWelcomeEntry):
        pass

WELCOME = 0
BLOCK = 1


class AbstractBackend(object):
    requiredvars = {}
    
    def __init__(self, config, section):
        self.config = config
        self.section = section
        self.engine = self.__class__.__name__
        self.logger = logging.getLogger('fuglu.blwl.backend.%s' % self.engine)
    
    def __str__(self):
        return self.engine
    
    def evaluate(self, suspect):
        raise NotImplementedError
    
    def lint(self):
        raise NotImplementedError
    
    def _add_tag(self, suspect, action):
        if action == WELCOME:
            suspect.tags['welcomelisted'][self.engine] = True
        elif action == BLOCK:
            suspect.tags['blocklisted'][self.engine] = True
        elif action is None:
            self.logger.debug('%s no listing action: %s' % (suspect.id, action))
    
    def _set_global_tag(self, suspect):
        suspect.set_tag('welcomelisted.global', True)
    
    def _get_eval_order(self, suspect, items, have_global=False):
        evalorder = []
        for item in items:
            if item == 'global' and have_global:
                evalorder.append(GLOBALSCOPE)
            elif item == 'domain' and suspect.to_domain:
                evalorder.append(f'%{suspect.to_domain.lower()}')
            elif item == 'user' and suspect.to_address:
                evalorder.append(suspect.to_address.lower())
        return evalorder



class FugluBlockWelcome(AbstractBackend):
    """
    This backend evaluates complex block and welcome lists based on sender, sender host and recipient.
    
    
    minimal table layout:
    list_id, list_type, list_scope, sender_addr, sender_host, netmask, scope
    
    CREATE TABLE `fuglu_blwl` (
      `list_id` int(11) NOT NULL AUTO_INCREMENT,
      `list_type` varchar(30) NOT NULL,
      `list_scope` varchar(30) NOT NULL DEFAULT 'any',
      `sender_addr` varchar(255) DEFAULT NULL,
      `sender_host` varchar(255) DEFAULT NULL,
      `netmask` int(8) NOT NULL DEFAULT -1,
      `scope` varchar(255) NOT NULL,
      `lasthit` timestamp NULL,
      `hitcount` int(11) NOT NULL DEFAULT 0,
      PRIMARY KEY (`list_id`),
      KEY `idx_scope` (`scope`),
      KEY `idx_sort` (`list_type`, `list_scope`, `netmask`, `sender_host`, `sender_addr`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
    
    list_type is varchar and accepts:
    block (unwanted mail)
    welcome (wanted mail)
    
    list_scope is varchar and accepts:
    any (apply listing to envelope sender and header)
    env (apply to envelope sender only)
    hdr (apply to headers only)
    
    sender_addr is varchar and accepts:
    null: any sender
    empty string: bounce
    %domain: any user in domain
    *.domain: any user in recursively matched domain
    user@domain: full address
    
    sender_host is varchar and accepts
    null: any host
    ip address: full ip or first ip in cidr range
    *.fqdn: recursively matching fqdn
    fqdn: full fqdn
    
    netmask is int and accepts:
    -1: if host field is empty
    0-32 for ipv4
    0-128 for ipv6
    1-n for fqdn (number of labels in fqdn, including * or in other words: number of dots + 1)
    
    scope is varchar and accepts:
    $GLOBAL: any recipient
    %domain: any user in domain
    user@domain: full address
    
    match algorithm:
    by default: more precise scope wins (and individual wl overrides global bl, but this should be configurable)
    within same scope: asc sort listtype: block before welcome (should be configurable)
    within same listtype: desc sort by bitmask first: prioritise fqdn with more labels and smaller cidr ranges
    within same bitmask: desc sort host: exact match before wildcard
    wichin same fqdn: desc sort sender: exact match before wildcard before bounce before global
    match scope + sender + host
    if sender and host are set: both must hit
    
    all values (except $GLOBAL) should be lowercase
    
    observe mariadb asc sort order: NULL, '', $, %, *, -, 1, <, a
    """
    requiredvars = {
        'fublwl_dbconnection': {
            'default': '',
            'description': 'sqlalchemy db connection string mysql://user:pass@host/database?charset=utf-8',
        },
        'fublwl_restapi_endpoint': {
            'default': "",
            'description': """REST API endpoint path to block/welcome list""",
        },
        'fublwl_restapi_key_map': {
            'default': "listID:list_id, listType:list_type, listScope:list_scope, senderAddress:sender_addr, senderHost:sender_host, netmask:netmask, scope:scope",
            'description': """map rest:sql keys""",
        },
        'fublwl_usecache':{
            'default':"True",
            'description':'Use Mem Cache. This is recommended. However, if enabled it will take up to fublwl_cache_ttl seconds until listing changes are effective.',
        },
        'fublwl_cache_ttl':{
            'default':"300",
            'description':'how long to keep listing data in memory cache',
        },
        'fublwl_update_hitcount': {
            'default': 'True',
            'description': 'update counter and lasthit timestamp on hits',
        },
        'fublwl_block_before_welcome': {
            'default': 'True',
            'description': 'evaluate blocklist before welcomelist, can be overridden individually in filter settings',
        },
        'fublwl_eval_order': {
            'default': 'user,domain,global',
            'description:': 'in which order to evaluate [global, domain, user] listings. defaults to user before domain before global',
        },
        'fublwl_header_checks': {
            'default': '',
            'description': 'Also check specified FROM-like headers (e.g. From, Sender, Resent-From, ...)'
        },
    }
    
    def __init__(self, config, section):
        super().__init__(config, section)
        self.cache = get_default_cache()
        self.engine = 'BlockWelcome'
    
    
    def _get_sql(self, fugluid) -> tp.Dict[str, tp.List[BlockWelcomeTable]]:
        listings = {}
        connectstring = self.config.get(self.section, 'fublwl_dbconnection')
        if SQL_EXTENSION_ENABLED and connectstring:
            dbsession = get_session(connectstring)
            query = dbsession.query(BlockWelcomeTable)
            #query = query.order_by(desc(BlockWelcomeTable.scope))
            query = query.order_by(desc(BlockWelcomeTable.sender_addr))
            query = query.order_by(desc(BlockWelcomeTable.netmask))
            query = query.order_by(asc(BlockWelcomeTable.sender_host)) # ip before hostname
            query = query.order_by(asc(BlockWelcomeTable.list_type))
            query = query.order_by(asc(BlockWelcomeTable.list_scope))
            for listing in query.all():
                try:
                    listings[listing.scope].append(listing)
                except KeyError:
                    listings[listing.scope] = [listing]
        return listings
    
    
    def _get_rest(self, fugluid) -> tp.Dict[str, tp.List[BlockWelcomeEntry]]:
        listings = {}
        
        restapi_endpoint = self.config.get(self.section, 'fublwl_restapi_endpoint')
        if restapi_endpoint:
            restapi = RESTAPIConfig()
            content = restapi.get(self.config, restapi_endpoint, fugluid)
            
            restapi_key_map = self.config.getlist(self.section, 'fublwl_restapi_key_map')
            key_map = {k:v for (k,v) in [x.split(':') for x in restapi_key_map if ':' in x]} # convert list to tuple list to dict
            for item in content:
                item = {key_map.get(k,k):v for k,v in item.items()} # convert item keys from rest to sql naming
                listing = BlockWelcomeEntry(**item)
                scope = item.get('scope')
                try:
                    listings[scope].append(listing)
                except KeyError:
                    listings[scope] = [listing]
        return listings
    
    
    def _get_listings(self, fugluid: str = "") -> tp.Dict[str, tp.List[tp.Union[BlockWelcomeEntry, BlockWelcomeTable]]]:
        key = 'blwl-fublwl'
        usecache = self.config.getboolean(self.section, 'fublwl_usecache')
        self.logger.debug(f"{fugluid} Get listings, usecache={usecache}")
        listings = {}
        if usecache:
            listings = self.cache.get_cache(key) or {}
            self.logger.debug(f"{fugluid} Got {len(listings)} listings from cache")
        if not listings:
            self.logger.debug(f"{fugluid} No cached listings, get")
            if listings is None:
                listings = {}
            for func in [self._get_sql, self._get_rest]:
                self.logger.debug(f"{fugluid} No cached listings, get using function {func.__name__}")
                items = func(fugluid)
                #self.logger.debug(f"{fugluid} Got items: {items}")
                for scope in items:
                    try:
                        listings[scope].extend(items[scope])
                    except KeyError:
                        listings[scope] = items[scope]
                    self.logger.debug(f"{fugluid} scope={scope} has {len(listings[scope])} elements after adding {len(items[scope])}")
            for scope in listings:
                listings[scope] = sorted(listings[scope])
            if listings:
                cachettl = self.config.getint(self.section, 'fublwl_cache_ttl')
                self.cache.put_cache(key, listings, ttl=cachettl)
        return listings
    
    
    def _subnet_of(self, inner, outer) -> bool:
        try: # python >= 3.7
            subnet_of = getattr(inner, 'subnet_of')
            return subnet_of(outer)
        except TypeError: # check if ipv6 addr is in ipv4 net or vice versa
            return False
        except AttributeError:
            for ip in inner:
                if ip not in outer:
                    return False
        return True
    
    
    def _parse_host(self, listing:tp.Union[BlockWelcomeEntry, BlockWelcomeTable]):
        listing_net = listing_host = None
        try:
            listing_net = ipaddress.ip_network(f'{listing.sender_host}/{listing.netmask}', False)
        except ValueError:
            listing_host = listing.sender_host.lower()
        return listing_net, listing_host
    
    
    def _check_listings(self, check_listings, sender_address, sender_hostname, sender_hostip, listscope, fugluid: str = ""):
        if sender_address:
            sender_address = sender_address.lower()
            sender_domain = sender_address.rsplit('@',1)[-1]
            sender_domain_pct = f'%{sender_domain}'
            sender_domain_dot = f'.{sender_domain}'
        else:
            sender_domain_pct = None
            sender_domain_dot = None
        
        if sender_hostname:
            sender_hostname = sender_hostname.lower()
            sender_hostname_dot = f'.{sender_hostname}'
        else:
            sender_hostname_dot = None
        
        if sender_hostip:
            sender_hostip = ipaddress.ip_network(sender_hostip, False)
        self.logger.debug(f"{fugluid} sender_domain_pct={sender_domain_pct}, sender_domain_dot={sender_domain_dot}, sender_hostip")

        for listing in check_listings:
            #print(f"Check listing: list_scope:{listing.list_scope}, sender_addr:{listing.sender_addr}, sender_host:{listing.sender_host}, sender_netmask:{listing.netmask}")
            if not listing.list_scope in (BlockWelcomeEntry.SCOPE_ANY, listscope):
                self.logger.debug(f"{fugluid} checking listing: {listing} -> skip due to listscope {listing.list_scope} not in scopes {BlockWelcomeEntry.SCOPE_ANY}, {listscope}")
                continue
            if listing.sender_addr is None and listing.sender_host is None: # would allow any sender from any host
                self.logger.debug(f"{fugluid} checking listing: {listing} "
                                  f"-> skip because listing sender address is none ({listing.sender_addr}) "
                                  f"and listing sender host is none ({listing.sender_host})")
                continue
            
            sender_ok = False
            host_ok = False
            
            if listing.sender_addr=='' and not sender_address: # bounces
                sender_ok = True
            elif listing.sender_addr is None: # any sender
                sender_ok = True
            elif listing.sender_addr and sender_address:
                listing_addr = listing.sender_addr.lower()
                if listing_addr == sender_address or listing_addr == sender_domain_pct: # exact match
                    sender_ok = True
                elif sender_domain_dot and listing_addr.startswith('*.') and fnmatch.fnmatch(sender_domain_dot, listing_addr): # wilcard match
                    sender_ok = True
            
            if not sender_ok: # it'll never hit, save some cpu cycles
                self.logger.debug(f"{fugluid} sender not ok skip (listing_sender_addr={listing.sender_addr}, "
                                  f"sender_address={sender_address}")
                continue
            
            if not listing.sender_host: # any host
                host_ok = True
            else:
                listing_net, listing_host = self._parse_host(listing)
                self.logger.debug(f"{fugluid} listing_net={listing_net}, listing_host={listing_host}")
                if sender_hostip and listing_net and self._subnet_of(sender_hostip, listing_net): # ip/cidr match
                    host_ok = True
                elif not listing_net and listing_host and listing_host == sender_hostname: # hostname exact match
                    host_ok = True
                elif not listing_net and listing_host and sender_hostname_dot and listing_host.startswith('*.') and fnmatch.fnmatch(sender_hostname_dot, listing_host):
                    host_ok = True

            if sender_ok and host_ok:
                self.logger.debug(f"{fugluid} sender_ok={sender_ok}, host_ok={host_ok} -> return listing: {listing}")
                return listing
            else:
                self.logger.debug(f"{fugluid} sender_ok={sender_ok}, host_ok={host_ok} -> continue searching for listing")
        return None
    
    
    def _block_before_welcome(self, suspect:Suspect) -> bool:
        block_before_welcome = suspect.get_tag('filtersettings', {}).get('block_before_welcome', None)
        if block_before_welcome is None:
            block_before_welcome = self.config.getboolean(self.section, 'fublwl_block_before_welcome', True)
        return block_before_welcome
    
    
    def _sort_listings(self,
                       suspect: Suspect,
                       all_listings: tp.Dict[str, tp.List[tp.Union[BlockWelcomeEntry, BlockWelcomeTable]]],
                       scopes: tp.List[str]) -> tp.List[tp.Union[BlockWelcomeEntry, BlockWelcomeTable]]:
        block_before_welcome = self._block_before_welcome(suspect)
        check_listings = []
        for scope in scopes:
            scope_listings = all_listings.get(scope, [])
            if scope_listings and not block_before_welcome:
                scope_listings = sorted(scope_listings, key=attrgetter('list_type'), reverse=True)
            check_listings.extend(scope_listings)
        return check_listings
    
    
    def _check_user_listings(self,
                             suspect: Suspect,
                             all_listings: tp.Dict[str, tp.List[tp.Union[BlockWelcomeEntry, BlockWelcomeTable]]]
                             ) -> tp.Tuple[tp.Union[BlockWelcomeEntry, BlockWelcomeTable], str]:
        eval_order = self._get_eval_order(suspect, self.config.getlist(self.section, 'fublwl_eval_order', lower=True), have_global=True)
        check_listings = self._sort_listings(suspect, all_listings, eval_order)
        
        clientinfo = suspect.get_client_info(self.config)
        if clientinfo is not None:
            helo, clientip, clienthostname = clientinfo
        else:
            helo, clientip, clienthostname = None, None, None
        
        sender_address = suspect.from_address
        list_scope = BlockWelcomeEntry.SCOPE_ENV

        #self.logger.debug(f"{suspect.id} Check listings with: sender={sender_address}, clienthostname={clienthostname}, clientip={clientip}, list_scope={list_scope}, listings={check_listings}")
        listing = self._check_listings(check_listings, sender_address, clienthostname, clientip, list_scope, suspect.id)
        self.logger.debug(f"{suspect.id} Check listings returned: {listing} for list_scope {list_scope}")
        if not listing:
            list_scope = BlockWelcomeEntry.SCOPE_HDR
            headers = self.config.getlist(self.section, 'fublwl_header_checks')
            header = None
            for header in headers:
                hdr_addresses = [item[1] for item in suspect.parse_from_type_header(header=header, validate_mail=True)]
                for sender_address in hdr_addresses:
                    listing = self._check_listings(check_listings, sender_address, clienthostname, clientip, list_scope, suspect.id)
                    if listing:
                        break
                if listing:
                    break
            self.logger.debug(f"{suspect.id} Check listings returned: {listing} for list_scope {list_scope} in header {header}")
        return listing, list_scope
    
    
    def _update_hit_count(self, suspect:Suspect, listing:BlockWelcomeTable):
        list_id = listing.list_id
        try:
            connectstring = self.config.get(self.section, 'fublwl_dbconnection')
            if connectstring:
                session = get_session(connectstring)
                listing=session.query(BlockWelcomeTable).filter_by(BlockWelcomeTable.list_id == list_id).first()
                if listing is None:
                    self.logger.warning('%s Cannot update listing with id %s - not found' % (suspect.id, list_id))
                    return
                listing.hitcount+=1
                listing.lasthit=utcnow()
                session.flush()
                session.remove()
        except Exception as e:
            self.logger.error('%s Updating hit count failed: %s' % (suspect.id, str(e)))
    
    
    def _test_listings(self, listings:tp.List[tp.Union[BlockWelcomeTable, BlockWelcomeEntry]]):
        errors = []
        for listing in listings:
            err = None
            if listing.list_type not in (BlockWelcomeEntry.TYPE_BLOCK, BlockWelcomeEntry.TYPE_WELCOME):
                err = 'invalid list_type'
            elif listing.list_scope not in (BlockWelcomeEntry.SCOPE_ANY, BlockWelcomeEntry.SCOPE_ENV, BlockWelcomeEntry.SCOPE_HDR):
                err = 'invalid list_scope'
            elif not (
                    listing.scope == GLOBALSCOPE
                    or (listing.scope.startswith('%') and not '@' in listing.scope)
                    or not listing.scope.startswith('%') and '@' in listing.scope
            ):
                err = 'invalid scope'
            elif listing.sender_addr is None and not listing.sender_host:
                err = 'no sender_addr and no sender_host'
            elif not (
                    listing.sender_addr in [None, '']
                    or (listing.sender_addr.startswith(('%', '*.')) and not '@' in listing.sender_addr)
                    or ('@' in listing.sender_addr and not listing.sender_addr.startswith(('%', '*.')))
            ):
                err = 'invalid sender_addr'
            elif (
                    (not listing.sender_host and listing.netmask != -1)
                    or (listing.sender_host and listing.netmask == -1)
            ):
                err = 'invalid netmask'
            elif listing.sender_host:
                listing_net, listing_host = self._parse_host(listing)
                if listing.sender_host and listing_net is None and listing_host is None:
                    err = 'unparseable sender_host'
                elif listing_host is not None and len(listing_host.split('.')) != listing.netmask:
                    err = 'mismatching sender_host and netmask'
                elif listing_net and isinstance(listing_net, ipaddress.IPv4Address) and listing.netmask > 32:
                    err = 'illegal netmask for ipv4 sender_host'
                elif listing_net and isinstance(listing_net, ipaddress.IPv6Address) and listing.netmask > 128:
                    err = 'illegal netmask for ipv6 sender_host'
            
            if err is not None:
                errors.append((listing, err))
        return errors
        
    
    def lint(self):
        if not SQL_EXTENSION_ENABLED and not self.config.get(self.section, 'fublwl_dbconnection'):
            print('WARNING: SQL extension not enabled, this backend will do nothing')
        
        if not REQUESTS_AVAILABLE and self.config.get('databaseconfig', 'restapi_uri'):
            print('WARNING: requests library not found, REST API cannot be queried')
        
        listings = self._get_listings()
        #suspect = Suspect('sender@fuglu.org', 'recipient@fuglu.org', '/dev/null')
        #eval_order = self._get_eval_order(suspect, self.config.getlist(self.section, 'fublwl_eval_order', lower=True), have_global=True)
        #check_listings = self._sort_listings(suspect, listings, eval_order)
        #print(eval_order)
        #for listing in check_listings:
        #    print(str(listing))
        if listings:
            all_listings = []
            for scope in listings:
                #print(f'{scope} {[str(l) for l in listings[scope]]}')
                all_listings.extend(listings[scope])
            print('INFO: loaded %s listings' % len(all_listings))
            try:
                errors = self._test_listings(all_listings)
                for listing, err in errors:
                    print(f'{err} {str(listing)}')
                if errors:
                    return False
            except Exception:
                print(traceback.format_exc())
                return False
        else:
            print('INFO: no listings loaded')
        return True
    
    
    def evaluate(self, suspect:Suspect):
        if not SQL_EXTENSION_ENABLED and not self.config.get(self.section, 'fublwl_restapi_uri'):
            self.logger.debug(f"{suspect.id} Skip because SQL_EXTENSION is not enabled and fublwl_restapi is not set")
            return
        
        self.logger.debug(f"{suspect.id} Get listings")
        try:
            listings = self._get_listings(fugluid=suspect.id)
            self.logger.debug(f"{suspect.id} Start with {len(listings)} listings")
        except RESTAPIError as e:
            suspect.set_tag('restapi.error', e)
            return
        
        listing, list_scope = self._check_user_listings(suspect, listings)
        self.logger.debug(f"{suspect.id} after applying user -> listing: {listing}, list_scope: {list_scope}")
        
        if listing and listing.list_type == BlockWelcomeEntry.TYPE_BLOCK:
            self._add_tag(suspect, BLOCK)
        elif listing and listing.list_type == BlockWelcomeEntry.TYPE_WELCOME:
            self._add_tag(suspect, WELCOME)
            if listing.scope == GLOBALSCOPE:
                self._set_global_tag(suspect)
            if list_scope == BlockWelcomeEntry.SCOPE_HDR:
                suspect.set_tag('welcomelisted.header', True)
            elif list_scope == BlockWelcomeEntry.SCOPE_ENV and listing.sender_addr and listing.sender_host:
                suspect.set_tag('welcomelisted.confirmed', True) # confirmed listings have both envelope sender address and sender host set
        if listing and self.config.getboolean(self.section, 'fublwl_update_hitcount'):
            self._update_hit_count(suspect, listing)
        if listing:
            self.logger.info('%s hits on listing %s' % (suspect.id, listing))
        else:
            self.logger.info('%s no listing hit' % suspect.id)
            



class FilterSettingsBackend(AbstractBackend):
    """
    This backend reads specific values per recipient/recipient domain from fuglu database config and adds respective tags.
    allows global settings in config file or database.
    configure database configuration in [databaseconfig] section
    """
    
    requiredvars = {
        'fs_section_name': {
            'default': 'FilterSettings',
            'description': 'name of config section',
        },
        'fs_welcome_options': {
            'default': 'disable_filter',
            'description': 'options that act like "welcomelist_to" (boolean values only)',
        },
        'fs_yesno_options': {
            'default': 'deliver_spam, deliver_highspam, block_before_welcome, enforce_tls',
            'description': 'options that enable or disable a feature (boolean values only)',
        },
        'fs_level_options': {
            'default': 'subject_tag_ext_level, max_message_size',
            'description': 'options that set a level or threshold (numeric values only)',
        },
        'fs_value_options': {
            'default': 'spam_recipient, subject_tag_ext, subject_tag_spam, ca_target',
            'description': 'options that describe or configure other settings (text values, allows template variables like ${to_address})',
        },
        
        'subject_tag_ext': {
            'section': 'FilterSettings',
            'default': '[EXTERNAL]',
            'description': 'default subject tag for tagging external messages',
        },
        'subject_tag_ext_level': {
            'section': 'FilterSettings',
            'default': '0',
            'description': 'when to tag external messages: 0 never, 1 always, 2 when sender domain equals recipient domain',
        },
        'subject_tag_spam': {
            'section': 'FilterSettings',
            'default': '[SPAM]',
            'description': 'default subject tag for tagging spam messages',
        },
        'spam_recipient': {
            'section': 'FilterSettings',
            'default': '${to_address}',
            'description': 'default subject tag for tagging spam messages',
        },
        'block_before_welcome': {
            'section': 'FilterSettings',
            'default': 'True',
            'description': 'evaluate blocklist before welcomelist (influences other backends/plugins)',
        },
    }
    
    
    def __init__(self, config, section):
        super().__init__(config, section)
        self.engine = 'FilterSettings'
        
        
    def _add_filtersetting_tag(self, suspect:Suspect, option:str, value:tp.Union[str, float, bool, tp.List[str]]):
        try:
            suspect.tags['filtersettings'][option] = value
        except KeyError:
            suspect.tags['filtersettings'] = {}
            suspect.tags['filtersettings'][option] = value
    
    
    def evaluate(self, suspect:Suspect):
        errors = set()
        dbsection = self.config.get(self.section, 'fs_section_name')
        
        runtimeconfig = DBConfig(self.config, suspect)
        loaded = runtimeconfig.load_section(self.section) # maybe need to catch restapierror here
        if not loaded:
            self.logger.warning(f'{suspect.id} failed to load runtimeconfig, will proceed without cached data')
        
        welcome_options = self.config.getlist(self.section, 'fs_welcome_options', lower=True)
        for option in welcome_options:
            try:
                value = runtimeconfig.getboolean(dbsection, option)
                self._add_filtersetting_tag(suspect, option, value)
                if value:
                    self._add_tag(suspect, WELCOME)
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                errors.add(str(e))
                self.logger.debug(f'{suspect.id} fs_welcome_options {str(e)}')
            except RESTAPIError as e:
                suspect.set_tag('restapi.error', e)

        yesno_options = self.config.getlist(self.section, 'fs_yesno_options', lower=True)
        for option in yesno_options:
            try:
                value = runtimeconfig.getboolean(dbsection, option)
                if value is not None:
                    self._add_filtersetting_tag(suspect, option, value)
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                errors.add(str(e))
                self.logger.debug(f'{suspect.id} fs_yesno_options {str(e)}')
            except RESTAPIError as e:
                suspect.set_tag('restapi.error', e)

        level_options = self.config.getlist(self.section, 'fs_level_options', lower=True)
        for option in level_options:
            try:
                value = runtimeconfig.getfloat(dbsection, option)
                if value is not None:
                    self._add_filtersetting_tag(suspect, option, value)
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                errors.add(str(e))
                self.logger.debug(f'{suspect.id} fs_level_options {str(e)}')
            except RESTAPIError as e:
                suspect.set_tag('restapi.error', e)

        value_options = self.config.getlist(self.section, 'fs_value_options', lower=True)
        for option in value_options:
            try:
                value = runtimeconfig.get(dbsection, option)
                value = apply_template(value, suspect)
                if value is not None:
                    self._add_filtersetting_tag(suspect, option, value)
            except (configparser.NoSectionError, configparser.NoOptionError) as e:
                errors.add(str(e))
                self.logger.debug(f'{suspect.id} fs_value_options {str(e)}')
            except RESTAPIError as e:
                suspect.set_tag('restapi.error', e)
        
        return errors
    
    
    def lint(self):
        if not SQL_EXTENSION_ENABLED:
            print('WARNING: SQL extension not enabled, this backend will not read individual config overrides from databases')
        
        suspect = Suspect('sender@unittests.fuglu.org', 'recipient@unittests.fuglu.org', '/dev/null')
        errors = self.evaluate(suspect)
        fs = suspect.tags.get('filtersettings')
        if fs:
            print('INFO:', fs)
        for error in errors:
            print('WARNING:', error)
        
        return True



class SAUserPrefBackend(AbstractBackend):
    """
    Backend that reads default SpamAssassin UserPref table
    """
    requiredvars = {
        'userpref_dbconnection': {
            'default': '',
            'description': "sqlalchemy db connect string, e.g. mysql:///localhost/spamassassin",
        },
        'userpref_usecache':{
            'default':"True",
            'description':'Use Mem Cache. This is recommended. However, if enabled it will take up to userpref_cache_ttl seconds until listing changes are effective.',
        },
        'userpref_cache_ttl':{
            'default':"300",
            'description':'how long to keep userpref data in memory cache',
        },
        'userpref_block_before_welcome': {
            'default': 'True',
            'description:': 'Does blocklist have precedence over welcome list',
        },
        'userpref_eval_order': {
            'default': 'user,domain,global',
            'description:': 'in which order to evaluate [global, domain, user] listings. defaults to user before domain before global',
        },
    }
    
    
    USERPREF_TYPES = OrderedDict()
    USERPREF_TYPES['whitelist_to'] = {'cmp': ['to_address'], 'act': WELCOME}
    USERPREF_TYPES['welcomelist_to'] = {'cmp': ['to_address'], 'act': WELCOME}
    USERPREF_TYPES['more_spam_to'] = {'cmp': ['to_address'], 'act': WELCOME}
    USERPREF_TYPES['all_spam_to'] = {'cmp': ['to_address'], 'act': WELCOME}
    USERPREF_TYPES['whitelist_from'] = {'cmp': ['from_address', 'from_domain'], 'act': WELCOME}
    USERPREF_TYPES['welcomelist_from'] = {'cmp': ['from_address', 'from_domain'], 'act': WELCOME}
    USERPREF_TYPES['blacklist_to'] = {'cmp': ['to_address'], 'act': BLOCK}
    USERPREF_TYPES['blocklist_to'] = {'cmp': ['to_address'], 'act': BLOCK}
    USERPREF_TYPES['blacklist_from'] = {'cmp': ['from_address', 'from_domain'], 'act': BLOCK}
    USERPREF_TYPES['blocklist_from'] = {'cmp': ['from_address', 'from_domain'], 'act': BLOCK}
    
    
    def __init__(self, config, section):
        super().__init__(config, section)
        self.cache = get_default_cache()
        self.engine = 'UserPref'
    
    
    def __str(self):
        return 'UserPref'
    
    
    def lint(self):
        if not SQL_EXTENSION_ENABLED:
            print('WARNING: SQL extension not enabled, this backend will do nothing')
        
        suspect = Suspect('dummy@example.com', 'dummy@example.com', '/dev/null')
        if not self.config.get(self.section, 'userpref_dbconnection'):
            print('WARNING: spamassassin userprefs enabled but no db connection configured')
            return False
        else:
            try:
                listings = self._get_sa_userpref()
                print('INFO: retrieved %s global/dummy userprefs' % len(listings))
                self._check_sa_userpref(suspect, listings)
            except Exception as e:
                print('ERROR: failed to retrieve spamassassin userpref due to %s' % str(e))
                return False
        return True
    
    
    def _get_sa_userpref(self):
        key = 'blwl-userpref'
        usecache = self.config.getboolean(self.section, 'userpref_usecache')
        listings = OrderedDict()
        if usecache:
            listings = self.cache.get_cache(key) or OrderedDict()
        if not listings:
            dbconn = self.config.get(self.section, 'userpref_dbconnection')
            if not dbconn:
                self.logger.debug('userpref_dbconnection not set')
                return listings
            
            dbsession = get_session(dbconn)
            query = dbsession.query(UserPref)
            query = query.filter(UserPref.preference.in_(list(self.USERPREF_TYPES.keys())))
            query = query.order_by(desc(UserPref.username))
            result = query.all()
            for r in result:
                listing_type = r.preference
                if not listing_type in listings:
                    listings[listing_type] = {}
                username = r.username
                if username.startswith('*@'):  # roundcube sauserprefs plugin domain wide scope
                    username = username.lstrip('*@')
                    username = f'%{username}'
                try:
                    listings[listing_type][username].append(r.value)
                except KeyError:
                    listings[listing_type][username] = [r.value]
            if listings:
                cachettl = self.config.getint(self.section, 'userpref_cache_ttl')
                self.cache.put_cache(key, listings, ttl=cachettl)
        return listings
    
    
    def _compare_sa_userpref(self, listings, listtype, user, value):
        if not listings:
            return False
        
        try:
            userlistings = listings[listtype].get(user, [])
        except KeyError:
            return False
        
        for l in userlistings:
            if fnmatch.fnmatch(value, l):
                listed = True
                break
        else:
            listed = False
        return listed
    
    
    def _get_pref_order(self, suspect:Suspect, listings):
        block_before_welcome = suspect.get_tag('filtersettings', {}).get('block_before_welcome', None)
        if block_before_welcome is None:
            block_before_welcome = self.config.getboolean(self.section, 'userpref_block_before_welcome')
        if block_before_welcome:
            return list(listings.keys())
        else:
            return reversed(list(listings.keys()))
    
    
    def _check_sa_userpref(self, suspect:Suspect, listings):
        if not listings:
            return
        
        items = [i.lower() for i in self.config.getlist(self.section, 'userpref_eval_order')]
        eval_order = self._get_eval_order(suspect, items, have_global=True)
        pref_order = self._get_pref_order(suspect, listings)
        
        for preference in pref_order:
            check = self.USERPREF_TYPES[preference]
            act = check['act']
            for cmp in check['cmp']:
                cmp_value = getattr(suspect, cmp)
                for scope in eval_order:
                    listed = self._compare_sa_userpref(listings, preference, scope, cmp_value)
                    if listed:
                        blocktype = 'block' if act == WELCOME else 'welcome'
                        self.logger.debug('%s userpref hit pref=%s scope=%s val=%s type=%s' % (
                        suspect.id, preference, scope, cmp_value, blocktype))
                        if scope == GLOBALSCOPE and act == WELCOME:
                            self._set_global_tag(suspect)
                        elif act == BLOCK:
                            suspect.set_tag('blocklisted.preference', preference)
                            suspect.set_tag('blocklisted.scope', scope)
                            suspect.set_tag('blocklisted.value', cmp_value)
                        return act
        return None
    
    
    def evaluate(self, suspect:Suspect):
        if not SQL_EXTENSION_ENABLED:
            return
        
        try:
            listings = self._get_sa_userpref()
        except Exception as e:
            listings = None
            self.logger.error('%s failed to retrieve userprefs due to %s' % (suspect.id, str(e)))
        
        action = self._check_sa_userpref(suspect, listings)
        self._add_tag(suspect, action)


class StaticBackend(AbstractBackend):
    requiredvars = {
        'static_recipients_welcome': {
            'default': '',
            'description': "list of recipients that to which all mail is supposed to be welcome",
        },
        'static_senders_welcome': {
            'default': '',
            'description': "list of senders that are always welcomelisted (domains or full addresses)",
        },
        'static_senders_blocked': {
            'default': '',
            'description': "list of senders that are always blocked (domains or full addresses)",
        },
    }
    
    def evaluate(self, suspect:Suspect):
        recipients_welcome = self.config.getlist(self.section, 'static_recipients_welcome')
        for recipient in suspect.recipients:
            if recipient in recipients_welcome or recipient.rsplit('@',1)[-1] in recipients_welcome:
                self.logger.info(f'{suspect.id} is welcome (rcpt={recipient})')
                self._add_tag(suspect, WELCOME)
                self._set_global_tag(suspect)
                break
        else:
            if recipients_welcome:
                self.logger.debug(f'{suspect.id} is not in recipients welcome list {",".join(recipients_welcome)}')
        
        senders_welcome = self.config.getlist(self.section, 'static_senders_welcome')
        if suspect.from_address in senders_welcome or suspect.from_domain in senders_welcome:
            self.logger.info(f'{suspect.id} is welcome (sender={suspect.from_address})')
            self._add_tag(suspect, WELCOME)
            self._set_global_tag(suspect)
        elif senders_welcome:
            self.logger.debug(f'{suspect.id} is not in senders welcome list {",".join(senders_welcome)}')
            
        senders_blocked = self.config.getlist(self.section, 'static_senders_blocked')
        if suspect.from_address in senders_blocked or suspect.from_domain in senders_blocked:
            self.logger.info(f'{suspect.id} is blocked')
            self._add_tag(suspect, BLOCK)
        elif senders_blocked:
            self.logger.debug(f'{suspect.id} is not in senders blocked list {",".join(senders_welcome)}')

    def lint(self):
        return True



class AutoListMixin(object):
    config = None
    section = None
    requiredvars = {
        'redis_conn': {
            'default': 'redis://127.0.0.1:6379/1',
            'description': 'the redis database connection URI: redis://host:port/dbid',
        },
        'redis_ttl': {
            'default': str(7 * 24 * 3600),
            'description': 'TTL in seconds',
        },
        'timeout': {
            'default': '2',
            'description': 'redis timeout in seconds'
        },
        'pinginterval': {
            'default': '0',
            'description': 'ping redis interval to prevent disconnect (0: don\'t ping)'
        },
        'skip_headers': {
            'default': '',
            'description': 'list of headers which disable autlist if header is found',
        },
        'threshold': {
            'default': '50',
            'description': 'threshold for auto welcomelisting',
        },
        'max_count': {
            'default': '1000',
            'description': 'do not increase counter beyond this value (for performance reasons)'
        }
    }
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backend_redis = None
    
    
    def _envelope_skip(self, envelope_sender:str, envelope_recipient:str):
        if envelope_recipient is None or envelope_sender is None or envelope_sender==envelope_recipient:
            return True
        if envelope_sender in ['', '<>'] or envelope_recipient == '' or not is_email(envelope_sender or not is_email(envelope_recipient)):
            return True
        return False
    
    
    def _header_skip(self, suspect: Suspect):
        """Check if evaluation should be skipped due to header in skiplist"""
        try:
            headers_list = self.config.getlist(self.section, 'skip_headers')
            msrep = suspect.get_message_rep()
            for h in headers_list:
                if msrep.get(h, None):
                    return h
        except Exception:
            pass
        return None


    def _init_backend_redis(self):
        """
        Init Redis backend if not yet setup.
        """
        if self.backend_redis is not None:
            return
        redis_conn = self.config.get(self.section, 'redis_conn')
        if redis_conn:
            ttl = self.config.getint(self.section, 'redis_ttl')
            socket_timeout = self.config.getint(self.section, 'timeout'),
            pinginterval = self.config.getint(self.section, 'pinginterval')
            redis_pool = RedisPooledConn(redis_conn, socket_keepalive=True, socket_timeout=socket_timeout, pinginterval=pinginterval)
            maxcount = self.config.getint(self.section, 'max_count')
            self.backend_redis = ExpiringCounter(redis_pool, ttl, maxcount=maxcount)
    
    
    def _address_normalise(self, address:str) -> str:
        if DOMAINMAGIC_AVAILABLE or not address:
            return force_uString(strip_batv(email_normalise_ebl(address)))
        else:
            return address
    
    
    def _gen_key(self, sender:str, recipient:str) -> str:
        # rcpt first to allow more efficient search by rcpt
        return '%s\n%s' % (recipient, sender)
    
    
    def lint(self):
        if not DOMAINMAGIC_AVAILABLE:
            print('WARNING: domainmagic not available')
        
        if not REDIS_EXTENSION_ENABLED:
            print('ERROR: redis not available')
            return False
        
        ok = True
        try:
            self._init_backend_redis()
            reply = self.backend_redis.redis_pool.check_connection()
            if reply:
                print("OK: redis server replied to ping")
            else:
                ok = False
                print("ERROR: redis server did not reply to ping")

        except redis.exceptions.ConnectionError as e:
            ok = False
            print(f"ERROR: failed to talk to redis server: {str(e)}")
        except Exception as e:
            ok = False
            print(f"ERROR: failed to connect to redis: {str(e)}")
            import traceback
            traceback.print_exc()
        return ok



class AutoListBackend(AbstractBackend, AutoListMixin):
    requiredvars={
        'threshold': {
            'default': '50',
            'description': 'threshold for auto welcomelisting',
        },
        'sa_headername': {
            'default': 'X-AutoWL-Lvl',
            'description': 'header name for SpamAssassin',
        },
    }
    requiredvars.update(AutoListMixin.requiredvars)
    
    def __init__(self, config, section):
        AbstractBackend.__init__(self, config, section)
        AutoListMixin.__init__(self)
        self.engine = 'AutoList'
    
    
    def evaluate(self, suspect:Suspect):
        if not REDIS_EXTENSION_ENABLED:
            return
        if suspect.is_welcomelisted() or suspect.is_blocklisted():
            return
        envelope_sender = self._address_normalise(suspect.from_address)
        envelope_recipient = self._address_normalise(suspect.to_address)
        if self._envelope_skip(envelope_sender, envelope_recipient):
            self.logger.info(f'{suspect.id} Skipped due to envelope sender={envelope_sender} recipient={envelope_recipient}')
            return
        header = self._header_skip(suspect)
        if header:
            self.logger.info(f'{suspect.id} Skipped due to header {header}')
            return
        
        rediskey = self._gen_key(envelope_sender, envelope_recipient)
        
        count = 0
        attempts = 2
        while attempts:
            attempts -= 1
            try:
                self._init_backend_redis()
                if self.backend_redis:
                    count = self.backend_redis.get_count(rediskey)
            except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                msg = f'{suspect.id} failed to connect to redis server (retry={bool(attempts)}): {str(e)}'
                if attempts:
                    self.logger.warning(msg)
                    self.backend_redis = None
                else:
                    self.logger.error(msg)
                    return
        
        if count is not None and count > 0:
            if count > self.config.getint(self.section, 'threshold'):
                self._add_tag(suspect, WELCOME)
            headername = self.config.get(self.section, 'sa_headername')
            if headername:
                suspect.write_sa_temp_header(headername, count)
            self.logger.info("%s mail from %s to %s seen %s times" % (suspect.id, envelope_sender, envelope_recipient, count))
        else:
            self.logger.debug("%s mail from %s to %s seen %s times" % (suspect.id, envelope_sender, envelope_recipient, 0))
    
    
    def lint(self):
        return AutoListMixin.lint(self)


BLWL_BACKENDS = OrderedDict()
BLWL_BACKENDS['fublwl'] = FugluBlockWelcome
BLWL_BACKENDS['filtersettings'] = FilterSettingsBackend
BLWL_BACKENDS['userpref'] = SAUserPrefBackend
BLWL_BACKENDS['static'] = StaticBackend
BLWL_BACKENDS['autolist'] = AutoListBackend


class BlockWelcomeList(PrependerPlugin):
    """
    This plugin evaluates block and welcome lists, e.g. from spamassassin userprefs.
    Respective tags if a sender/recipient combination is welcome listed or block listed are written.
    use e.g. p_skipper.PluginSkipper to skip certain checks or create a custom plugin to decide further action
    """
    
    def __init__(self, config, section=None):
        PrependerPlugin.__init__(self, config, section)
        self.logger = self._logger()
        self.backends = None
        self.filter = None
        self.requiredvars = {
            'blwl_backends': {
                'default': '',
                'description': 'comma separated list of backends to use. available backends: %s' % ', '.join(list(BLWL_BACKENDS.keys())),
            },
            'skipfile': {
                'default': '',
                'description':  """Skip following backends if a certain SuspectFilter criteria is met
                                @tagname    value   backendname
                                """,
            },
        }
        for backend_name in BLWL_BACKENDS:
            self.requiredvars.update(BLWL_BACKENDS[backend_name].requiredvars)
    
    
    def __str__(self):
        return "Block and welcome list evaluation plugin"
    
    
    def _load_backends(self):
        self.backends = OrderedDict()
        backend_names = self.config.getlist(self.section, 'blwl_backends')
        for backend_name in backend_names:
            try:
                backendclass = BLWL_BACKENDS[backend_name]
                backend = backendclass(self.config, self.section)
                self.backends[backend_name] = backend
            except KeyError:
                self.logger.error(f'invalid backend name {backend_name}')
    
    
    def _initfilter(self):
        if self.filter is not None:
            return True

        filename = self.config.get(self.section, 'skipfile')
        if filename is None or filename == "":
            return False

        if not os.path.exists(filename):
            self.logger.error('Skipfile not found: %s' % filename)
            return False

        self.filter = SuspectFilter(filename)
        return True
    
    
    def _skip_backend(self, suspect:Suspect, backendname) -> bool:
        if not self._initfilter():
            return False
        match, backends = self.filter.matches(suspect)
        if match:
            backendlist = [b.strip() for b in backends.split(',')]
            if backendname in backendlist:
                return True
        return False
    
    
    def _run_backends(self, suspect:Suspect):
        if self.backends is None:
            self._load_backends()
        self.logger.debug(f"{suspect.id} available backends: {', '.join(list(self.backends.keys()))}")
        for backend_name in self.backends:
            if self._skip_backend(suspect, backend_name):
                self.logger.debug(f"{suspect.id} skipping backend: {backend_name}")
                continue
            self.logger.debug(f"{suspect.id} evaluating backend: {backend_name}")
            backend = self.backends[backend_name]
            try:
                backend.evaluate(suspect)
            except RESTAPIError as e:
                suspect.set_tag('restapi.error', e)
            except Exception as e:
                self.logger.debug(traceback.format_exc())
                self.logger.error('%s backend %s failed to evaluate due to %s: %s' % (suspect.id, backend_name, e.__class__.__name__, str(e)))
    
    
    def pluginlist(self, suspect:Suspect, pluginlist):
        self._run_backends(suspect)
        return pluginlist
    
    
    def lint(self):
        ok = self.check_config()
        if ok:
            self._load_backends()
            print('loaded backends: %s' % ', '.join(self.backends.keys()))
            for backend_name in self.backends:
                backend = self.backends[backend_name]
                backend_ok = backend.lint()
                if not backend_ok:
                    ok = False
        return ok



class BlockWelcomeMilter(BMPRCPTMixin, BasicMilterPlugin, BlockWelcomeList):
    def __init__(self, config, section=None):
        super().__init__(config, section=section)
        BlockWelcomeList.__init__(self, config, section)
        self.logger = self._logger()
        
        requiredvars = {
            'welcomeaction': {
                'default': 'DUNNO',
                'description': "default action on welcome list hit (usually DUNNO or ACCEPT - ACCEPT will end milter processing)",
            },
            
            'rejectmessage': {
                'default': 'message identified as spam',
                'description': "reject message template if running in milter mode",
            },

            'state': {
                'default': asm.RCPT,
                'description': f'comma/space separated list states this plugin should be '
                               f'applied ({",".join(BasicMilterPlugin.ALL_STATES.keys())})'
            },
    
            'wltagname': {
                'default': 'skipmplugins',
                'description': 'tagname in case of WL hit (empty: don\'t set, skipmplugins to skip milter plugins)'
            },
            
            'wltagvalue': {
                'default': '',
                'description': 'tag content in case of WL hit (empty: don\'t set)'
            },
        }
        self.requiredvars.update(requiredvars)
    
    
    async def examine_rcpt(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._examine(sess, recipient)
    
    async def examine_eoh(self, sess: tp.Union[asm.MilterSession, sm.MilterSession]) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        return self._examine(sess, sess.to_address)
    
    def _examine(self, sess: tp.Union[asm.MilterSession, sm.MilterSession], recipient: bytes) -> tp.Union[bytes, tp.Tuple[bytes, str]]:
        self.logger.debug(f"{sess.id} -> examine with recipient: {force_uString(recipient)}")
        suspect = Suspect(force_uString(sess.sender), force_uString(recipient), '/dev/null', id=sess.id,
                          sasl_login=sess.sasl_login, sasl_sender=sess.sasl_sender, sasl_method=sess.sasl_method,
                              queue_id=sess.queueid,)
        suspect.clientinfo = force_uString(sess.heloname), force_uString(sess.addr), force_uString(sess.ptr)
        suspect.timestamp = sess.timestamp
        suspect.tags = sess.tags # pass by reference - any tag change in suspect should be reflected in session
        suspect.source = b''
        for hdr, val in sess.original_headers:
            suspect.add_header(hdr, val, True)
        
        stageaction = DUNNO
        message = None
        try:
            self._run_backends(suspect)
            if suspect.is_blocklisted():
                stageaction = REJECT
                message = apply_template(self.config.get(self.section, 'rejectmessage'), suspect)
            elif suspect.is_welcomelisted():
                stageaction = string_to_actioncode(self.config.get(self.section, 'welcomeaction'), self.config)
                
                wltag = self.config.get(self.section, 'wltagvalue')
                wlname = self.config.get(self.section, 'wltagname')
                if wlname and wltag:
                    self.logger.info(f"{sess.id} -> welcomelisting, tags defined, skip -> {wlname}:{wltag}")
                    stageaction = DUNNO
                    if wlname in sess.tags:
                        sess.tags[wlname] = f"{sess.tags[wlname]},{wltag}"
                    else:
                        sess.tags[wlname] = wltag
        except RESTAPIError:
            stageaction = DEFER
            message = 'Internal Server Error'

        return convert_return2milter((stageaction, message))



class AutoListAppender(AppenderPlugin, AutoListMixin):
    
    def __init__(self, config, section=None):
        AppenderPlugin.__init__(self, config, section)
        AutoListMixin.__init__(self)
        self.logger = self._logger()
        
        self.requiredvars = {
            'max_sa_score': {
                'default': '3',
                'description': 'do not count mail with SpamAssassin score higher than this'
            },
            'increment': {
                'default': '1',
                'description': 'increase counter by this value',
            },
            'increment_trusted': {
                'default': '10',
                'description': 'increase counter by this value for "outbound" mail',
            },
            'trustedport': {
                'default': '10099',
                'description': 'messages incoming on this port will be considered to be "outbound"',
            },
        }
        self.requiredvars.update(AutoListMixin.requiredvars)
    
    
    def _get_spamscore(self, suspect:Suspect):
        spamscore = suspect.get_tag('SpamAssassin.score')
        if spamscore is None or suspect.get_tag('SpamAssassin.skipreason') is not None:
            score = 0
        else:
            try:
                score = float(spamscore)
            except ValueError:
                score = 5
        return score
    
    
    def process(self, suspect:Suspect, decision):
        if not REDIS_EXTENSION_ENABLED:
            return
        
        if not suspect.is_ham():
            self.logger.debug(f'{suspect.id} Skipped non ham message')
            return
            
        header = self._header_skip(suspect)
        if header:
            self.logger.debug(f'{suspect.id} Skipped due to header {header}')
            return
        
        sascore = self._get_spamscore(suspect)
        if sascore > self.config.getfloat(self.section, 'max_sa_score'):
            self.logger.debug("%s Skipped due to spam score %s" % (suspect.id, sascore))
            return
        
        envelope_sender = self._address_normalise(suspect.from_address)
        for recipient in suspect.recipients:
            envelope_recipient = self._address_normalise(recipient)
            
            if self._envelope_skip(envelope_sender, envelope_recipient):
                self.logger.debug(f'{suspect.id} Skipped due to envelope sender={envelope_sender} recipient={envelope_recipient}')
                return
            
            if self.config.getint(self.section, 'trustedport') == suspect.get_tag('incomingport'):
                self.logger.debug("%s mail received on trusted port %s with sascore %s" % (suspect.id, suspect.get_tag('incomingport'), sascore))
                rediskey = self._gen_key(envelope_recipient, envelope_sender)
                increment = self.config.getint(self.section, 'increment_trusted')
            else:
                self.logger.debug("%s mail received on non-trusted port %s with sascore %s" % (suspect.id, suspect.get_tag('incomingport'), sascore))
                rediskey = self._gen_key(envelope_sender, envelope_recipient)
                increment = self.config.getint(self.section, 'increment')
            
            attempts = 2
            while attempts:
                attempts -= 1
                try:
                    self._init_backend_redis()
                    if self.backend_redis:
                        result = self.backend_redis.increase(rediskey, increment)
                        if result == 0:
                            self.logger.error(f'{suspect.id} failed to register mail from {envelope_sender} to {envelope_recipient} due to TimeoutError in backend (result==0)')
                        else:
                            self.logger.debug(f"{suspect.id} mail from {envelope_sender} to {envelope_recipient} registered with result {result}")
                    attempts = 0
                except redis.exceptions.TimeoutError as e:
                    # don't retry here...
                    self.logger.error(f'{suspect.id} failed to register mail from {envelope_sender} to {envelope_recipient} due to {str(e)}')
                    attempts = 0
                except redis.exceptions.ConnectionError as e:
                    # retry possible for connection errors
                    msg = f'{suspect.id} (retry={bool(attempts)})failed to register mail from {envelope_sender} to {envelope_recipient} due to {str(e)}, resetting connection'
                    self.logger.warning(msg) if attempts else self.logger.error(msg)
                    self.backend_redis = None
    
    
    def lint(self):
        return AutoListMixin.lint(self)
