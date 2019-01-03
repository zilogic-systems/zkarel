from setuptools import setup
import os

setup(
    name = "zkarel",
    version = os.getenv("KAREL_VERSION"),
    author = "Vijay Kumar",
    author_email = "code@zilogic.com",
    description = "A Karel like environment for learning programming.",
    license = "Apache 2.0",
    packages = ['zkarel'],
    package_data = {"zkarel": ["levels.json", "images/*.gif", "workspace/*/*"]},
    include_package_data = True,
    entry_points = {
        "console_scripts": ["karel-sim = zkarel.karelsim:main",
                            "karel-init = zkarel.karelenv:main"]
    },
)
