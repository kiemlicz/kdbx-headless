import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="kdbx-headless",
    version="0.0.1",
    author="kiemlicz",
    author_email="stanislaw.dev@gmail.com",
    description="KDBX headless service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kiemlicz/kdbx-headless",
    install_requires=requirements,
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
