import re
from setuptools import setup


version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('modfree/modfree.py').read(),
    re.M
    ).group(1)


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")
    
    
setup(
    name = "modelfree-protein15n",
    packages = ["modfree"],
    entry_points = {
        "console_scripts": ['modfree = modfree.modfree:main']
        },
    version = version,
    description = "Model free analysis of protein backbone amide 15N spin relaxation rates.",
    long_description = long_descr,
    long_decription_content_type="test/markdown",
    author = "Vincent Schnapka",
    author_email = "vincentschnapka@gmail.com",
    url="https://github.com/VSchnapka/modelfree-protein15n.git",
    install_requires=[
        'numpy',
        'scipy',
        'lmfit',
        'matplotlib',
        'rich',
        'tomli',
        'seaborn',
    ]
    classifiers = [
        "Programming Language :: Python :: 3",
        ],
    extras_requires = {
        "dev": [
            "pytest>=3.7",
            ],
        },
    )
