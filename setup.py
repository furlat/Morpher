from setuptools import setup, find_packages

setup(
    name="morpher",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic",
        "openai>=1.0.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A framework for structured AI transformations using OpenAI's API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/Morpher",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)