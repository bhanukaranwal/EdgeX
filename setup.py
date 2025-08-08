from setuptools import setup, find_packages

setup(
    name='EdgeX',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'pandas', 'numpy', 'pyyaml', 'flask', 'kiteconnect', 'scikit-learn', 'requests'
    ],
    author='Your Name',
    description='Automated Options Trading Bot',
    url='https://github.com/yourusername/EdgeX',
)
