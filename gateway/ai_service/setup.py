from setuptools import setup, find_packages

setup(
    name="ai-service",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,  # Includes files from MANIFEST.in
    install_requires=[
        "Django>=3.2",
        "djangorestframework",
        "whisper",
        "transformers",
        "torch",
        "PyYAML",
        "pydub",
        "spacy==3.8.0",
        # spaCy model from direct wheel URL
        "en_core_web_md @ https://github.com/explosion/spacy-models/releases/download/en_core_web_md-3.8.0/en_core_web_md-3.8.0-py3-none-any.whl",
    ],
    entry_points={
        "console_scripts": [
            "openchs = ai_service.cli:main"
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
