from setuptools import setup, find_packages

setup(
    name="Project_Collector",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'projcol=src.cli:run',
        ],
    },
    install_requires=[],
    include_package_data=True,
)