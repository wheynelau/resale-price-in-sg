from setuptools import setup, find_packages

with open("workflow_requirements.txt", "r", encoding="utf-8") as f:
    requirements = f.read().splitlines()

setup(
    name="my_project",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
    package_dir={"": "./"},
)
