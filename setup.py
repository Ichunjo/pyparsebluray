import setuptools


with open('README.md') as fh:
    long_description = fh.read()

with open("requirements.txt") as fh:
    install_requires = fh.read()

NAME = 'pyparsebluray'
VERSION = '0.1.0'

setuptools.setup(
    name=NAME,
    version=VERSION,
    author='Vardë',
    author_email='ichunjo.le.terrible@gmail.com',
    description='Parse and extract binary data from bluray files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['pyparsebluray', 'pyparsebluray.mpls'],
    url='https://github.com/Ichunjo/pyparsebluray',
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
    install_requires=install_requires,
)
