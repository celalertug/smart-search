import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smsearch",
    version="0.1.3",
    author="Celal Ertug",
    author_email="celalertug@gmail.com",
    description="A recursive file searcher with boolean expressions.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/celalertug/smart-search",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pyparsing",
        "colorama",
        "pyperclip",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'smsearch=smsearch.main:main',
        ],
    },
)