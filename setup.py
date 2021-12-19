# This program will create a distribution package which is an archive file containing the source code for fwss along with all the necessary libraries. 
# Note that any python version later than 3.6 should work. Type python3 --version on your system to see what version of Python 3 is installed.

from setuptools import setup

setup (
      name='fwss',
      version='0.1',
      description='fop web socket service',
      url='www.urbanspacefarms.com',
      author='UrbanSpaceFarms',
      author_email='fwss@urbanspacefarms.com',
      # all the code is in the directory named python.
      packages = ['fwss']
      )
