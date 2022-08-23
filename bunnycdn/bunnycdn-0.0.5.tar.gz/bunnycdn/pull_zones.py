import requests
from bunnycdn.errors import ValidationError
from bunnycdn import BUNNY_API_ENDPOINT
from bunnycdn.utils import (
    get_access_key,
    handle_response,
)

def list_pull_zones(page:int = 0, per_page:int = 1000, include_cert: bool = False) -> dict:
    """ List pull zones """
    if include_cert:
        cert = 'true'
    else:
        cert = 'false'
    url = f"{BUNNY_API_ENDPOINT}/pullzone?page={page}&perPage={per_page}&includeCertificate={cert}"
    headers = {
        "Accept": "application/json",
        "AccessKey": get_access_key(),
    }
    res = requests.get(url, headers=headers)
    return handle_response(res)

def add_pull_zone(
    name: str,
    origin_url: str = None,
    allowed_referers: list = [],
    blocked_referers: list = [],
    blocked_ips: list = [],
    enable_geo_zone_us: bool = None,
    enable_geo_zone_eu: bool = None,
    enable_geo_zone_asia: bool = None,
    enable_geo_zone_sa: bool = None,
    enable_geo_zone_af: bool = None,
    block_root_path_access: bool = None,
    block_post_requests: bool = None,
    enable_query_string_ordering: bool = None,
    enable_webp_vary: bool = None,
    enable_avif_vary: bool = None,
    enable_mobile_vary: bool = None,
    enable_country_code_vary: bool = None,
    enable_hostname_vary: bool = None,
    enable_cache_slice: bool = None,
    zone_security_enabled: bool = None,
    zone_security_include_hash_remote_ip: bool = None,
    ignore_query_strings: bool = None,
    monthly_bandwidth_limit: int = None,
    access_control_origin_header_extensions: list = [],
    enable_access_control_origin_header: bool = None,
    disable_cookies: bool = None,
    budget_redirected_countries: list = [],
    blocked_countries: list = [],
    cache_control_max_age_override: int = None,
    cache_control_browser_max_age_override: int = None,
    add_host_header: bool = None,
    add_canonical_header: bool = None,
    enable_logging: bool = None,
    logging_ip_anonymization_enabled: bool = None,
    perma_cache_storage_zone_id: int = None,
    aws_signing_enabled: bool = None,
    aws_signing_key: str = None,
    aws_signing_secret: str = None,
    aws_signing_region_name: str = None,
    enable_origin_shield: bool = None,
    origin_shield_zone_code: str = None,
    enable_tls_1: bool = None,
    enable_tls_1_1: bool = None,
    cache_error_responses: bool = None,
    verify_origin_ssl: bool = None,
    log_forwarding_enabled: bool = None,
    log_forwarding_hostname: str = None,
    log_forwarding_port: int = None,
    log_forwarding_token: str = None,
    log_forwarding_protocol: int = None, # 0, 1, 2, 3
    logging_save_to_storage: bool = None,
    logging_storage_zone_id: int = None,
    follow_redirects: bool = None,
    connection_limit_per_ip_count: int = None,
    request_limit: int = None,
    limit_rate_after: float = None,
    limit_rate_per_second: int = None,
    burst_size: int = None,
    waf_enabled: bool = None,
    waf_disabled_rule_groups: list = [],
    waf_disabled_rules: list = [],
    waf_enable_request_header_logging: bool = None,
    waf_request_header_ignores: list = [],
    error_page_enable_custom_code: bool = None,
    error_page_custom_code: str = None,
    error_page_enable_status_page_widget: bool = None,
    error_page_status_page_code: str = None,
    error_page_whitelabel: bool = None,
    optimizer_enabled: bool = None,
    optimizer_desktop_max_width: int = None,
    optimizer_mobile_max_width: int = None,
    optimizer_image_quality: int = None,
    optimizer_mobile_image_quality: int = None,
    optimizer_enable_webp: bool = None,
    optimizer_enable_manipulation_engine: bool = None,
    optimizer_minify_css: bool = None,
    optimizer_minify_js: bool = None,
    optimizer_watermark_enabled: bool = None,
    optimizer_watermark_url: str = None,
    optimizer_watermark_position: int = None,
    optimizer_wartermark_offset: float = None,
    optimizer_watermark_min_image_size: int = None,
    optimizer_automatic_optimization_enabled: bool = None,
    optimizer_classes: list = [],
    optimizer_force_classes: bool = None,
    type: int = 1, # 0 or 1 (0 = premium, 1 = volume)
    origin_retries: int = None,
    origin_connect_timeout: int = None,
    origin_response_timeout: int = None,
    use_stale_while_updating: bool = None,
    use_stale_while_offline: bool = None,
    origin_retry_5xx_responses: bool = None,
    origin_retry_connection_timeout: bool = None,
    origin_retry_response_timeout: bool = None,
    origin_retry_delay: int = None,
    dns_origin_port: int = None,
    dns_origin_scheme: str = None,
    query_string_vary_parameters: list = [],
    origin_shield_enable_concurrency_limit: bool = None,
    origin_shield_max_concurrent_requests: int = None,
    enable_cookie_vary: bool = None,
    cookie_vary_parameters: list = [],
    enable_safe_hop: bool = None,
    origin_shield_queue_max_wait_time: int = None,
    origin_shield_max_queued_requests: int = None,
    use_background_update: bool = None,
    enable_auto_ssl: bool = None,
    log_anonymization_type: int = None,
    storage_zone_id: int = None,
    edge_script_id: int = None,
    origin_type: int = 0, # 0,1,2,3,4  (0 = standard (bunny.net origin), 1 = standard, )
    log_format: int = None,
    log_forwarding_format: int = None,
    shield_ddos_protection_type: int = None,
    shield_ddos_protection_enabled: bool = None,
    origin_host_header: str = None,
    enable_smart_cache: bool = None,
    enable_request_coalescing: bool = None,
    request_coalescing_timeout: int = None,
    ):

    url = f"{BUNNY_API_ENDPOINT}/pullzone"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'AccessKey': get_access_key(),
    }

    payload = { "Name": name, "Type": type }

    # TODO: add better validation to this

    if origin_url is None and storage_zone_id is None:
        raise ValidationError("either origin_url or storage_zone_id is required")
    
    if origin_url is not None and storage_zone_id is not None:
        raise ValidationError("either origin_url or storage_zone_id is required")

    if origin_url is not None:
        payload["OriginUrl"] = origin_url

    if len(allowed_referers) > 0:
        payload["AllowedReferers"] = allowed_referers
    
    if len(blocked_referers) > 0:
        payload["BlockedReferers"] = blocked_referers
    
    if len(blocked_ips) > 0:
        payload["BlockedIps"] = blocked_ips
    
    if enable_geo_zone_us is not None:
        payload["EnableGeoZoneUS"] = enable_geo_zone_us
    
    if enable_geo_zone_eu is not None:
        payload["EnableGeoZoneEU"] = enable_geo_zone_eu
    
    if enable_geo_zone_asia is not None:
        payload["EnableGeoZoneASIA"] = enable_geo_zone_asia
    
    if enable_geo_zone_sa is not None:
        payload["EnableGeoZoneSA"] = enable_geo_zone_sa
    
    if enable_geo_zone_af is not None:
        payload["EnableGeoZoneAF"] = enable_geo_zone_af
    
    if block_root_path_access is not None:
        payload["BlockRootPathAccess"] = block_root_path_access
    
    if block_post_requests is not None:
        payload["BlockPostRequests"] = block_post_requests
    
    if enable_query_string_ordering is not None:
        payload["EnableQueryStringOrdering"] = enable_query_string_ordering
    
    if enable_webp_vary is not None:
        payload["EnableWebpVary"] = enable_webp_vary
    
    if enable_avif_vary is not None:
        payload["EnableAvifVary"] = enable_avif_vary
    
    if enable_mobile_vary is not None:
        payload["EnableMobileVary"] = enable_mobile_vary
    
    if enable_country_code_vary is not None:
        payload["EnableCountryCodeVary"] = enable_country_code_vary
    
    if enable_hostname_vary is not None:
        payload["EnableHostnameVary"] = enable_hostname_vary
    
    if enable_cache_slice is not None:
        payload["EnableCacheSlice"] = enable_cache_slice
    
    if zone_security_enabled is not None:
        payload["ZoneSecurityEnabled"] = zone_security_enabled
    
    if zone_security_include_hash_remote_ip is not None:
        payload["ZoneSecurityIncludeHashRemoteIP"] = zone_security_include_hash_remote_ip
    
    if ignore_query_strings is not None:
        payload["IgnoreQueryStrings"] = ignore_query_strings
    
    if monthly_bandwidth_limit is not None:
        payload["MonthlyBandwidthLimit"] = monthly_bandwidth_limit
    
    if len(access_control_origin_header_extensions) > 0:
        payload["AccessControlOriginHeaderExtensions"] = access_control_origin_header_extensions
    
    if enable_access_control_origin_header is not None:
        payload["EnableAccessControlOriginHeader"] = enable_access_control_origin_header
    
    if disable_cookies is not None:
        payload["DisableCookies"] = disable_cookies
    
    if len(budget_redirected_countries) > 0:
        payload["BudgetRedirectedCountries"] = budget_redirected_countries
    
    if len(blocked_countries) > 0:
        payload["BlockedCountries"] = blocked_countries
    
    if cache_control_max_age_override is not None:
        payload["CacheControlMaxAgeOverride"] = cache_control_max_age_override
    
    if cache_control_browser_max_age_override is not None:
        payload["CacheControlBrowserMaxAgeOverride"] = cache_control_browser_max_age_override
    
    if add_host_header is not None:
        payload["AddHostHeader"] = add_host_header
    
    if add_canonical_header is not None:
        payload["AddCanonicalHeader"] = add_canonical_header
    
    if enable_logging is not None:
        payload["EnableLogging"] = enable_logging
    
    if logging_ip_anonymization_enabled is not None:
        payload["LoggingIPAnonymizationEnabled"] = logging_ip_anonymization_enabled
    
    if perma_cache_storage_zone_id is not None:
        payload["PermaCacheStorageZoneId"] = perma_cache_storage_zone_id
    
    if aws_signing_enabled is not None:
        payload["AWSSigningEnabled"] = aws_signing_enabled
    
    if aws_signing_key is not None:
        payload["AWSSigningKey"] = aws_signing_key
    
    if aws_signing_region_name is not None:
        payload["AWSSigningRegionName"] = aws_signing_region_name

    if aws_signing_secret is not None:
        payload["AWSSigningSecret"] = aws_signing_secret
    
    if enable_origin_shield is not None:
        payload["EnableOriginShield"] = enable_origin_shield
    
    if origin_shield_zone_code is not None:
        payload["OriginShieldZoneCode"] = origin_shield_zone_code
    
    if enable_tls_1 is not None:
        payload["EnableTLS1"] = enable_tls_1
    
    if enable_tls_1_1 is not None:
        payload["EnableTLS1_1"] = enable_tls_1_1
    
    if cache_error_responses is not None:
        payload["CacheErrorResponses"] = cache_error_responses
    
    if verify_origin_ssl is not None:
        payload["VerifyOriginSSL"] = verify_origin_ssl
    
    if log_forwarding_enabled is not None:
        payload["LogForwardingEnabled"] = log_forwarding_enabled
    
    if log_forwarding_hostname is not None:
        payload["LogForwardingHostname"] = log_forwarding_hostname
    
    if log_forwarding_port is not None:
        payload["LogForwardingPort"] = log_forwarding_port
    
    if log_forwarding_token is not None:
        payload["LogForwardingToken"] = log_forwarding_token
    
    if log_forwarding_protocol is not None:
        payload["LogForwardingProtocol"] = log_forwarding_protocol
    
    if logging_save_to_storage is not None:
        payload["LoggingSaveToStorage"] = logging_save_to_storage
    
    if logging_storage_zone_id is not None:
        payload["LoggingStorageZoneId"] = logging_storage_zone_id
    
    if follow_redirects is not None:
        payload["FollowRedirects"] = follow_redirects
    
    if connection_limit_per_ip_count is not None:
        payload["ConnectionLimitPerIPCount"] = connection_limit_per_ip_count
    
    if request_limit is not None:
        payload["RequestLimit"] = request_limit
    
    if limit_rate_after is not None:
        payload["LimitRateAfter"] = limit_rate_after
    
    if limit_rate_per_second is not None:
        payload["LimitRatePerSecond"] = limit_rate_per_second
    
    if burst_size is not None:
        payload["BurstSize"] = burst_size
    
    if waf_enabled is not None:
        payload["WAFEnabled"] = waf_enabled
    
    if len(waf_disabled_rule_groups) > 0:
        payload["WAFDisabledRuleGroups"] = waf_disabled_rule_groups
    
    if len(waf_disabled_rules) > 0:
        payload["WAFDisabledRules"] = waf_disabled_rules
    
    if waf_enable_request_header_logging is not None:
        payload["WAFEnableRequestHeaderLogging"] = waf_enable_request_header_logging
    
    if len(waf_request_header_ignores) > 0:
        payload["WAFRequestHeaderIgnores"] = waf_request_header_ignores
    
    if error_page_enable_custom_code is not None:
        payload["ErrorPageEnableCustomCode"] = error_page_enable_custom_code

    if error_page_custom_code is not None:
        payload["ErrorPageCustomCode"] = error_page_custom_code
    
    if error_page_enable_status_page_widget is not None:
        payload["ErrorPageEnableStatusPageWidget"] = error_page_enable_status_page_widget
    
    if error_page_status_page_code is not None:
        payload["ErrorPageStatuspageCode"] = error_page_status_page_code
    
    if error_page_whitelabel is not None:
        payload["ErrorPageWhitelabel"] = error_page_whitelabel
    
    if optimizer_enabled is not None:
        payload["OptimizerEnabled"] = optimizer_enabled
    
    if optimizer_desktop_max_width is not None:
        payload["OptimizerDesktopMaxWidth"] = optimizer_desktop_max_width
    
    if optimizer_mobile_max_width is not None:
        payload["OptimizerMobileMaxWidth"] = optimizer_mobile_max_width
    
    if optimizer_image_quality is not None:
        payload["OptimizerImageQuality"] = optimizer_image_quality
    
    if optimizer_mobile_image_quality is not None:
        payload["OptimizerMobileImageQuality"] = optimizer_mobile_image_quality
    
    if optimizer_enable_webp is not None:
        payload["OptimizerEnableWebp"] = optimizer_enable_webp
    
    if optimizer_enable_manipulation_engine is not None:
        payload["OptimizerEnableManipulationEngine"] = optimizer_enable_manipulation_engine
    
    if optimizer_minify_css is not None:
        payload["OptimizerMinifyCSS"] = optimizer_minify_css
    
    if optimizer_minify_js is not None:
        payload["OptimizerMinifyJavaScript"] = optimizer_minify_js
    
    if optimizer_watermark_enabled is not None:
        payload["OptimizerWatermarkEnabled"] = optimizer_watermark_enabled
    
    if optimizer_watermark_url is not None:
        payload["OptimizerWatermarkURL"] = optimizer_watermark_url
    
    if optimizer_watermark_position is not None:
        payload["OptimizerWatermarkPosition"] = optimizer_watermark_position
    
    if optimizer_wartermark_offset is not None:
        payload["OptimizerWatermarkOffset"] = optimizer_wartermark_offset
    
    if optimizer_watermark_min_image_size is not None:
        payload["OptimizerWatermarkMinImageSize"] = optimizer_watermark_min_image_size
    
    if optimizer_automatic_optimization_enabled is not None:
        payload["OptimizerAutomaticOptimizationEnabled"] = optimizer_automatic_optimization_enabled
    
    if optimizer_classes is not None:
        payload["OptimizerClasses"] = optimizer_classes
    
    if optimizer_force_classes is not None:
        payload["OptimizerForceClasses"] = optimizer_force_classes
    
    if origin_retries is not None:
        payload["OriginRetries"] = origin_retries
    
    if origin_connect_timeout is not None:
        payload["OriginConnectTimeout"] = origin_connect_timeout
    
    if origin_response_timeout is not None:
        payload["OriginResponseTimeout"] = origin_response_timeout
    
    if use_stale_while_updating is not None:
        payload["UseStaleWhileUpdating"] = use_stale_while_updating
    
    if use_stale_while_offline is not None:
        payload["UseStaleWhileOffline"] = use_stale_while_offline
    
    if origin_retry_5xx_responses is not None:
        payload["OriginRetry5xxResponses"] = origin_retry_5xx_responses
    
    if origin_retry_connection_timeout is not None:
        payload["OriginRetryConnectionTimeout"] = origin_retry_connection_timeout
    
    if origin_retry_response_timeout is not None:
        payload["OriginRetryResponseTimeout"] = origin_retry_response_timeout
    
    if origin_retry_delay is not None:
        payload["OriginRetryDelay"] = origin_retry_delay
    
    if dns_origin_port is not None:
        payload["DNSOriginPort"] = dns_origin_port
    
    if dns_origin_scheme is not None:
        payload["DNSOriginScheme"] = dns_origin_scheme
    
    if len(query_string_vary_parameters) > 0:
        payload["QueryStringVaryParameters"] = query_string_vary_parameters
    
    if origin_shield_enable_concurrency_limit is not None:
        payload["OriginShieldEnableConcurrencyLimit"] = origin_shield_enable_concurrency_limit
    
    if origin_shield_max_concurrent_requests is not None:
        payload["OriginShieldMaxConcurrentRequests"] = origin_shield_max_concurrent_requests
    
    if enable_cookie_vary is not None:
        payload["EnableCookieVary"] = enable_cookie_vary
    
    if len(cookie_vary_parameters) > 0:
        payload["CookieVaryParameters"] = cookie_vary_parameters
    
    if enable_safe_hop is not None:
        payload["EnableSafeHops"] = enable_safe_hop
    
    if origin_shield_queue_max_wait_time is not None:
        payload["OriginShieldQueueMaxWaitTime"] = origin_shield_queue_max_wait_time
    
    if origin_shield_max_queued_requests is not None:
        payload["OriginShieldMaxQueuedRequests"] = origin_shield_max_queued_requests
    
    if use_background_update is not None:
        payload["UseBackgroundUpdate"] = use_background_update
    
    if enable_auto_ssl is not None:
        payload["EnableAutoSSL"] = enable_auto_ssl
    
    if log_anonymization_type is not None:
        payload["LogAnonymizationType"] = log_anonymization_type
    
    if storage_zone_id is not None:
        payload["StorageZoneID"] = storage_zone_id
    
    if edge_script_id is not None:
        payload["EdgeScriptID"] = edge_script_id
    
    if origin_type is not None:
        payload["OriginType"] = origin_type
    
    if log_format is not None:
        payload["LogFormat"] = log_format
    
    if log_forwarding_format is not None:
        payload["LogForwardingFormat"] = log_forwarding_format
    
    if shield_ddos_protection_type is not None:
        payload["ShieldDDOSProtectionType"] = shield_ddos_protection_type

    if shield_ddos_protection_enabled is not None:
        payload["ShieldDDOSProtectionEnabled"] = shield_ddos_protection_enabled

    if origin_host_header is not None:
        payload["OriginHostHeader"] = origin_host_header

    if enable_smart_cache is not None:
        payload["EnableSmartCache"] = enable_smart_cache

    if enable_request_coalescing is not None:
        payload["EnableRequestCoalescing"] = enable_request_coalescing

    if request_coalescing_timeout is not None:
        payload["RequestCoalescingTimeout"] = request_coalescing_timeout    

    res = requests.post(url, headers=headers, json=payload)

    return handle_response(res)

