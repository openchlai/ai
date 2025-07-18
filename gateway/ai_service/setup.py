#setup.py
from setuptools import setup, find_packages

setup(
    name="ai-service",
    version="0.1.0",
    description="AI-powered Django backend for transcription, classification, summarization, and insights.",
    author="Your Name or Org",
    packages=find_packages(),
    include_package_data=True,  # Includes files specified in MANIFEST.in
    install_requires=[
        "Django>=3.2",
        "djangorestframework",
        "whisper",
        "transformers",
        "torch",
        "PyYAML",
        "pydub",
        "spacy==3.8.0",
        "gunicorn==20.1.0",
        # Direct spaCy model wheel from GitHub
        # "en_core_web_md @ https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl",
    ],
    entry_points={
        "console_scripts": [
            "openchs = ai_service.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Django",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Natural Language :: English",
    ],
    python_requires='>=3.8',
)
