# read the contents of your README file
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='flowable.external-worker-client',
    packages=['flowable', 'flowable.external_worker_client', 'flowable.robocorp_client'],
    version='1.0.1',
    description='Flowable External Worker Library to connect Python code to Flowable using an external worker.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Flowable',
    license='',
    install_requires=['requests>=2.27.0', 'robocorp-actions>=0.2.1', 'robocorp-tasks>=3.1.1', 'robocorp-truststore>=0.9.1'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'vcrpy'],
    test_suite='tests',
)
