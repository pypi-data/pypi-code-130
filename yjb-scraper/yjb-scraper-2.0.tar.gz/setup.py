from setuptools import find_packages, setup


setup(
    name="yjb-scraper",
    version="2.0",
    description="Scrape a user's VSCO profile data",
    author="yJb",
    author_email="bob@glob.com",
    packages=find_packages(),
    install_requires=[
        "tqdm",
        "requests",
        "beautifulsoup4",
    ],
    entry_points="""
        [console_scripts]
        vsco-scraper=vscoscrape:main
    """,
    keywords="none",
)
