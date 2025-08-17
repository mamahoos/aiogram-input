from setuptools import setup, find_packages

setup(
    name='aiogram_ask',
    version='0.1.1', 
    packages=find_packages(),
    install_requires=[
        'aiogram>=3.0.0',
    ],
    author='mamahoos',
    description='A modular, multi-client library for aiogram to handle user response waiting in Telegram bots.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
)