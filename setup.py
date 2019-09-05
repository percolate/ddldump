"""Setup file to automate the install of ddldump in the Python environment."""
from setuptools import setup
from ddldump.constants import VERSION


setup(
    name='ddldump',
    version=VERSION,
    author='Laurent Raufaste',
    author_email='analogue@glop.org',
    url='https://github.com/percolate/ddldump',
    description=('Dump a clean version of the DDLs of your tables, so you can '
                 'version them.'),
    keywords=('ddldump ddl dump sql mysql postgresql sqlalchemy mysqldump '
              'pg_dump'),
    license='GPLv3',
    packages=['ddldump'],
    install_requires=['docopt', 'sqlalchemy'],
    entry_points={
        'console_scripts': [
            'ddldump=ddldump.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        ('License :: OSI Approved :: '
         'GNU General Public License v3 or later (GPLv3+)'),
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
