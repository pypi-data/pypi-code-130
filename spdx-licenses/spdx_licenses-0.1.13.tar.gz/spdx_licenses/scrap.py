from typing import List
import requests
import asyncio
import os

import aiohttp
from bs4 import BeautifulSoup

from .type import License, Licenses

if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

spdx_url_direct = "https://spdx.org/licenses/"
spdx_url_xmls = ""  # not determined yet

# Lines with "#danger" at the end are dangerous and in case the website template
# update, they may break the code, check them in case of malfunction first.


def spdx_scrapper_direct(
    log: bool = False,
) -> Licenses:  # make it with async requests
    response = requests.get(spdx_url_direct)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find(
        "table", {"class": "sortable"}
    )  # also unsotable one append to this table
    session = aiohttp.ClientSession()
    licenses = []
    for i, row in enumerate(table.find_all("tr")):
        if row.find("th"):
            continue
        licenses.append(__get_license_header_and_text(session, row, i, log))
    licenses = asyncio.gather(*licenses)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(licenses)
    licenses = licenses.result()
    loop.run_until_complete(session.close())
    loop.close()
    return Licenses(licenses)
    # return asyncio.gather(
    #     # iterate over table rows in order to move those with either OSI or FSF approve to a sep dictinary
    #     *[
    #         __get_license_header_and_text(session, row)
    #         for row in table.find_all("tr")
    #         if not row.find("th")
    #     ]#, return_exceptions = True # wtf is this?
    # )


async def __get_license_header_and_text(session, row, i, log):
    full_name, spdx_id, approved_osi, approved_fsf = row.find_all("td")
    url = (
        spdx_url_direct + full_name.find("a").get("href")[2:]
    )  # danger (also because of find_all order is not promised)
    full_name = full_name.find("a").text.strip()
    spdx_id = spdx_id.find("code").text.strip()
    approved_osi = approved_osi.text.strip() == "Y"  # danger
    approved_fsf = approved_fsf.text.strip() == "Y"  # danger
    async with session.get(url) as response:
        soup = BeautifulSoup(await response.text(), "html.parser")
        license_header_text = "".join(
            soup.find("div", {"property": "spdx:standardLicenseHeader"}).findAll(
                text=True
            )
        ).strip()
        if license_header_text == "There is no standard license header for the license":
            license_header_text = None
        license_text = "".join(
            soup.find("div", {"property": "spdx:licenseText"}).findAll(text=True)
        ).strip()
        if log:
            print(f"{i} done: {spdx_id}")
        return License(
            direct_url=url,
            full_name=full_name,
            spdx_id=spdx_id,
            approved_osi=approved_osi,
            approved_fsf=approved_fsf,
            license_header_text=license_header_text,
            license_text=license_text,
            obsolete=False,
        )


# def spdx_scrapper_xmls(log:bool=False) -> List[License]:
#     pass
