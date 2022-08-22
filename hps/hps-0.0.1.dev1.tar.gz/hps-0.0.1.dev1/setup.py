import setuptools

with open("NAME.md", "r", encoding="utf-8") as fh:
    libname = fh.read()

setuptools.setup(
    name=libname,
    version="0.0.1.dev1",
    author="Xiaoyu Zhai",
    author_email="xiaoyu.zhai@hotmail.com",
    description=f"A placeholder for {libname} project",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
)