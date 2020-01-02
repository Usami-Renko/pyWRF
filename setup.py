'''
@Description: 
@Author: Hejun Xie
@Date: 2019-12-29 18:41:03
@LastEditors: Hejun Xie
@LastEditTime: 2020-01-02 16:34:07
'''
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
        package_data   = {'pyWRF' : ['WRF_modelvar_alias.txt']},
        install_requires=['numpy','netCDF4', 'pyproj'],
        zip_safe=False
        )
