from setuptools import setup, find_packages
import os


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname)) as f:
        return f.read()


# Dynamically calculate the version based on anthill.framework.VERSION.
version = __import__('anthill.framework').get_version()


EXCLUDE_FROM_PACKAGES = [
    'anthill.framework.conf.project_template',
    'anthill.framework.conf.app_template',
    'anthill.framework.bin'
]


setup(
    name='anthill-framework',
    version=version,
    long_description=read('README.rst'),
    license='BSD',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    scripts=['anthill/framework/bin/anthill-admin.py'],
    install_requires=['tornado', 'pytz'],
    extras_require={

    },
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Framework :: Tornado',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        # 'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
