from setuptools import setup, find_packages

setup(
    name="myhashcat",
    version="0.1.0",
    packages=find_packages(),
    package_dir={"": "."},
    install_requires=[
        "pyyaml>=5.1",
    ],
    entry_points={
        'console_scripts': [
            'myhashcat=src.cli:main',
        ],
    },
    author="Votre Nom",
    author_email="votre.email@example.com",
    description="Outil de génération de dictionnaires et d'interface avec Hashcat",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/votre-repo/myhashcat",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
) 