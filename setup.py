from setuptools import find_packages, setup


setup(
    name="scaife-cts-api",
    version="0.0.1",
    packages=find_packages(),
    entry_points="""
        [console_scripts]
        scaife-cts-api=scaife_cts_api.__main__:cli
    """,
)
