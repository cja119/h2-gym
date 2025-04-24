from setuptools import setup, find_packages

setup(
    name="vc_gym",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    include_package_data=True,
    package_data={
        'vc_gym': ['data/*.csv'],  # adjust as needed
    },
    install_requires = [
        "meteor_py  @ git+https://github.com/cja119/meteor_py.git",
        "numpy",
        "jax"
    ]
)
