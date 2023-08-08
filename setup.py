from setuptools import find_packages, setup

setup(
    name='flowableexternalworker',
    packages=find_packages(include=['flowableexternalworker']),
    version='0.0.1',
    description='Flowable External Worker Library to write code using an external worker.',
    author='Flowable',
    license='',
    install_requires=['requests'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)
