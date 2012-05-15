import os

from setuptools import setup, find_packages

from iso3166 import __version__ as version

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)
for dirpath, dirnames, filenames in os.walk('iso3166'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[8:] # Strip "iso3166/" or "iso3166\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))


setup(name = "django-iso3166",
      version=version,
      description = "This is a application for Django projects providing list of world countries based on ISO3166.",
      long_description='\n\n'.join([read("README"), read("CHANGELOG")]),
      author = 'Co-Capacity',
      author_email = 'django-iso3166@co-capacity.org',
      url='https://trac.co-capacity.biz/trac/cocap/wiki/django-ISO3166',
      download_url='http://pypi.python.org/pypi/django-iso3166',
      package_dir={'iso3166': 'iso3166'},
      packages=packages,
      package_data={'iso3166': data_files},
      install_requires = ['setuptools'],
      zip_safe=False,
      classifiers = [
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP',
      ]
)
