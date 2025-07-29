# STRICTLY A SOCIAL MEDIA PLATFORM
# Intellectual Property & Artistic Inspiration
# Legal & Ethical Safeguards
from setuptools import setup

APP = ['validate_hypothesis.py']
OPTIONS = {
    'argv_emulation': True,
    'plist': {'CFBundleName': 'SuperNova 2177'},
}

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
