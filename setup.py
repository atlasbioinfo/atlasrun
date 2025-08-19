from setuptools import setup, find_packages

setup(
    name="atlasrun",
    version="0.1.0",
    description="A simple command queue management tool",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        # argparse is part of Python standard library
    ],
    entry_points={
        "console_scripts": [
            "arun=atlasrun.cli:main",
        ],
    },
    python_requires=">=3.7",
)
