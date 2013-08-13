import sys
import subprocess

from setuptools import setup

import distutils.core
        
setup(
    name = "notos",
    version = "0.1",
    package_dir = {
        'notos': 'src/notos',
    },
    packages = [
        'notos',
        'notos.migrations',
    ],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires = [
        'gcm-client>=0.1.3',
        'django-celery>=3.0.17',
        'Django>=1.5.1',
        'django-json-field>=0.5.4',
    ],

    author = "Sigmapoint",
    author_email = "karol.majta@sigmapoint.co",
    description = "Generic aproach to push messaging with django-rest-framework",
    license = "MIT",
    url = "http://sigmapoint.co",
)
