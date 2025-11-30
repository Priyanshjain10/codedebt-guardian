"""Setup configuration for CodeDebt Guardian package"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="codedebt-guardian",
    version="1.0.0",
    author="Priyansh Jain",
    author_email="priyanshj1304@gmail.com",
    description="🤖 AI-Powered Multi-Agent System for Technical Debt Detection",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Priyanshjain10/codedebt-guardian",
    project_urls={
        "Bug Tracker": "https://github.com/Priyanshjain10/codedebt-guardian/issues",
        "Documentation": "https://github.com/Priyanshjain10/codedebt-guardian#readme",
        "Source Code": "https://github.com/Priyanshjain10/codedebt-guardian",
        "Kaggle": "https://www.kaggle.com/code/priyanshjain01/codedebt-guardian-multi-agent-technical-debt-sys",
    },
    packages=find_packages(exclude=['tests*', 'docs*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Bug Tracking",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "codedebt=codedebt_guardian.cli:main",
        ],
    },
    keywords="technical-debt code-analysis multi-agent ai gemini code-quality static-analysis",
    include_package_data=True,
    zip_safe=False,
)
