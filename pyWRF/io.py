# -*- coding: utf-8 -*-

'''
@Description: A class get WRF output file handler wrapped 
@Author: Hejun Xie
@Date: 2019-12-31 16:04:04
@LastEditors  : Hejun Xie
@LastEditTime : 2020-01-01 21:02:20
'''

# global import
import netCDF4 as nc
import numpy as np
import os
import gc
import warnings

# local import
from pyWRF.derived_vars import DERIVED_VARS, get_derived_var
import pyWRF.data as d

# netcdf attributes
_nc_builtins = ['__class__', '__delattr__', '__doc__', '__getattribute__', '__hash__', \
            '__init__', '__module__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', \
            '__setattr__', '__str__', '__weakref__', '__getitem__', '__setitem__', '__len__' ]

_nc_localatts = ['variables', 'dimensions', 'groups']

def open_file(fname): # Just create a file_instance class
    return FileClass(fname)

def get_alias_dic():
    cur_path=os.path.dirname(os.path.realpath(__file__))
    f = open(cur_path+'/WRF_modelvar_alias.txt', 'r')
    dic={}
    for line in f:
        line=line.strip('\n')
        line=line.split(',')
        dic[line[0]]=line[1]
    return dic

class FileClass(object):
    def __init__(self, fname):
        bname = os.path.basename(fname)
        name, extname = os.path.splitext(bname)


        print('--------------------------')
        print('Reading file '+ fname)

        # check if the file exists
        if not os.path.exists(fname):
            warnings.warn('File not found! Aborting...')
            return None
        
        # check the file extension name
        if extname == '':
            print('Input file has no extension, assuming it is NetCDF...')
            file_format = 'ncdf'
        elif extname in ['.nc', '.cdf', '.netcdf', '.nc3', '.nc4']:
            print('Input file is NetCDF file')
            file_format = 'ncdf'
        else:
            warnings.warn('Invalid data type, must be GRIB or NetCDF, aborting...' )
            return None
        
        # get file handle
        _fhandle = nc.open_file(fname, 'r')

        self._handle = _fhandle
        self.name = fname
        self.format = file_format
        self.dic_variables = {}

        print('File ' + fname + ' read successfully')
        print('--------------------------')
        print('')
    
    def __getattribute__(self, attrib):
        if attrib in _nc_localatts or attrib in _nc_builtins:
            return self._handle.__getattribute__(attrib)
        else:
            return object.__getattribute__(self,attrib)
    
    def close(self):
        del self.dic_variables
        self._handle.close()
        gc.collect() # Force garbage collection

    def check_varname(self, varname):
        varname_checked = ''

        # first check if the varname is in modelvar
        list_vars = np.asarray(self.variables.keys())

        if varname in list_vars or varname in DERIVED_VARS:
            varname_checked = varname
        else:
            dic = get_alias_dic()
            if varname in dic.keys():
                varname_checked = dic[varname]
        
        return varname_checked

    def get_variable(self, var_names, itime=0, get_proj_info=True, assign_heights=False, shared_heights=False):
        
        # Create dictionary of options
        # share height means share topograph
        import_opts = {'itime':itime
                       'get_proj_info':get_proj_info,\
                       'shared_heights':shared_heights,\
                       'assign_heights':assign_heights}
        
        if isinstance(var_names, list):
            dic_var = {} # only return those wanted vars
            for i,v in enumerate(var_names):
                var = self.get_variables(v, **import_opts)
                if assign_heights:
                    if i > 0 and shared_heights:
                    # Stop assigning heights, after first variable
                    import_opts['assign_heights'] = False
                    # If shared_heights is true we just copy the heights from the first variables to all others
                    var.attributes['z-levels'] = dic_var[var_names[0]].attributes['z-levels']
                    var.attributes['topograph'] = dic_var[var_names[0]].attributes['topograph']

                dic_var[v] = var
            return dic_var
        else:
            print('--------------------------')
            print('Reading variable ' + var_names)
            
            # check if already read
            if var_names in self.dic_variables.keys():
                var = self.dic_variables[var_names]
            elif var_names in DERIVED_VARS:
                var = get_derived_var(self,var_names,import_opts)
            else:
                varname_checked = self.check_varname(var_names)
                if varname_checked != '':
                    var = d.DataClass(self, varname_checked, get_proj_info=get_proj_info, itime=itime)
                else:
                    print('Variable was not found in file_instance')
                    return
            
            self.dic_variables[var_names] = var

            # Assign heights if wanted
            if assign_heights and var:
                var.assign_heights()

            print 'Variable was read successfully'
            print('--------------------------' )
            print('')
            return var

    def check_if_variables_in_file(self, varnames):
        for var in varnames:
            varname_checked = self.check_varname(var)
            if varname_checked == '':
                return False
        return True


if __name__ == '__main__':
    import pyWRF as pw
    file_h = pw.open_file('../../cosmo_pol/pathos/WRF/wsm6/wrfout_d03_2013-10-06_00_00_00')
    
    QR = file_h.get_variable('QR', assign_heights=True)
    N = file_h.get_variable('N', assign_heights=True)
