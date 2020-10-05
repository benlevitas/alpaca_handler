import os
import setuptools

with open('README.md') as readme_file:
    README = readme_file.read()

with open(os.path.join(".dev", "requirements.txt")) as reqs:
    REQUIREMENTS = reqs.readlines()

setuptools.setup(
    name='alpaca-handler',
    version='0.0.1',
    description='Alpaca API python client handler',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Ben Levitas',
    author_email='',
    url='https://github.com/benlevitas/alpaca_handler',
    packages=setuptools.find_packages(),
    install_requires=REQUIREMENTS,
    setup_requires=[],
)
