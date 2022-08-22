import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bing_hashing_image_downloader",
    version="22.8.22.1840",
    author="Jeremiah Korreck (fork), Guru Prasad Singh (original)",
    author_email="korreckj328@gmail.com",
    description="Python library to download bulk images from Bing.com without repeated images",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/korreckj328/bing_hashing_image_downloader",
    keywords=['bing', 'images', 'scraping', 'image download', 'bulk image downloader','sha1'],
    packages=['bing_hashing_image_downloader'],
    classifiers=[
	"Programming Language :: Python :: 3",
	"License :: OSI Approved :: MIT License",
	"Operating System :: OS Independent",
        ]
)
