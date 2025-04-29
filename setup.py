from setuptools import setup, find_packages

setup(
    name="h2_gym",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"":"src"},
    include_package_data=True,
    package_data={
        'h2_gym': ['data/*.csv'],  # adjust as needed
    },
    install_requires = [
        "meteor_py  @ git+https://github.com/cja119/meteor_py.git",
        "numpy",
        "jax",
        #"mu_F @ git+https://github.com/mawbray/mu.F.git"
    ], 
    extras_require={
        "supply": ["gymnasium"],
        "shipping": ["pyomo"],
        "all": [
            "gymnasium",
            "pyomo",
        ]
    }
)
