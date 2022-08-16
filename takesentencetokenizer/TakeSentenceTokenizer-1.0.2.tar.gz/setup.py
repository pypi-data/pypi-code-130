import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()	

setuptools.setup(
    name="TakeSentenceTokenizer",
    version="1.0.2",
    author="Karina Tiemi Kato",
    author_email="karinat@take.net",
	keywords='Tokenization',
    description="TakeSentenceTokenizer is a tool for tokenizing and pre processing messages",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
	install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	package_data = {
		'SentenceTokenizer': ['dictionaries/*.json', 'dictionaries/*.txt'],
	},
	include_package_data = True
)