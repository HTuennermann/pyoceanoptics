try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'pyoceanoptics',
    'author': 'Henrik Tuennermann',
    'url': 'https://github.com/tuehen/pyoceanoptics',
    'download_url': 'https://github.com/tuehen/pyoceanoptics',
    'author_email': 'tuennermann@gmail.com',
    'version': '0.11',
    'install_requires': ['pyusb','numpy'],
    'packages': ['pyoceanoptics'],
    'scripts': [],
    'name': 'pyoceanoptics'
}

setup(**config)