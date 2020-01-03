# -*- coding: utf-8 -*-

'''
@Description: A class get WRF output file handler wrapped 
@Author: Hejun Xie
@Date: 2019-12-31 16:04:04
@LastEditors  : Hejun Xie
@LastEditTime : 2020-01-03 12:15:27
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
_nc_builtins = ['__class__', '__delattr__', '__doc__', '__getattribute__', '__hash__', '__dict__',\
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
        _fhandle = nc.Dataset(fname, 'r')

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

    def get_variable(self, var_names, itime=0, get_proj_info=True, assign_heights=False, shared_heights=False, depth=-1):
        
        # Create dictionary of options
        # share height means share topograph

        depth += 1
        import_opts = {'itime':itime,\
                       'get_proj_info':get_proj_info,\
                       'shared_heights':shared_heights,\
                       'assign_heights':assign_heights,\
                       'depth':depth}
        
        if isinstance(var_names, list):
            import_opts['depth'] -= 1
            dic_var = {} # only return those wanted vars
            for i,v in enumerate(var_names):
                var = self.get_variable(v, **import_opts)
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
            print('----'*depth + '>' + var_names)
            
            # check if already read
            if var_names in self.dic_variables.keys():
                var = self.dic_variables[var_names]
                # maybe not assigned at first when computing 'Zm' and 'Zw'
                if 'z-levels' not in var.attributes and assign_heights:
                    var.assign_heights(depth=depth)
            elif var_names in DERIVED_VARS:
                var = get_derived_var(self,var_names,import_opts)
                # force the heights and topograph assignment
                if 'z-levels' in var.attributes.keys():
                    del var.attributes['z-levels'], var.attributes['topograph']
            else:
                varname_checked = self.check_varname(var_names)
                if varname_checked != '':
                    var = d.DataClass(self, varname_checked, var_names, get_proj_info=get_proj_info, itime=itime)
                else:
                    print('Variable was not found in file_instance')
                    return
            
            self.dic_variables[var_names] = var

            # Assign heights if wanted
            if 'z-levels' not in var.attributes and assign_heights and var:
                var.assign_heights(depth=depth)

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

    # [1]. Zw Zm RHO
    # Zw = file_h.get_variable('Zw', assign_heights=False)
    # Zm = file_h.get_variable('Zm', assign_heights=False)
    # RHO = file_h.get_variable('RHO', assign_heights=False)
    # print(Zw[:,0,0])
    # print(Zm[:,0,0])
    # print(RHO[:,0,0])
    
    # [2]. U V GRIDS
    # d = file_h.get_variable(['U','V','P'], assign_heights=True)
    # print(d['U'].attributes['z-levels'][0, 0, :])
    # print(d['P'].attributes['z-levels'][0, 0, :])
    # print(d['V'].attributes['z-levels'][0, :, 0])
    # print(d['P'].attributes['z-levels'][0, :, 0])

    # [3]. W GRIDS
    # d = file_h.get_variable(['W', 'P'], assign_heights=True)
    # print(d['W'].attributes['z-levels'][:, 0, 0])
    # print(d['P'].attributes['z-levels'][:, 0, 0])

    # [4]. Full test
    d = file_h.get_variable(['P', 'T', 'U', 'V', 'W', 'QR_v', 'QC_v', 'QI_v', 'QS_v', 'QG_v'], assign_heights=True)
