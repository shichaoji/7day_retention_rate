try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'My Project',
    'author': 'Shichao_Ji',
    'author_email': 'shichao.ji@uconn.edu',
    'version': '0.1',
    'install_requires': ['pandas','bokeh','nose'],
    'packages': ['scripts'],
    'scripts': [],
    'name': '7day_retention'
}

setup(**config)
