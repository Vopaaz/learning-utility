from setuptools import setup, find_packages

setup(
    name='Lutil',
    version='0.1.0',
    description='This is a test of the setup',
    author='Vopaaz',
    author_email='liyifan945@163.com',
    url='https://vopaaz.github.io/',
    packages=find_packages(),
    install_requires=["pandas", "scikit-learn"],
)
