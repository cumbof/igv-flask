import sys

import setuptools

from igv.igv import __version__

if sys.version_info[0] < 3 or (sys.version_info[0] == 3 and sys.version_info[1] < 6):
    sys.exit(
        "MetaSBT requires Python 3.6 or higher. Your current Python version is {}.{}.{}\n".format(
            sys.version_info[0], sys.version_info[1], sys.version_info[2]
        )
    )

setuptools.setup(
    author="Fabio Cumbo",
    author_email="fabio.cumbo@gmail.com",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    description="Flask webserver for rendering igv.js",
    download_url="https://pypi.org/project/igv-flask/",
    entry_points={"console_scripts": ["igv=igv.igv:main"]},
    install_requires=[
        "flask>=1.1.1"
    ],
    keywords=[
        "bioinformatics",
        "visualization"
    ],
    license="MIT",
    license_files=["LICENSE"],
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    name="igv-flask",
    packages=setuptools.find_packages(),
    package_data={
        "igv": [
            "static/*",
            "templates/*"
        ]
    },
    project_urls={
        "Source": "https://github.com/cumbof/igv-flask",
        "Wiki": "https://github.com/igvteam/igv.js/wiki",
    },
    python_requires=">=3.6",
    url="http://github.com/cumbof/igv-flask",
    version=__version__,
    zip_safe=False,
)
