#!/usr/bin/python3
from shutil import which
from sys import exit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
from rich.console import Console
from json import dumps
from json import loads as ld
from random import choice


__all__ = ["fetch_proxies", "proxies_json"]


# Rich Lib Object Intialization--->
console = Console()


# Variables
ua_list = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/37.0.2062.94 Chrome/37.0.2062.94 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; Touch; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (X11; CrOS x86_64 6946.70.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.132 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.116 Safari/537.36"
]
proxies = []
proxy_type = ""
output_filename = ""
output_format = ""
_driver = which("chromedriver")


# Saving Proxies
def iO_func(json_prox, proxy_type, output_filename, output_format):
    txt_prox = []
    try:
        _filename = f"{output_filename}_{proxy_type}.{output_format}"
        if output_format == "json":
            with open(_filename, "w+") as handle:
                handle.write(json_prox)
        else:
            json_data = ld(json_prox)
            for _ in json_data:
                proxy = f"{_['IP Address']}:{_['Port']}"
                if proxy not in txt_prox:
                    txt_prox.append(proxy)
            with open(_filename, "w+") as handle:
                for _ in txt_prox:
                    handle.write(str(_) + "\n")
    except Exception as err:
        console.print("[" + "[red bold]Error[/red bold]" + "]" + f"[bold blink] {err}...![/bold blink]")
        exit(1)


# Get Proxies by Scraping the site
def get_proxies(driver, proxy_type, output_filename, output_format):
    global proxy_list_json
    proxy_list_json = []
    try:
        if proxy_type == "https":
            url = "https://sslproxies.org"
        elif proxy_type == "socks":
            url = "https://www.socks-proxy.net"
        else:
            exit("""Please Select a Valid Proxy Type.
                    => https
                    => socks""")
        driver.get(url)
        table = driver.find_element(By.TAG_NAME, 'table')
        thead = table.find_element(By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')
        tbody = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')

        headers = []
        for th in thead:
            headers.append(th.text.strip())
        for tr in tbody:
            proxy_data = {}
            tds = tr.find_elements(By.TAG_NAME, 'td')
            for i in range(len(headers)):
                proxy_data[headers[i]] = tds[i].text.strip()
            proxies.append(proxy_data)
        if output_filename != "None":
            json_prox = dumps(proxies)
            iO_func(json_prox, proxy_type, output_filename, output_format)
        else:
            proxy_list_json = proxies
            return proxy_list_json
    except Exception as err:
        console.print("[" + "[red bold]Error[/red bold]" + "]" + f"[bold blink] {err}...![/bold blink]")
        exit(1)


# Start the Chrome Driver.
def chrome_driver(proxy_type, output_filename, output_format):
    try:
        # Random User Agent
        agent = choice(ua_list)

        # Chrome Driver Options
        chrome_options = Options()
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1280x1696')
        chrome_options.add_argument('--user-data-dir=/tmp/user-data')
        chrome_options.add_argument('--hide-scrollbars')
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        chrome_options.add_argument('--v=99')
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--data-path=/tmp/data-path')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--homedir=/tmp')
        chrome_options.add_argument('--disk-cache-dir=/tmp/cache-dir')
        chrome_options.add_argument(f"user-agent={agent}")

        # Initializing Chromium Driver
        driver = webdriver.Chrome(options=chrome_options)

        # Stealth Selenium Options
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )

        try:
            get_proxies(driver, proxy_type, output_filename, output_format)
            driver.quit()
        except Exception as err:
            driver.quit()
            console.print("[" + "[red bold]Error[/red bold]" + "]" + f"[bold blink] {err}...![/bold blink]")
            exit(1)
    except Exception as err:
        console.print("[" + "[red bold]Error[/red bold]" + "]" + f"[bold blink] {err}...![/bold blink]")
        exit(1)


def fetch_proxies(proxy_type, output_filename, output_format):
    if _driver is not None:
        _type = str(proxy_type)
        _filename = str(output_filename)
        _format = str(output_format)
        chrome_driver(_type, _filename, _format)
    else:
        exit("""
        ChromeDriver is not installed. Please install it.
            => sudo apt-get install chromium-driver""")


def proxies_json(proxy_type):
    global json_proxy_list
    json_proxy_list = []
    if _driver is not None:
        _type = str(proxy_type)
        _filename = "None"
        _format = "json"
        chrome_driver(_type, _filename, _format)
        json_proxy_list = proxy_list_json
        return json_proxy_list
    else:
        exit("""
        ChromeDriver is not installed. Please install it.
            => sudo apt-get install chromium-driver""")
