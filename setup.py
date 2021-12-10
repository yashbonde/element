import setuptools
import os

readme = os.path.join(os.path.split(os.path.abspath(__file__))[0], "README.md")
with open(readme, "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="elemental_api",
    version="0.1",
    author="Yash Bonde",
    author_email="bonde.yash97@gmail.com",
    description="Convert any python module to FastAPI compatible server. YoCo!",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yashbonde/element",
    project_urls={
        "Bug Tracker": "https://github.com/yashbonde/element/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"elemental_api": "elemental_api"},
    python_requires=">=3.6",
)
