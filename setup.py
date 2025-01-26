import pathlib
from distutils.core import setup

exec(open('./src/MockServerLibrary/version.py').read())

HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(name='robotframework_mockserverlibrary',
      packages=['MockServerLibrary'],
      package_dir={'': 'src'},
      version=VERSION,
      description='Robot framework library for MockServer',
      long_description=README,
      author="Frank van der Kuur",
      author_email='frank.vanderkuur@bqa.nl',
      url="https://github.com/frankvanderkuur/robotframework-mockserverlibrary",
      keywords='testing robotframework mockserver mock stub',
      include_package_data=True,
      install_requires=["robotframework-requests", "robotframework-jsonlibrary"],
      classifiers=[])
