from setuptools import setup

# Explicitly define the version instead of importing from the package
version = '0.1.2'

setup(
    name='lomap',
    version=version,
    description='LTL Optimal Multi-Agent Planner (LOMAP)',
    long_description='',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    url='https://github.com/wasserfeder/lomap',
    author='Alphan Ulusoy, Cristian-Ioan Vasile',
    author_email='cvasile@mit.edu',
    license='GNU GPLv2',
    packages=['lomap', 'lomap.algorithms', 'lomap.classes'],
    package_dir={'lomap': 'lomap'},
    install_requires=[
        'networkx>=1.11',
        'pp>=1.6.2',
        'matplotlib>=1.3.1',
        'setuptools>=1.1.6',
    ],
    zip_safe=False
)
