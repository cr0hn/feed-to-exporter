from os import path
from os.path import join, abspath, dirname
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst')) as f:
    readme = f.read()

with open(join(here, 'requirements.txt')) as f:
    required = f.read().splitlines()

with open(join(abspath(dirname(__file__)), "VERSION"), "r") as v:
    VERSION = v.read().replace("\n", "")

setup(
    name='feed-to-exporter',
    version=VERSION,
    packages=find_packages(),
    long_description=readme,
    install_requires=required,
    include_package_data=True,
    url='https://github.com/cr0hn/feed-to-exporter',
    license='BSD 3 License',
    author='cr0hn[-at-]cr0hn.com',
    description='Export RSS Feed as different outputs: Wordpress, MongoDB',
    entry_points={'console_scripts': [
        'f2e = feed_to_exporter.__main__:main',
    ]},
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
    ],
)

