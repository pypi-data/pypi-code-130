import time
import requests
from bs4 import BeautifulSoup
import lib_dsa.byte_array as byte_array
import lib_compute.serialization as serialization
import lib_compute.deserialization as deserialization
import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
import pandas as pd
import random

def read_website(url):
    resp = requests.get(url)
    return resp.content


def scrape_L1(links):
    return [
            read_website(url)
            for url in links
        ]


def read_iter(file_names, mode='rb'):
    result = []
    for file_name in file_names:
        fp = open(file_name, mode)
        fsource = fp.read()
        fp.close()
        result.append(fsource)
    return result


def scrape_write(link, file_name):
    file_repr = read_website(link)
    fp = open(file_name, 'wb')
    fp.write(file_repr)
    fp.close()


def scrape_write_L1(links, out_files):
    for i in range(0, len(links)):
        print(i)
        scrape_write(links[i], out_files[i])


def fwrite_L1(file_name_L1, file_repr_L1, mode='wb'):
    i = 0
    for file_name, file_repr in zip(file_name_L1, file_repr_L1):
        print( i )
        i += 1
        fp = open(file_name, mode)
        fp.write(file_repr)
        fp.close()


def select_links(html_raw):
    soup = BeautifulSoup(html_raw, 'html.parser')
    L1 = soup.find_all('a')
    result = []
    for x in L1:
        if 'href' not in x.attrs:
            continue
        result.append( x.attrs['href'] )
    return result


def vba_write(base_path, str_L1, is_bytes=False):
    vba = byte_array.make_vba(base_path)
    if is_bytes:
        vba.batch_insert_bytes(str_L1)
        return
    target_bytes_L1 = []
    try:
        target_bytes_L1 = [ x.encode('latin-1') for x in str_L1 ]
    except:
        target_bytes_L1 = [ x.encode() for x in str_L1 ]
    vba.batch_insert_bytes(target_bytes_L1)


def eval_html_srcs(file_name_L1, out_file_L1, time_sleep=1, executable_path=''):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options, executable_path=executable_path)
    for fspath, out_file in zip(file_name_L1, out_file_L1):
        file_name = f'file://{fspath}'
        print(file_name)
        try:
            X = driver.get(file_name)
            time.sleep(time_sleep)
            Y = driver.page_source
        except:
            continue
        fp = open(out_file, 'w')
        fp.write(Y)
        fp.close()
    driver.quit()
