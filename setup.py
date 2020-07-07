from setuptools import setup, find_packages, Extension
from codecs import open
from os import path
import sys
from setuptools import dist  # Install numpy right now
dist.Distribution().fetch_build_eggs(['numpy>=1.11.2'])

try:
    import numpy as np
except ImportError:
    exit('Please install numpy>=1.11.2 first.')

try:
    from Cython.Build import cythonize
    from Cython.Distutils import build_ext
except ImportError:
    USE_CYTHON = False
else:
    USE_CYTHON = True

__version__ = '1.1.0'

here = path.abspath(path.dirname(__file__))



# get the dependencies and installs
with open(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '')
                    for x in all_reqs if x.startswith('git+')]

cmdclass = {}
print("---------------", USE_CYTHON)
ext = '.pyx' if USE_CYTHON else '.c'
print('pxt===c')
extensions = [
    Extension(
        'QPQ.similarities',
        ['QPQ/similarities' + ext],
        include_dirs=[np.get_include()]
    ),
    Extension(
        'QPQ.prediction_algorithms.matrix_factorization',
        ['QPQ/prediction_algorithms/matrix_factorization' + ext],
        include_dirs=[np.get_include()]),
    Extension('QPQ.prediction_algorithms.optimize_baselines',
              ['QPQ/prediction_algorithms/optimize_baselines' + ext],
              include_dirs=[np.get_include()]),
    Extension('QPQ.prediction_algorithms.slope_one',
              ['QPQ/prediction_algorithms/slope_one' + ext],
              include_dirs=[np.get_include()]),
    Extension('QPQ.prediction_algorithms.co_clustering',
              ['QPQ/prediction_algorithms/co_clustering' + ext],
              include_dirs=[np.get_include()]),
]
print('set language level 3')
if USE_CYTHON:
    ext_modules = cythonize(extensions, compiler_directives={'language_level' : "3"})
    cmdclass.update({'build_ext': build_ext})
else:
    ext_modules = extensions
print('setup')
# setup(
# )
setup(
    name='QPQ',
    author='QuachPhuQuoc',
    author_email='quachphuquoc@gmail.com',
    github='https://github.com/quachphuquoc',
    description=('recommender systems'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='recommender recommendation system',

    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    ext_modules=ext_modules,
    cmdclass=cmdclass,
    install_requires=install_requires,
    dependency_links=dependency_links,

    entry_points={'console_scripts':
                  ['QPQ = QPQ.__main__:main']},
)


print('Done install')