def get_pull_zone_by_id(pull_zone_id: int, include_cert: bool = None) -> dict:
    """ Get pull zone by id """
    if include_cert:
        cert = 'true'
    else:
        cert = 'false'
    url = f"{BUNNY_API_ENDPOINT}/pullzone/{pull_zone_id}?includeCertificate={cert}"
    headers = {
        "Accept": "application/json",
        "AccessKey": get_access_key(),
    }
    res = requests.get(url, headers=headers)
    return handle_response(res)

def update_pull_zone(
    pull_zone_id: int,
    origin_url: str = None,
    allowed_referers: list = [],
    blocked_referers: list = [],
    blocked_ips: list = [],
    enable_geo_zone_us: bool = None,
    enable_geo_zone_eu: bool = None,
    enable_geo_zone_asia: bool = None,
    enable_geo_zone_sa: bool = None,
    enable_geo_zone_af: bool = None,
    block_root_path_access: bool = None,
    block_post_requests: bool = None,
    enable_query_string_ordering: bool = None,
    enable_webp_vary: bool = None,
    enable_avif_vary: bool = None,
    enable_mobile_vary: bool = None,
    enable_country_code_vary: bool = None,
    enable_hostname_vary: bool = None,
    enable_cache_slice: bool = None,
    zone_security_enabled: bool = None,
    zone_security_include_hash_remote_ip: bool = None,
    ignore_query_strings: bool = None,
    monthly_bandwidth_limit: int = None,
    access_control_origin_header_extensions: list = [],
    enable_access_control_origin_header: bool = None,
    disable_cookies: bool = None,
    budget_redirected_countries: list = [],
    blocked_countries: list = [],
    cache_control_max_age_override: int = None,
    cache_control_browser_max_age_override: int = None,
    add_host_header: bool = None,
    add_canonical_header: bool = None,
    enable_logging: bool = None,
    logging_ip_anonymization_enabled: bool = None,
    perma_cache_storage_zone_id: int = None,
    aws_signing_enabled: bool = None,
    aws_signing_key: str = None,
    aws_signing_secret: str = None,
    aws_signing_region_name: str = None,
    enable_origin_shield: bool = None,
    origin_shield_zone_code: str = None,
    enable_tls_1: bool = None,
    enable_tls_1_1: bool = None,
    cache_error_responses: bool = None,
    verify_origin_ssl: bool = None,
    log_forwarding_enabled: bool = None,
    log_forwarding_hostname: str = None,
    log_forwarding_port: int = None,
    log_forwarding_token: str = None,
    log_forwarding_protocol: int = None, # 0, 1, 2, 3
    logging_save_to_storage: bool = None,
    logging_storage_zone_id: int = None,
    follow_redirects: bool = None,
    connection_limit_per_ip_count: int = None,
    request_limit: int = None,
    limit_rate_after: float = None,
    limit_rate_per_second: int = None,
    burst_size: int = None,
    waf_enabled: bool = None,
    waf_disabled_rule_groups: list = [],
    waf_disabled_rules: list = [],
    waf_enable_request_header_logging: bool = None,
    waf_request_header_ignores: list = [],
    error_page_enable_custom_code: bool = None,
    error_page_custom_code: str = None,
    error_page_enable_status_page_widget: bool = None,
    error_page_status_page_code: str = None,
    error_page_whitelabel: bool = None,
    optimizer_enabled: bool = None,
    optimizer_desktop_max_width: int = None,
    optimizer_mobile_max_width: int = None,
    optimizer_image_quality: int = None,
    optimizer_mobile_image_quality: int = None,
    optimizer_enable_webp: bool = None,
    optimizer_enable_manipulation_engine: bool = None,
    optimizer_minify_css: bool = None,
    optimizer_minify_js: bool = None,
    optimizer_watermark_enabled: bool = None,
    optimizer_watermark_url: str = None,
    optimizer_watermark_position: int = None,
    optimizer_wartermark_offset: float = None,
    optimizer_watermark_min_image_size: int = None,
    optimizer_automatic_optimization_enabled: bool = None,
    optimizer_classes: list = [],
    optimizer_force_classes: bool = None,
    type: int = 1, # 0 or 1 (0 = premium, 1 = volume)
    origin_retries: int = None,
    origin_connect_timeout: int = None,
    origin_response_timeout: int = None,
    use_stale_while_updating: bool = None,
    use_stale_while_offline: bool = None,
    origin_retry_5xx_responses: bool = None,
    origin_retry_connection_timeout: bool = None,
    origin_retry_response_timeout: bool = None,
    origin_retry_delay: int = None,
    dns_origin_port: int = None,
    dns_origin_scheme: str = None,
    query_string_vary_parameters: list = [],
    origin_shield_enable_concurrency_limit: bool = None,
    origin_shield_max_concurrent_requests: int = None,
    enable_cookie_vary: bool = None,
    cookie_vary_parameters: list = [],
    enable_safe_hop: bool = None,
    origin_shield_queue_max_wait_time: int = None,
    origin_shield_max_queued_requests: int = None,
    use_background_update: bool = None,
    enable_auto_ssl: bool = None,
    log_anonymization_type: int = None,
    storage_zone_id: int = None,
    edge_script_id: int = None,
    origin_type: int = 0, # 0,1,2,3,4  (0 = standard (bunny.net origin), 1 = standard, )
    log_format: int = None,
    log_forwarding_format: int = None,
    shield_ddos_protection_type: int = None,
    shield_ddos_protection_enabled: bool = None,
    origin_host_header: str = None,
    enable_smart_cache: bool = None,
    enable_request_coalescing: bool = None,
    request_coalescing_timeout: int = None,
    ):
    """ Update pull zone """
    url = f"{BUNNY_API_ENDPOINT}/pullzone/{pull_zone_id}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'AccessKey': get_access_key(),
    }

    payload = {"Type": type}

    # TODO: add better validation to this

    if origin_url is None and storage_zone_id is None:
        raise ValidationError("either origin_url or storage_zone_id is required")
    
    if origin_url is not None and storage_zone_id is not None:
        raise ValidationError("either origin_url or storage_zone_id is required")

    if origin_url is not None:
        payload["OriginUrl"] = origin_url

    if len(allowed_referers) > 0:
        payload["AllowedReferers"] = allowed_referers
    
    if len(blocked_referers) > 0:
        payload["BlockedReferers"] = blocked_referers
    
    if len(blocked_ips) > 0:
        payload["BlockedIps"] = blocked_ips
    
    if enable_geo_zone_us is not None:
        payload["EnableGeoZoneUS"] = enable_geo_zone_us
    
    if enable_geo_zone_eu is not None:
        payload["EnableGeoZoneEU"] = enable_geo_zone_eu
    
    if enable_geo_zone_asia is not None:
        payload["EnableGeoZoneASIA"] = enable_geo_zone_asia
    
    if enable_geo_zone_sa is not None:
        payload["EnableGeoZoneSA"] = enable_geo_zone_sa
    
    if enable_geo_zone_af is not None:
        payload["EnableGeoZoneAF"] = enable_geo_zone_af
    
    if block_root_path_access is not None:
        payload["BlockRootPathAccess"] = block_root_path_access
    
    if block_post_requests is not None:
        payload["BlockPostRequests"] = block_post_requests
    
    if enable_query_string_ordering is not None:
        payload["EnableQueryStringOrdering"] = enable_query_string_ordering
    
    if enable_webp_vary is not None:
        payload["EnableWebpVary"] = enable_webp_vary
    
    if enable_avif_vary is not None:
        payload["EnableAvifVary"] = enable_avif_vary
    
    if enable_mobile_vary is not None:
        payload["EnableMobileVary"] = enable_mobile_vary
    
    if enable_country_code_vary is not None:
        payload["EnableCountryCodeVary"] = enable_country_code_vary
    
    if enable_hostname_vary is not None:
        payload["EnableHostnameVary"] = enable_hostname_vary
    
    if enable_cache_slice is not None:
        payload["EnableCacheSlice"] = enable_cache_slice
    
    if zone_security_enabled is not None:
        payload["ZoneSecurityEnabled"] = zone_security_enabled
    
    if zone_security_include_hash_remote_ip is not None:
        payload["ZoneSecurityIncludeHashRemoteIP"] = zone_security_include_hash_remote_ip
    
    if ignore_query_strings is not None:
        payload["IgnoreQueryStrings"] = ignore_query_strings
    
    if monthly_bandwidth_limit is not None:
        payload["MonthlyBandwidthLimit"] = monthly_bandwidth_limit
    
    if len(access_control_origin_header_extensions) > 0:
        payload["AccessControlOriginHeaderExtensions"] = access_control_origin_header_extensions
    
    if enable_access_control_origin_header is not None:
        payload["EnableAccessControlOriginHeader"] = enable_access_control_origin_header
    
    if disable_cookies is not None:
        payload["DisableCookies"] = disable_cookies
    
    if len(budget_redirected_countries) > 0:
        payload["BudgetRedirectedCountries"] = budget_redirected_countries
    
    if len(blocked_countries) > 0:
        payload["BlockedCountries"] = blocked_countries
    
    if cache_control_max_age_override is not None:
        payload["CacheControlMaxAgeOverride"] = cache_control_max_age_override
    
    if cache_control_browser_max_age_override is not None:
        payload["CacheControlBrowserMaxAgeOverride"] = cache_control_browser_max_age_override
    
    if add_host_header is not None:
        payload["AddHostHeader"] = add_host_header
    
    if add_canonical_header is not None:
        payload["AddCanonicalHeader"] = add_canonical_header
    
    if enable_logging is not None:
        payload["EnableLogging"] = enable_logging
    
    if logging_ip_anonymization_enabled is not None:
        payload["LoggingIPAnonymizationEnabled"] = logging_ip_anonymization_enabled
    
    if perma_cache_storage_zone_id is not None:
        payload["PermaCacheStorageZoneId"] = perma_cache_storage_zone_id
    
    if aws_signing_enabled is not None:
        payload["AWSSigningEnabled"] = aws_signing_enabled
    
    if aws_signing_key is not None:
        payload["AWSSigningKey"] = aws_signing_key
    
    if aws_signing_region_name is not None:
        payload["AWSSigningRegionName"] = aws_signing_region_name

    if aws_signing_secret is not None:
        payload["AWSSigningSecret"] = aws_signing_secret
    
    if enable_origin_shield is not None:
        payload["EnableOriginShield"] = enable_origin_shield
    
    if origin_shield_zone_code is not None:
        payload["OriginShieldZoneCode"] = origin_shield_zone_code
    
    if enable_tls_1 is not None:
        payload["EnableTLS1"] = enable_tls_1
    
    if enable_tls_1_1 is not None:
        payload["EnableTLS1_1"] = enable_tls_1_1
    
    if cache_error_responses is not None:
        payload["CacheErrorResponses"] = cache_error_responses
    
    if verify_origin_ssl is not None:
        payload["VerifyOriginSSL"] = verify_origin_ssl
    
    if log_forwarding_enabled is not None:
        payload["LogForwardingEnabled"] = log_forwarding_enabled
    
    if log_forwarding_hostname is not None:
        payload["LogForwardingHostname"] = log_forwarding_hostname
    
    if log_forwarding_port is not None:
        payload["LogForwardingPort"] = log_forwarding_port
    
    if log_forwarding_token is not None:
        payload["LogForwardingToken"] = log_forwarding_token
    
    if log_forwarding_protocol is not None:
        payload["LogForwardingProtocol"] = log_forwarding_protocol
    
    if logging_save_to_storage is not None:
        payload["LoggingSaveToStorage"] = logging_save_to_storage
    
    if logging_storage_zone_id is not None:
        payload["LoggingStorageZoneId"] = logging_storage_zone_id
    
    if follow_redirects is not None:
        payload["FollowRedirects"] = follow_redirects
    
    if connection_limit_per_ip_count is not None:
        payload["ConnectionLimitPerIPCount"] = connection_limit_per_ip_count
    
    if request_limit is not None:
        payload["RequestLimit"] = request_limit
    
    if limit_rate_after is not None:
        payload["LimitRateAfter"] = limit_rate_after
    
    if limit_rate_per_second is not None:
        payload["LimitRatePerSecond"] = limit_rate_per_second
    
    if burst_size is not None:
        payload["BurstSize"] = burst_size
    
    if waf_enabled is not None:
        payload["WAFEnabled"] = waf_enabled
    
    if len(waf_disabled_rule_groups) > 0:
        payload["WAFDisabledRuleGroups"] = waf_disabled_rule_groups
    
    if len(waf_disabled_rules) > 0:
        payload["WAFDisabledRules"] = waf_disabled_rules
    
    if waf_enable_request_header_logging is not None:
        payload["WAFEnableRequestHeaderLogging"] = waf_enable_request_header_logging
    
    if len(waf_request_header_ignores) > 0:
        payload["WAFRequestHeaderIgnores"] = waf_request_header_ignores
    
    if error_page_enable_custom_code is not None:
        payload["ErrorPageEnableCustomCode"] = error_page_enable_custom_code

    if error_page_custom_code is not None:
        payload["ErrorPageCustomCode"] = error_page_custom_code
    
    if error_page_enable_status_page_widget is not None:
        payload["ErrorPageEnableStatusPageWidget"] = error_page_enable_status_page_widget
    
    if error_page_status_page_code is not None:
        payload["ErrorPageStatuspageCode"] = error_page_status_page_code
    
    if error_page_whitelabel is not None:
        payload["ErrorPageWhitelabel"] = error_page_whitelabel
    
    if optimizer_enabled is not None:
        payload["OptimizerEnabled"] = optimizer_enabled
    
    if optimizer_desktop_max_width is not None:
        payload["OptimizerDesktopMaxWidth"] = optimizer_desktop_max_width
    
    if optimizer_mobile_max_width is not None:
        payload["OptimizerMobileMaxWidth"] = optimizer_mobile_max_width
    
    if optimizer_image_quality is not None:
        payload["OptimizerImageQuality"] = optimizer_image_quality
    
    if optimizer_mobile_image_quality is not None:
        payload["OptimizerMobileImageQuality"] = optimizer_mobile_image_quality
    
    if optimizer_enable_webp is not None:
        payload["OptimizerEnableWebp"] = optimizer_enable_webp
    
    if optimizer_enable_manipulation_engine is not None:
        payload["OptimizerEnableManipulationEngine"] = optimizer_enable_manipulation_engine
    
    if optimizer_minify_css is not None:
        payload["OptimizerMinifyCSS"] = optimizer_minify_css
    
    if optimizer_minify_js is not None:
        payload["OptimizerMinifyJavaScript"] = optimizer_minify_js
    
    if optimizer_watermark_enabled is not None:
        payload["OptimizerWatermarkEnabled"] = optimizer_watermark_enabled
    
    if optimizer_watermark_url is not None:
        payload["OptimizerWatermarkURL"] = optimizer_watermark_url
    
    if optimizer_watermark_position is not None:
        payload["OptimizerWatermarkPosition"] = optimizer_watermark_position
    
    if optimizer_wartermark_offset is not None:
        payload["OptimizerWatermarkOffset"] = optimizer_wartermark_offset
    
    if optimizer_watermark_min_image_size is not None:
        payload["OptimizerWatermarkMinImageSize"] = optimizer_watermark_min_image_size
    
    if optimizer_automatic_optimization_enabled is not None:
        payload["OptimizerAutomaticOptimizationEnabled"] = optimizer_automatic_optimization_enabled
    
    if optimizer_classes is not None:
        payload["OptimizerClasses"] = optimizer_classes
    
    if optimizer_force_classes is not None:
        payload["OptimizerForceClasses"] = optimizer_force_classes
    
    if origin_retries is not None:
        payload["OriginRetries"] = origin_retries
    
    if origin_connect_timeout is not None:
        payload["OriginConnectTimeout"] = origin_connect_timeout
    
    if origin_response_timeout is not None:
        payload["OriginResponseTimeout"] = origin_response_timeout
    
    if use_stale_while_updating is not None:
        payload["UseStaleWhileUpdating"] = use_stale_while_updating
    
    if use_stale_while_offline is not None:
        payload["UseStaleWhileOffline"] = use_stale_while_offline
    
    if origin_retry_5xx_responses is not None:
        payload["OriginRetry5xxResponses"] = origin_retry_5xx_responses
    
    if origin_retry_connection_timeout is not None:
        payload["OriginRetryConnectionTimeout"] = origin_retry_connection_timeout
    
    if origin_retry_response_timeout is not None:
        payload["OriginRetryResponseTimeout"] = origin_retry_response_timeout
    
    if origin_retry_delay is not None:
        payload["OriginRetryDelay"] = origin_retry_delay
    
    if dns_origin_port is not None:
        payload["DNSOriginPort"] = dns_origin_port
    
    if dns_origin_scheme is not None:
        payload["DNSOriginScheme"] = dns_origin_scheme
    
    if len(query_string_vary_parameters) > 0:
        payload["QueryStringVaryParameters"] = query_string_vary_parameters
    
    if origin_shield_enable_concurrency_limit is not None:
        payload["OriginShieldEnableConcurrencyLimit"] = origin_shield_enable_concurrency_limit
    
    if origin_shield_max_concurrent_requests is not None:
        payload["OriginShieldMaxConcurrentRequests"] = origin_shield_max_concurrent_requests
    
    if enable_cookie_vary is not None:
        payload["EnableCookieVary"] = enable_cookie_vary
    
    if len(cookie_vary_parameters) > 0:
        payload["CookieVaryParameters"] = cookie_vary_parameters
    
    if enable_safe_hop is not None:
        payload["EnableSafeHops"] = enable_safe_hop
    
    if origin_shield_queue_max_wait_time is not None:
        payload["OriginShieldQueueMaxWaitTime"] = origin_shield_queue_max_wait_time
    
    if origin_shield_max_queued_requests is not None:
        payload["OriginShieldMaxQueuedRequests"] = origin_shield_max_queued_requests
    
    if use_background_update is not None:
        payload["UseBackgroundUpdate"] = use_background_update
    
    if enable_auto_ssl is not None:
        payload["EnableAutoSSL"] = enable_auto_ssl
    
    if log_anonymization_type is not None:
        payload["LogAnonymizationType"] = log_anonymization_type
    
    if storage_zone_id is not None:
        payload["StorageZoneID"] = storage_zone_id
    
    if edge_script_id is not None:
        payload["EdgeScriptID"] = edge_script_id
    
    if origin_type is not None:
        payload["OriginType"] = origin_type
    
    if log_format is not None:
        payload["LogFormat"] = log_format
    
    if log_forwarding_format is not None:
        payload["LogForwardingFormat"] = log_forwarding_format
    
    if shield_ddos_protection_type is not None:
        payload["ShieldDDOSProtectionType"] = shield_ddos_protection_type

    if shield_ddos_protection_enabled is not None:
        payload["ShieldDDOSProtectionEnabled"] = shield_ddos_protection_enabled

    if origin_host_header is not None:
        payload["OriginHostHeader"] = origin_host_header

    if enable_smart_cache is not None:
        payload["EnableSmartCache"] = enable_smart_cache

    if enable_request_coalescing is not None:
        payload["EnableRequestCoalescing"] = enable_request_coalescing

    if request_coalescing_timeout is not None:
        payload["RequestCoalescingTimeout"] = request_coalescing_timeout    

    res = requests.post(url, headers=headers, json=payload)

    return handle_response(res)

