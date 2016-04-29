from setuptools import setup

setup(name='ezex',
      version='0.2.7',
      description='lightweigt destributed experimentation framework',
      url='https://github.com/SimonRamstedt/ezex',
      author='Simon Ramstedt',
      author_email='simonramstedt@gmail.com',
      license='MIT',
      packages=['ezex'],
      scripts=['bin/ezex'],
      install_requires=['jupyter'],
      zip_safe=False,
      include_package_data=True)