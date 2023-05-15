import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('modfree/modfree.py').read(),
    re.M
    ).group(1)


with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")
    
    
setup(
    name = "modelfree-amide15N-lmft",
    packages = ["modfree"],
    entry_points = {
        "console_scripts": ['modfree = modfree.modfree:main']
        },
    version = version,
    description = "Model free analysis of protein backbone amide 15N spin relaxation rates.",
    long_description = long_descr,
    author = "Vincent Schnapka",
    author_email = "vincentschnapka@gmail.com",
    install_requires=[
        'numpy',
        'scipy',
        'lmfit',
        'matplotlib',
        'rich',
        'tomli',
    ]
    )