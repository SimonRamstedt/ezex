from setuptools import setup

setup(name='ezex',
      version='0.1',
      description='lightweigt destributed experimentation framework',
      url='no-url',
      author='Simon Ramstedt',
      author_email='simonramstedt@gmail.com',
      license='MIT',
      packages=['ezex'],
      scripts=['bin/ezex'],
      install_requires=['jupyter'],
      zip_safe=False)