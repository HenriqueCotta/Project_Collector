from setuptools import setup, find_packages

setup(
    name="project_collector",
    version="0.1.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'projcol=project_collector.cli:main',
        ],
    },
    install_requires=[],
    include_package_data=True,
)