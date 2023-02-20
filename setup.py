import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="rtdicomtools",
    version="1.0.0",
    author="Sebastian Schäfer",
    author_email="se.schaefer@uke.de",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sebasj13/RTDICOMTools",
    project_urls={"Bug Tracker": "https://github.com/sebasj13/RTDICOMTools/issues",},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    
    install_requires=[
        "numpy",
        "opencv-python",
        "Pillow",
        "matplotlib",
        "pandas",
        "pydicom",
        "customtkinter"
    ],
    packages=[
        "rtdicomtools"
    ],
    keywords=["medical", "physics", "DICOM", "radiotherapy","3D numpy viewer", "RTPLAN", "RTSTRUCT"],
    python_requires=">=3.8",
)

