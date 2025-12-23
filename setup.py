from setuptools import setup, find_packages

setup(
    name="ai_structurer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["requests>=2.28.0"],
    description="Convert unstructured business text to strict JSON using Groq LLM",
    author="",
)
