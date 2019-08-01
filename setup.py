from setuptools import setup, find_packages

setup(
    name='pdlearn',
    version='0.0.1dev',
    description='This is a test of the setup',
    author='Vopaaz',
    author_email='liyifan945@163.com',
    url='https://vopaaz.github.io/',
    packages=find_packages(),
    install_requires=["pandas", "scikit-learn"],
)
