# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from redturtle.chefcookie import _
from redturtle.chefcookie.interfaces import IChefCookieSettings
from plone import api
from plone.memoize import view
from zope.i18n import translate

try:
    from collections import OrderedDict
except ImportError:
    pass

import logging
import json
import six

logger = logging.getLogger(__name__)

TEMPLATE = """

var iframeCookies = {iframe_cookies_ids_placeholder};
var anchorCookies = {anchor_cookies_ids_placeholder};
var profiling_cookies_config = {profiling_cookies_config_placeholder};

function accept_all_anchor_based_provider_when_tiles_loaded(cc){
    var placeholder_identifiers = ['twittertimeline-placeholder'];
    for (let i = 0; i < placeholder_identifiers.length; i++) {
        accept_anchor_based_provider(cc, placeholder_identifiers);
    }
}

function accept_anchor_based_provider(cc, placeholder_identifier){
    document.querySelectorAll("div." + placeholder_identifier).forEach(function(placeholder) {
        var anchor = placeholder.nextElementSibling;
        var twitter = anchor.nextElementSibling;
        var anchor_href = anchor.dataset.ccHref;
        var twitter_src = twitter.dataset.ccSrc;
        var name = anchor.dataset.ccName;
        if(cc.isAccepted(name)){
            anchor.setAttribute('href', anchor_href);
            anchor.removeAttribute('hidden');
            // re-add the script to force its execution
            twitter.parentNode.removeChild(twitter);
            var newScript = document.createElement('script');
            newScript.setAttribute('src', twitter_src);
            newScript.setAttribute('async', '');
            anchor.after(newScript);
            placeholder.setAttribute('hidden', true);
        }
    });
}

function decline_anchor_based_provider(cc, placeholder_identifier){
    debugger;
}

function accept_twitter_timeline(cc){
    var placeholder_identifier = 'twittertimeline-placeholder';
    accept_anchor_based_provider(cc, placeholder_identifier);
}

function decline_twitter_timeline(cc){
    var placeholder_identifier = 'twittertimeline-placeholder';
    decline_anchor_based_provider(cc, placeholder_identifier);

}

function accept_iframe(cc) {
    document.querySelectorAll('iframe').forEach(function(iframe) {
        var src = iframe.dataset.ccSrc;
        var name = iframe.dataset.ccName;
        var placeholder = iframe.previousElementSibling;
        console.log('placeholder: ', placeholder);
        console.log('name: ', name);
        if (placeholder && src) {
            if(cc.isAccepted(name)){
                iframe.setAttribute('src', src);
                iframe.removeAttribute('hidden');
                placeholder.setAttribute('hidden', true);
            } else {
                iframe.setAttribute('src', '');
                iframe.setAttribute('hidden', true);
                placeholder.removeAttribute('hidden');
            }
        }
    });
    // handle recaptcha
    if (cc.isAccepted("recaptcha")) {
        // re-enable scripts
        var scripts = document.querySelectorAll('script[data-cc-src*="https://www.google.com/recaptcha/api.js"]');
        if (scripts.length > 0) {
            scripts.forEach(function(script) {
                var scriptSrc = script.dataset.ccSrc;
                var sibling = script.nextElementSibling;
                script.parentNode.removeChild(script);
                var newScript = document.createElement('script');
                newScript.setAttribute('src', scriptSrc);
                newScript.setAttribute('async', '');
                newScript.setAttribute('defer', '');
                sibling.before(newScript);
            });
            document.querySelectorAll('div.iframe-placeholder.recaptcha').forEach(function(placeholder) {
                placeholder.setAttribute('hidden', true);
            });
        }
    }
}

if (Object.keys(profiling_cookies_config).length > 0) {
    iframeCookies.forEach(function(name) {
        if (profiling_cookies_config.scripts[name] !== undefined) {
            profiling_cookies_config.scripts[name].accept = (cc, resolve, isInit) => {
                accept_iframe(cc);
                if (name === 'facebook' && profiling_cookies_config.scripts[name].id) {
                    let script = document.createElement('script');
                    script.innerHTML =
                        "!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init', '" +
                        profiling_cookies_config.scripts[name].id +
                        "');fbq('track', 'PageView');fbq('track', 'ViewContent');";
                    document.head.appendChild(script);
                    window.chefcookie_loaded.push(name);
                }
            };
        }
    });

    anchorCookies.forEach(function(name) {
        if (profiling_cookies_config.scripts[name] !== undefined) {
            profiling_cookies_config.scripts[name].accept = (cc, resolve, isInit) => {
                if (name === 'twittertimeline'){
                    accept_twitter_timeline(cc);
                }
            };
            profiling_cookies_config.scripts[name].decline = (provider) =>{
                decline_twitter_timeline(cc);
            };
        }
    });

    if (profiling_cookies_config.scripts.hotjar !== undefined) {
        profiling_cookies_config.scripts.hotjar.accept = function(cc, resolve, isInit) {
                var id = cc.config.settings[1].scripts.hotjar.id;
                var script = document.createElement("script");
                script.innerHTML =
                    "(function(h,o,t,j,a,r){h.hj=h.hj||function(){(h.hj.q=h.hj.q||[]).push(arguments)};h._hjSettings={hjid:'" +
                    id +
                    "',hjsv:6};a=o.getElementsByTagName('head')[0];r=o.createElement('script');r.async=1;r.src=t+h._hjSettings.hjid+j+h._hjSettings.hjsv;a.appendChild(r);})(window,document,'https://static.hotjar.com/c/hotjar-','.js?sv=')";
                document.head.appendChild(script);
                cc.setLoaded("hotjar");
            };
    }
}

var cookies_settings = [];
var technical_cookies = {technical_cookies_placeholder};

if (Object.keys(technical_cookies).length > 0) {
    cookies_settings.push(technical_cookies);
}

if (Object.keys(profiling_cookies_config).length > 0) {
    cookies_settings.push(profiling_cookies_config);
}

var cc = new redturtlechefcookie({
  message: {message_labels_placeholder},
  accept_all_if_settings_closed: false,
  show_decline_button: true,
  scripts_selection: "true", // false|true|'collapse'
  debug_log: false,
  cookie_prefix: {cookie_prefix},
  consent_tracking: {consent_tracking_placeholder}, // '/wp-json/v1/track-consent.php'
  expiration: 180, // in days
  exclude_google_pagespeed: false,
  style: {
    layout: "bottombar", //"overlay", // overlay|bottombar|topbar
    size: 1, // 1|2|3|4|5
    color_text: "#4d4d4d",
    color_highlight: "",
    color_background: "#eeeeee",
    highlight_accept: true,
    show_disabled_checkbox: true,
    noscroll: false,
    fade: true,
    blur: true,
    css_add: "",
  },
  labels: {labels_placeholder},
  exclude: [
    // exclude privacy site if needed
    // exclude wordpress users
    () => {
      return (
        document.cookie !== undefined &&
        document.cookie.indexOf("wp-settings-time") > -1
      );
    }
  ],
  settings: cookies_settings,
});
document.addEventListener("DOMContentLoaded", () => {
  cc.init();
  accept_iframe(cc);
  accept_twitter_timeline(cc);
  document.querySelectorAll(".pat-tiles-management").forEach(el => {
    el.addEventListener("rtTilesLoaded", e => {
      accept_iframe(cc);
      accept_all_anchor_based_provider_when_tiles_loaded(cc);
    });
  });

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

  cc.registerEventListener(document, "click", e => {
    if (
      e.target.hasAttribute("data-cc-open-settings") ||
      (e.target.tagName !== "A" && e.target.closest("[data-cc-open-settings]"))
    ) {
      cc.open();
      cc.showSettings();
      cc.switchSettingsLabelsOpen();
      e.preventDefault();
    }
  });

  cc.registerEventListener(document, "click", e => {
    if (e.target.classList.contains("data-cc-open")) {
      cc.open();
      cc.showSettings();
      cc.switchSettingsLabelsOpen();
      e.preventDefault();
    }
    if (
      e.target.hasAttribute("data-cc-destroy") ||
      (e.target.tagName !== "A" && e.target.closest("[data-cc-destroy]"))
    ) {
      cc.setCookieToHideOverlay();
      cc.close();
      cc.logTracking('close_by_x', getCookie(cc.getCookieName('accepted_providers')));
      e.preventDefault();
    }
    if (e.target.hasAttribute("data-cc-accept-all")) {
      cc.acceptAllScripts();
      cc.setCookieToHideOverlay();
      cc.close();
      cc.logTracking('accept_all', getCookie(cc.getCookieName('accepted_providers')));
      e.preventDefault();
    }
  });
  {settings_icon_placeholder}
});
"""

