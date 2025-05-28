from setuptools import setup, find_packages

setup(
    name="championship_leverage_index",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "basketball_reference_web_scraper",
    ],
    python_requires=">=3.8",
) 