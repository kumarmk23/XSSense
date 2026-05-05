from setuptools import setup, find_packages

setup(
    name="xssense",
    version="1.0.0",
    description="A context-aware reflected XSS assistant for penetration testers",
    author="XSSense Contributor",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "typer>=0.9.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "xssense=contextxss.cli:app",
        ],
    },
)
