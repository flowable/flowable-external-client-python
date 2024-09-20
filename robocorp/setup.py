# read the contents of your README file
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='flowable.robocorp-client',
    packages=['flowable', 'flowable.robocorp_client'],
    version='1.0.0rc1',
    description='Flowable client to be used with Robocorp. This client connects to a Flowable instance via external worker and executes robocorp tasks or actions.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Flowable',
    license='Apache License, Version 2.0',
    install_requires=['flowable.external-worker-client>=1.0.1rc1', 'robocorp-actions>=0.2.1', 'robocorp-tasks>=3.1.1', 'robocorp-truststore>=0.9.1'],
    extras_require={
        'testing': ['pytest', 'vcrpy']
    },
)