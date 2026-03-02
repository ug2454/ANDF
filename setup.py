from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="andf",
    version="1.0.0",
    description="AI Native Document Format — self-contained HTML documents with embedded JSON",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="ANDF Authors",
    python_requires=">=3.8",
    packages=find_packages(exclude=["tests*", "examples*"]),
    entry_points={
        "console_scripts": [
            "andf=andf.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