SETTINGS_ICON_PLACEHOLDER = """
document.body.insertAdjacentHTML("beforeend", '<a title="{open_settings_placeholder}" id="cookie-settings-open" {data_cc_open_placeholder}="" href="/"><svg aria-hidden="true" focusable="false" data-prefix="fas" data-icon="user-lock" class="svg-inline--fa fa-user-lock fa-w-20" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512"><path fill="currentColor" d="M224 256A128 128 0 1 0 96 128a128 128 0 0 0 128 128zm96 64a63.08 63.08 0 0 1 8.1-30.5c-4.8-.5-9.5-1.5-14.5-1.5h-16.7a174.08 174.08 0 0 1-145.8 0h-16.7A134.43 134.43 0 0 0 0 422.4V464a48 48 0 0 0 48 48h280.9a63.54 63.54 0 0 1-8.9-32zm288-32h-32v-80a80 80 0 0 0-160 0v80h-32a32 32 0 0 0-32 32v160a32 32 0 0 0 32 32h224a32 32 0 0 0 32-32V320a32 32 0 0 0-32-32zM496 432a32 32 0 1 1 32-32 32 32 0 0 1-32 32zm32-144h-64v-80a32 32 0 0 1 64 0z"></path></svg></a>');
"""


class View(BrowserView):
    @property
    @view.memoize
    def youtube_enabled(self):
        return self.get_registry_settings(name="youtube")

    def __call__(self):
        self.request.response.setHeader(
            "Content-type", " application/javascript; charset=utf-8"
        )
        # i can't use format method because there are a lot of brackets

        endpoint = self.get_registry_settings("registry_endpoint")
        consent_traccking_url = endpoint and '"{}"'.format(endpoint) or "null"

        cookie_prefix = '"{}"'.format(self.get_registry_settings("cookie_name"))

        return (
            TEMPLATE.replace(
                "{iframe_cookies_ids_placeholder}",
                json.dumps(self.get_iframe_cookies_ids()),
            )
            .replace(
                "{anchor_cookies_ids_placeholder}",
                json.dumps(self.get_anchor_cookies_ids()),
            )
            .replace(
                "{profiling_cookies_config_placeholder}",
                self.get_profiling_cookies_config(),
            )
            .replace("{message_labels_placeholder}", self.get_message_labels())
            .replace("{labels_placeholder}", self.get_labels())
            .replace(
                "{technical_cookies_placeholder}",
                self.get_tech_cookies_config(),
            )
            .replace("{settings_placeholder}", self.get_settings())
            .replace("{consent_tracking_placeholder}", consent_traccking_url)
            .replace("{cookie_prefix}", cookie_prefix)
            .replace("{settings_icon_placeholder}", self.show_settings_icon())
        )

    @view.memoize
    def get_registry_settings(self, name, load_json=False):
        try:
            value = api.portal.get_registry_record(name, interface=IChefCookieSettings)
            if load_json:
                if six.PY2:
                    value = json.JSONDecoder(object_pairs_hook=OrderedDict).decode(
                        value
                    )
                else:
                    value = json.loads(value)
            elif isinstance(value, six.string_types) and six.PY2:
                value = value.encode("utf-8")
            return value
        except Exception as e:
            logger.exception(e)
            return ""

    def get_message_labels(self):
        labels = self.get_registry_settings("header_labels") or "{}"
        policy_url = self.get_registry_settings(name="policy_url", load_json=True)
        language = api.portal.get_current_language()
        if policy_url and language in policy_url:
            url = policy_url[language]
            if six.PY2:
                url = url.encode("utf-8")
            labels = labels.replace("{policy_url}", url)
        return labels

    def get_labels(self):
        labels = self.get_registry_settings(name="general_labels") or "{}"
        return labels

    def get_settings(self):
        tech_cookies = self.get_tech_cookies_config()
        profiling_cookies = self.get_profiling_cookies_config()

        res = []
        if tech_cookies:
            res.append(tech_cookies)
        if profiling_cookies:
            res.append(profiling_cookies)
        return json.dumps(res)

    def get_only_technical_cookies_values(self):
        value = self.get_registry_settings(name="only_technical_cookies")
        if not value:
            return False
        return True

    def get_tech_cookies_config(self):

        res = {
            "checked_by_default": True,
            "cannot_be_modified": True,
            "initial_tracking": True,
        }

        labels = self.get_registry_settings(name="technical_cookies_labels")
        specific_labels = self.get_registry_settings(
            name="technical_cookies_specific_labels", load_json=True
        )

        analytics_id = self.get_registry_settings(name="analytics_id")
        matomo_id = self.get_registry_settings(name="matomo_id")

        if labels:
            res.update(json.loads(labels))

        scripts = {}
        if six.PY2:
            scripts = OrderedDict()

        for name, value in specific_labels.items():
            scripts[name] = value
            if name == "analytics" and analytics_id:
                scripts[name]["id"] = analytics_id
            if name == "matomo" and matomo_id:
                scripts[name]["id"] = matomo_id

        if scripts:
            res.update({"scripts": scripts})
        return json.dumps(res)

    def get_profiling_cookies_config(self):

        facebook_id = self.get_registry_settings(name="facebook_id")
        iframe_cookies_ids = self.get_iframe_cookies_ids()
        anchor_cookies_ids = self.get_anchor_cookies_ids()
        hotjar_id = self.get_registry_settings(name="hotjar_id")
        linkedin_id = self.get_registry_settings(name="linkedin_id")
        profiling_cookies_labels = self.get_registry_settings(
            name="profiling_cookies_labels", load_json=True
        )
        profiling_cookies_specific_labels = self.get_registry_settings(
            name="profiling_cookies_specific_labels", load_json=True
        )
        if (
            not hotjar_id  # noqa
            and not linkedin_id  # noqa
            and not iframe_cookies_ids  # noqa
            and not anchor_cookies_ids  # noqa
        ):
            return "{}"

        scripts = {}
        if six.PY2:
            scripts = OrderedDict()

        for id, labels in profiling_cookies_specific_labels.items():
            if id in iframe_cookies_ids or id in anchor_cookies_ids:
                scripts[id] = labels

            if facebook_id and id == "facebook":
                if id not in scripts:
                    scripts[id] = labels
                scripts[id]["id"] = facebook_id

            if linkedin_id and id == "linkedin":
                if id not in scripts:
                    scripts[id] = labels
                scripts[id]["id"] = linkedin_id

            if hotjar_id and id == "hotjar":
                if id not in scripts:
                    scripts[id] = labels
                scripts[id]["id"] = hotjar_id

        res = {
            "checked_by_default": False,
            "cannot_be_modified": False,
            "initial_tracking": False,
        }
        res.update(profiling_cookies_labels)
        res["scripts"] = scripts

        return json.dumps(res)

    def get_profiling_labels_by_name(self, name):
        labels = self.get_registry_settings(
            name="profiling_cookies_specific_labels", load_json=True
        )
        if not labels:
            return {}

        return labels.get(name, {})

    def get_iframe_cookies_ids(self):
        data = self.get_registry_settings(name="iframes_mapping")

        res = []
        for mapping in filter(bool, data):
            id, domains = mapping.split("|")
            res.append(id)
        return res

    def get_anchor_cookies_ids(self):
        data = self.get_registry_settings(name="links_mapping")

        res = []
        for mapping in filter(bool, data):
            id, domains = mapping.split("|")
            res.append(id)
        return res

    def show_settings_icon(self):
        if self.get_registry_settings(name="show_settings_icon") is False:
            return ""
        manage_cc_open = "data-cc-open-settings"
        manage_cookie_label = translate(
            _(
                "manage_cookie_settings_label",
                default="Manage cookie settings",
            ),
            context=self.request,
        )
        if six.PY2:
            manage_cookie_label = manage_cookie_label.encode("utf-8")
        if self.get_only_technical_cookies_values():
            manage_cc_open = "data-cc-open"
        return SETTINGS_ICON_PLACEHOLDER.format(
            open_settings_placeholder=manage_cookie_label,
            data_cc_open_placeholder=manage_cc_open,
        )
