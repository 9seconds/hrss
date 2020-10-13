#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import setuptools


with open("README.rst", "rt") as readme_fp:
    long_description = readme_fp.read().strip()


REQUIREMENTS = (
    "inotify_simple",
    "enum34"
)


setuptools.setup(
    name="concierge",
    version="0.2.3",
    description="Maintainable SSH config",
    long_description=long_description,
    url="https://github.com/Tr4sK/concierge",
    author="Sergey Arkhipov",
    author_email="serge@aerialsounds.org",
    maintainer="Tr4sK",
    maintainer_email="github@tr4sk.me",
    license="MIT",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=REQUIREMENTS,
    entry_points={
        "console_scripts": [
            "concierge = concierge.endpoints.daemon:main",
            "concierge-check = concierge.endpoints.check:main"
        ],
        "concierge.templater": [
            "dummy = concierge.templater:Templater"
        ]
    },
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ]
)
