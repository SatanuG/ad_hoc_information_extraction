from setuptools import setup, find_packages

setup(
    name='ad_hoc_information_extraction',
    version='1.1',
    packages=find_packages(exclude=('tests', 'data')),
    package_dir={'' : ''},
    url='https://github.com/SatanuG/ad_hoc_information_extraction',
    license='MIT',
    author='Satanu Ghosh',
    author_email='satanu.ghosh@unh.edu',
    description='code corresponding to our paper Toward Reliable Ad-hoc Scientific Information Extraction: A Case Study on Two Materials Datasets (https://arxiv.org/abs/2406.05348)'
)
