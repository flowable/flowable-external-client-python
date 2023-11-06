from setuptools import find_packages, setup

setup(
    name='flowable.external-worker-client',
    packages=find_packages(include=['flowable.external-worker-client']),
    version='1.0.dev1',
    description='Flowable External Worker Library to connect Python code to Flowable using an external worker.',
    author='Flowable',
    license='',
    install_requires=['requests'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'vcrpy'],
    test_suite='tests',
)
