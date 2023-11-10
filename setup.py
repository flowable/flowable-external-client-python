from setuptools import find_packages, setup

# read the contents of your README file
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='flowable.external-worker-client',
    packages=['flowable', 'flowable.external_worker_client'],
    version='1.0.0.rc2',
    description='Flowable External Worker Library to connect Python code to Flowable using an external worker.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Flowable',
    license='',
    install_requires=['requests>=2.27.0'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'vcrpy'],
    test_suite='tests',
)
