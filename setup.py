from setuptools import setup, find_packages

setup(
    version="1.0",
    name="download_ust_rvc",
    packages=find_packages(),
    py_modules=["rvc_dl"],
    author="RapDoodle",
    install_requires=[
        'tqdm',
    ],
    description="Download UST's remote video capture (RVC) recordings.",
    entry_points={
        'console_scripts': ['rvc-dl=rvc_dl.rvc_dl:main'],
    },
    include_package_data=True,
)