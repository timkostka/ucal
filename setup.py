import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ucal",
    version="1.2.0",
    author="Tim Kostka",
    author_email="kostka@gmail.com",
    description='A calculator with automatic unit conversions',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/timkostka/ucal",
    packages=setuptools.find_packages(),
    package_data={'ucal_gui': ['*.ico']},
    install_requires=['pyperclip', 'wxPython'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
     ])
