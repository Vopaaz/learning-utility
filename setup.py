from setuptools import setup, find_packages

with open(r'README.md',"r",encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='Lutil',
    version='0.1.7',
    author='Vopaaz',
    author_email='liyifan945@163.com',
    url='https://github.com/Vopaaz/learning-utility',
    description='Assist small-scale machine learning.',
    long_description = long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=["pandas", "chardet", "numpy", "joblib"],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
    ],
)
