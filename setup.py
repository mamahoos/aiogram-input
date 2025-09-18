from setuptools import setup, find_packages

setup(
    name='aiogram_input',
    version='2.2.0', 
    packages=find_packages(),
    install_requires=[
        'aiogram>=3.0.0',
    ],
    author='mamahoos',
    author_email='m4m4hoos@example.com',  
    description='A modular, multi-client library for aiogram to handle user response waiting in Telegram bots.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
    url='https://github.com/mamahoos/aiogram-input',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)