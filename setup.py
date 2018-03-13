from setuptools import setup, find_packages


setup(
    name="scaife-cts-api",
    version="0.0.1",
    packages=find_packages(),
    install_requires=[
        "Click",
    ],
    entry_points="""
        [console_scripts]
        scaife-cts-api=scaife_cts_api.__main__:cli
    """,
)
