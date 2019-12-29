from setuptools import setup, Extension, Command

# setup
setup(  name        = "pyWRF",
        description = "python interface to read and plot WRF output data",
        version     = "1.0",
        url='https://github.com/Usami-Renko/pyWRF',
        author='Hejun Xie - Zhejiang University',
        author_email='hejun.xie@zju.edu.cn',
        license='GPL-3.0',
        packages=['pyWRF'],
        install_requires=['numpy','netCDF4'],
        zip_safe=False
        )
