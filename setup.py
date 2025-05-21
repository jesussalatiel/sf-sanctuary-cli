"""Setup script for the sf-cli package."""

from pathlib import Path
from setuptools import setup, find_packages

readme_path = Path(__file__).parent / "README.md"
long_description = (
    readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""
)

setup(
    name="sf-cli",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Command-line interface for managing Salesforce users.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sf-cli",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    include_package_data=True,
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
    ],
    entry_points={
        "console_scripts": [
            "sf-cli=sf_users.sf_users_cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
)
