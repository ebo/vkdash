"""vkdash version/release information"""

# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
_version_major = 0
_version_minor = 1
_version_micro = ''  # use '' for first of series, number for 1 and above
_version_extra = 'dev'
# _version_extra = ''  # Uncomment this for full releases

# Construct full version string from these.
_ver = [_version_major, _version_minor]
if _version_micro:
    _ver.append(_version_micro)
if _version_extra:
    _ver.append(_version_extra)

__version__ = '.'.join(map(str, _ver))

CLASSIFIERS = ["Development Status :: 4 - Beta",
               "Environment :: Console",
               "Environment :: Web Environment",
               "Intended Audience :: Developers",
               "License :: OSI Approved :: NASA1.3",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Software Development :: Testing"]

description = "VKDash: TAP compliant dashpoard"

# Note: this long_description is actually a copy/paste from the top-level
# README.txt, so that it shows up nicely on PyPI.  So please remember to edit
# it only in one place and sync it correctly.
long_description = """
===================================================
VKDash: timeseries TAP compliant dashpoard
===================================================

...
"""

NAME = "vkdash"
MAINTAINER = "John (EBo) David"
MAINTAINER_EMAIL = "John.L.David@NASA.gov"
DESCRIPTION = description
LONG_DESCRIPTION = long_description
URL = "http://developer.nasa.gov/jldavid3/vkdash"
DOWNLOAD_URL = "http://developer.nasa.gov/jldavid3/vkdash/downloads"
LICENSE = "NASA-1.3"
AUTHOR = "Jesse R. Meyer"
AUTHOR_EMAIL = "Jesse.R.Meyer@NASA.gov"
PLATFORMS = "OS Independent"
MAJOR = _version_major
MINOR = _version_minor
MICRO = _version_micro
VERSION = __version__

# FIXME: add to this...
PACKAGE_DATA = {"vkdash": ["LICENSE"
                           #, "tests/*.txt", "tests/*.npy",
                           # "data/*.nii.gz","data/*.txt", "data/*.csv"
                          ]}
REQUIRES = [] # "numpy", "matplotlib", "scipy"]

ENTRY_POINTS = {'console_scripts': ['vkdashboard=vkdash.dashboard:main',
                                    'vkprove=vkdash.tap.prove:main']}
