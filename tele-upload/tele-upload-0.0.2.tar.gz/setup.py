import setuptools
from tele_upload.cli import __version__

with open("README.md", "r") as readme_file:
	readme = readme_file.read()

setuptools.setup(
	name="tele-upload",
	version=__version__,
	author="Jak Bin",
	author_email="jakbin4747@gmail.com",
	description="upload files to your telegram channel or group with ypur telegram bot",
	long_description=readme,
	long_description_content_type="text/markdown",
	url="https://github.com/jakbin/tele-upload",
	install_requires=["tqdm","requests","requests-toolbelt"],
	python_requires=">=3",
	project_urls={
		"Bug Tracker": "https://github.com/jakbin/tele-upload/issues",
	},
	classifiers=[
		"Programming Language :: Python :: 3.6",
		"License :: OSI Approved :: MIT License",
		"Natural Language :: English",
		"Operating System :: OS Independent",
	],
	keywords='telegram,tele-upload,telegram-api,telegram-api-bot,telegram-file-upload,elegram-upload',
	packages=["tele_upload"],
	package_data={  
		'tele_upload': [
			'config.ini',
		]},
	entry_points={
		"console_scripts":[
			"tele-upload = tele_upload.cli:main"
		]
	}
)