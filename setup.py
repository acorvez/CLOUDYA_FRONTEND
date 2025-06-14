#!/usr/bin/env python3
"""
Setup script pour Cloudya CLI
Installation recommandée : pip install .
"""

from setuptools import setup, find_packages
import os

# Lire le README pour la description longue
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "CLI DevOps intelligente pour l'automatisation d'infrastructures cloud"

# Lire les dépendances depuis requirements.txt
def read_requirements():
    req_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(req_path):
        with open(req_path, 'r', encoding='utf-8') as f:
            requirements = []
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # Ignorer les dépendances conditionnelles problématiques
                    if 'subprocess32' in line and 'python_version' in line:
                        continue
                    # Éviter les doublons
                    if line not in requirements:
                        requirements.append(line)
            return requirements
    return [
        'click>=8.0.0',
        'pyyaml>=6.0',
        'requests>=2.28.0',
        'rich>=12.0.0',
        'psutil>=5.9.0',
        'jinja2>=3.1.0',
        'typer>=0.9.0',
        'textual>=0.40.0'
    ]

setup(
    name="cloudya",
    version="1.0.0",
    author="acorvez",
    author_email="contact@cloudya.dev",
    description="CLI DevOps intelligente pour l'automatisation d'infrastructures cloud",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/acorvez/CLOUDYA_FRONTEND",
    project_urls={
        "Bug Reports": "https://github.com/acorvez/CLOUDYA_FRONTEND/issues",
        "Source": "https://github.com/acorvez/CLOUDYA_FRONTEND",
        "Documentation": "https://github.com/acorvez/CLOUDYA_FRONTEND#readme"
    },
    
    # Configuration des packages
    packages=find_packages(),
    include_package_data=True,
    
    # Point d'entrée de la CLI - CORRECT
    entry_points={
        'console_scripts': [
            'cloudya=cloudya.cli.main:main',
        ],
    },
    
    # Dépendances - SANS DUPLICATION
    install_requires=read_requirements(),
    
    # Métadonnées
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
        "Environment :: Console",
    ],
    
    # Version Python minimale
    python_requires=">=3.8",
    
    # Mots-clés pour PyPI
    keywords="devops, cloud, infrastructure, automation, terraform, ansible, cli",
    
    # Fichiers de données à inclure
    package_data={
        'cloudya': [
            'templates/**/*',
            'templates/**/*.j2',
            'templates/**/*.tf',
            'templates/**/*.yml',
            'templates/**/*.yaml',
            'config/*.yaml',
            'config/*.yml',
        ],
    },
    
    # Options pour le développement
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'black>=22.0.0',
            'flake8>=5.0.0',
            'mypy>=1.0.0',
        ],
        'docs': [
            'sphinx>=5.0.0',
            'sphinx-rtd-theme>=1.0.0',
        ]
    },
    
    # Configuration pour les wheels
    zip_safe=False,
)
