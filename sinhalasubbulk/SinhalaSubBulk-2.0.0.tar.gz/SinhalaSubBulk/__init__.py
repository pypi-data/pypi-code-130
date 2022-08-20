from bs4 import BeautifulSoup as bs
import requests
from io import BytesIO
import os
from zipfile import ZipFile

HELP = """
READ ME
- First , visit to https://www.baiscopelk.com/tv-series or https://cineru.lk/tv_series/
- Now Click The TV Series Which You Want Sinhala Subtitles.
- Copy the url and Paste it as bulk url
- Run the program and download All subtitles for your selected tv series

OPTIONAL
- If you want to change download path, Add it as download_path


"""

ABOUTME = """
ABOUT-ME
- Name : SinhalaSubBulk
- Version : 2.0.0
- Author : Gavindu Tharaka
- Email : gavi.tharaka@gmail.com
- Description : A Simple Python library for Download Bulk of Sinhala Subtitles

If you have any problem of this program try here
https://colab.research.google.com/drive/1Xk4VmrHgNdA3od5OSxWGv_pGQYTBhdm5?usp=sharing

Visit for More projects
https://pypi.org/user/GavinduTharaka/

Thanx for using SinhalaSubBulk
"""


def download(bulk_url, download_path=None):
        if download_path is None:
        download_path = ""
    else:
        
        try:
            os.makedirs(download_path)
        except:
            pass

    r = requests.get(bulk_url).text
    soup = bs(r, "html.parser")
    if "baiscopelk.com" in bulk_url:
        for f in soup.find_all('td'):
            if f.a:
                link2 = f.a['href']
                r = requests.get(link2).text
                soup2 = bs(r, "html.parser")
                title = soup2.title.text
                file_name = title[:title.index("|")]
                find_download = soup2.find('p', {'style': 'padding: 0px; text-align: center;'}).a['href']
                print(file_name)
                content = requests.get(find_download).content
                try:
                    ZipFile(BytesIO(content))
                    file = open(download_path + "/" + file_name + '.zip', 'wb')
                except:
                    file = open(download_path + "/" + file_name + '.rar', 'wb')
                file.write(content)
                file.close()
                print("Downloaded")
                print("-----------------------------------------------------------")
                print("  ")

    elif "cineru.lk" in bulk_url:
        for f in soup.find_all('a', {'class': "epi_item"}):
            r = requests.get(f['href']).text
            soup2 = bs(r, "html.parser")
            title = soup2.title.text
            print(title)
            find_download = soup2.find('a', {"id": "btn-download"})['data-link']
            if find_download[-1] == "/":
                find_download = find_download[:-1]
            file_name = find_download[find_download.rindex("/") + 1:].replace(".zip", "").replace(".rar", "")
            content = requests.get(find_download).content
            try:
                ZipFile(BytesIO(content))
                file = open(download_path + "/" + file_name + '.zip', 'wb')
            except:
                file = open(download_path + "/" + file_name + '.rar', 'wb')
            file.write(content)
            file.close()
            print("Downloaded")
            print("-----------------------------------------------------------")
            print("  ")
    read_me = open(download_path + "/" + 'ReadMe' + '.txt', 'w')
    read_me.write(HELP+ABOUTME)
    read_me.close()