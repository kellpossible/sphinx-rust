from setuptools import setup

setup(
    name = "sphinxrust",
    packages = ["sphinxrust"],
    version = "0.1",
    author = "Luke Frisken",
    author_email = "cthunes@brewtab.com",
    url = "http://github.com/kellpossible/sphinx-rust",
    description = "Sphinx extension for documenting Rust projects",
    license = "Apache 2.0",
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 1 - Alpha",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries"
        ],
    install_requires=[
        "future",
        "docutils",
        "sphinx"
    ],
    long_description = """\
==========
sphinxrust
==========

sphinxrust is a Sphinx extension which adds support for rust language directives,
and external references to rust api documentation.
"""
)