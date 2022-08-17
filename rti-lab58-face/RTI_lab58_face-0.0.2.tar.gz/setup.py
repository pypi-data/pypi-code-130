import setuptools


setuptools.setup(
    name="RTI_lab58_face",
    version="0.0.2",
    author="INF",
    author_email="rnsbhargav@gmail.com",
    description="Art",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ],
    entry_points={
        "console_scripts":
        ["RTI_lab58_face = RTI_lab58_face.main:cli"],
    },
    python_requires='>=3.5.5',
    install_requires=["numpy>=1.14.0", "pandas>=0.23.4", "tqdm>=4.30.0", "gdown>=3.10.1", "Pillow>=5.2.0", "opencv-python>=4.5.5.64", "tensorflow>=1.9.0", "keras>=2.2.0", "Flask>=1.1.2", "mtcnn>=0.1.0", "retina-face>=0.0.1", "fire>=0.4.0"]
)
