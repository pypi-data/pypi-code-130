import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PTTAPI",
    packages=setuptools.find_packages(),
    version="0.0.5",
    license='MIT',
    author="Avilash Kumar/aswiro",
    author_email="areff.hirad@gmail.com",
    description="Unofficial TikTok API wrapper in Python with Async",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aswiro/PTTAPI",
    download_url='https://github.com/aswiro/PTTAPI',
    keywords=['tiktok', 'python', 'api', 'tiktok-api', 'tiktok api'],
    install_requires=[
        'requests',
        'pyppeteer',
        "pyppeteer_stealth"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
    ],
    include_package_data=True
)
