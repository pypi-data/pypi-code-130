url = "https://archive.apache.org/dist/spark/"

import urllib.request
from bs4 import BeautifulSoup


def getSparkVersion():
    # Set request
    request = urllib.request.urlopen(url)

    # Use BeautifulSoup to extract all link starting with spark- and remove slash at the end of the link and save
    # in list
    soup = BeautifulSoup(request, 'html.parser')
    links = soup.find_all('a', href=True)
    spark_links = [link['href'] for link in links if
                   link['href'].startswith('spark-') and link['href'].endswith('/')]
    # Remove slash at the end of the link and save in list
    spark_links = [link.replace('/', '') for link in spark_links]
    print(spark_links)
    return spark_links


def getHadoopVersion(self, sparkVersion):
    # Use BeautifulSoup to extract all link contains tar.gz and save in list
    request = urllib.request.urlopen(url + sparkVersion)
    soup = BeautifulSoup(request, 'html.parser')
    links = soup.find_all('a', href=True)
    tar_links = [link['href'] for link in links if link['href'].endswith('tgz')]

    # filter links contains bin-hadoop and save in list
    tar_links = [link for link in tar_links if 'bin-hadoop' in link]
    # Get complete version of hadoop from link and save in list
    tar_links = [link.split('-')[3] for link in tar_links]

    # Remove duplicate version and save in list
    tar_links = list(set(tar_links))

    # Remove hadoop from list and save in list and file extension
    tar_links = [link.replace('hadoop', '') for link in tar_links]
    tar_links = list(set([link.replace('.tgz', '') for link in tar_links]))

    # Print list of tar.gz in url
    print(tar_links)
    return tar_links
