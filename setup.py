from setuptools import setup

setup(
    name="carafe",
    version="1.3.0",
    author="Jelmer van Arnhem",
    description="carafe is a tiny management tool for wine bottles/carafes",
    license="MIT",
    py_modules=["carafe"],
    include_package_data=True,
    python_requires=">= 3.5.*",
    setup_requires=["setuptools"],
    entry_points={"console_scripts": ["carafe= carafe:main"]}
)
