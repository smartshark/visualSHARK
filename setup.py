#!/usr/bin/env python

from setuptools import find_packages, setup

from sntest.base import VERSION

setup(
    name='django-visualSHARK',
    version=VERSION,
    python_requires='>=3.6',
    install_requires=['pycoshark>=1.0.10', 'networkx>=2.0', 'pika'],
    dependency_links=['git+https://github.com/smartshark/pycoSHARK.git@1.0.10#egg=pycoshark-1.0.10'],
    packages=find_packages(),
    include_package_data=True,
    license='Apache 2.0 License',
    description='visualizations for SmartSHARK.',
    url='https://github.com/smartshark/visualSHARK',
    download_url='https://github.com/smartshark/visualSHARK/zipball/master',
    author='Alexander Trautsch',
    author_email='alexander.trautsch@cs.uni-goettingen.de',
    classifiers=[
        'Environment :: Web Environment',
        'Development Status :: 4 - Beta',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache2.0 License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
