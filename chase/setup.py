from setuptools import setup

setup(
    name="chase",
    version="0.1",
    description="A simulation of a wolf chasing sheep",
    author="Wojciech Stefaniak, Maja Frydlewska",
    author_email="236657@edu.p.lodz.pl, 236527@edu.p.lodz.pl",
    packages=["chase"],
    package_dir={"chase": "src/chase"},
    entry_points={
        "console_scripts": [
            "chase=chase.__main__:main",
        ],
    },
)