def delete_pull_zone(pull_zone_id: int):
    """ Delete pull zone """
    url = f"{BUNNY_API_ENDPOINT}/pullzone/{pull_zone_id}"
    headers = {
        "Accept": "application/json",
        "AccessKey": get_access_key(),
    }
    res = requests.delete(url, headers=headers)
    return handle_response(res)

def delete_edge_rule():
    raise NotImplementedError

def add_update_edge_rule():
    raise NotImplementedError

def enable_edge_rule():
    raise NotImplementedError

def get_origin_shield_queue_statistics():
    raise NotImplementedError

def get_safe_hop_statistics():
    raise NotImplementedError

def get_optimizer_statistics():
    raise NotImplementedError

def load_free_certificate(hostname: str):
    url = f"{BUNNY_API_ENDPOINT}/pullzone/loadFreeCertificate?hostname={hostname}"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'AccessKey': get_access_key(),
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return {"Message": "certificate loaded"}
    return handle_response(res)

def purge_cache():
    raise NotImplementedError

def add_custom_certificate():
    raise NotImplementedError

def remove_certificate():
    raise NotImplementedError

def add_custom_hostname(
    pull_zone_id: int, 
    hostname: str
    ):
    url = f"{BUNNY_API_ENDPOINT}/pullzone/{pull_zone_id}/addHostname"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'AccessKey': get_access_key(),
    }

    payload = {"Hostname": hostname}

    res = requests.post(url, headers=headers, json=payload)
    return handle_response(res)

def remove_custom_hostname(
    pull_zone_id: int, 
    hostname: str,
    ):
    url = f"{BUNNY_API_ENDPOINT}/pullzone/{pull_zone_id}/removeHostname"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'AccessKey': get_access_key(),
    }

    payload = {"Hostname": hostname}

    res = requests.delete(url, headers=headers, json=payload)
    return handle_response(res)

def set_force_ssl(
    pull_zone_id: int, 
    hostname: str,
    force_ssl: bool = True
    ):
    url = f"{BUNNY_API_ENDPOINT}/pullzone/{pull_zone_id}/setForceSSL"
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'AccessKey': get_access_key(),
    }

    payload = {
        "Hostname": hostname,
        "ForceSSL": force_ssl
    }

    res = requests.post(url, headers=headers, json=payload)
    return handle_response(res)

def reset_token_key():
    raise NotImplementedError

def add_allowed_referer():
    raise NotImplementedError

def remove_allowed_referer():
    raise NotImplementedError

def add_blocked_referer():
    raise NotImplementedError

def remove_blocked_referer():
    raise NotImplementedError

def add_blocked_ip():
    raise NotImplementedError

def remove_blocked_ip():
    raise NotImplementedError
