# -*- coding: utf-8 -*-

'''
@Description: a small class to handle a variable and its attributes in WRF output
@Author: Hejun Xie
@Date: 2019-12-31 16:04:11
@LastEditors  : Hejun Xie
@LastEditTime : 2020-01-01 23:42:46
'''

import numpy as np
from collections import OrderedDict
import copy
import glob, os
import datetime
import warnings

class DataClass:
    # This is just a small class that contains the content of a variable, to facilitate manipulation of data.
    def __init__(self, file='', varname='', get_proj_info=True, itime=0):
        if file != '' and varname != '':
            self.create(file, varname, get_proj_info, itime)
    
    def create(self, file, varname, get_proj_info, itime):
        self.file = file
        self.name = varname
        self.data = self.file.variables[varname][:].astype('float32')
        self.dim =  len(self.data.shape)
        self.coordinates = OrderedDict()

        # Ex: OrderedDict([(u'FieldType', 104), (u'MemoryOrder', u'XY '), (u'description', u'LATITUDE, SOUTH IS NEGATIVE'), 
        # (u'units', u'degree_north'), (u'stagger', u'')])
        self.attributes = self.file.variables[varname].__dict__
        # Ex: (u'Time', u'south_north', u'west_east') 
        self.dimensions = self.file.variables[varname].dimensions
        
        # [A]. Deal with time slice
        # Ex: 2013-10-06_00:00:00
        init_time = datetime.datetime.strptime(self.file.__dict__['START_DATE'],'%Y-%m-%d_%H:%M:%S')
        self.attributes['init_time'] = init_time
        self.attributes['step'] = self.file.variable['XTIME']
        self.attributes['step_type'] = 'minutes'
        self.get_time_slice(itime)

        if self.attributes['step_type'] == 'days':
            current_time = init_time+datetime.timedelta(days=self.attributes['step'])
        elif self.attributes['step_type'] == 'hours':
            current_time = init_time+datetime.timedelta(hours=self.attributes['step'])
        elif self.attributes['step_type'] == 'minutes':
            current_time = init_time+datetime.timedelta(minutes=self.attributes['step'])
        elif self.attributes['step_type'] == 'seconds':
            current_time = init_time+datetime.timedelta(seconds=self.attributes['step'])

        self.attributes['time']=str(current_time)
        
        # [B]. get projection information and coordinates
        dic_proj = {'TRUELAT1':self.file.__dict__['TRUELAT1'], 'TRUELAT2':self.file.__dict__['TRUELAT2'],
                    'MOAD_CENLAT':self.file.__dict__['MOAD_CENLAT'], 'STAND_LON':self.file.__dict__['STAND_LON'],
                    'CEN_LAT':self.file.__dict__['CEN_LAT'], 'CEN_LON':self.file.__dict__['CEN_LON'],
                    'DX':self.file.__dict__['DX'], 'DY':self.file.__dict__['DY']}
        
        shape = self.data.shape
        for i, dim in enumerate(self.dimensions):   
            if 'west_east' in dim:
                dic_proj['nI'] = shape[i]
            elif 'south_north' in dim:
                dic_proj['nJ'] = shape[i]
            # currently we just make the coordinates as grid index
            self.coordinates[dim]=np.arange(0,shape[i]).astype('float32')
        
        if get_proj_info:
            self.attributes['proj_info']=dic_proj

    def get_time_slice(self, itime):
        # we assume the time dimention comes first, maybe too special in some cases
        list_dimensions = list(self.dimensions)
        list_dimensions.remove('Time')
        self.dimensions = tuple(list_dimensions) # remove the time dimension
        self.data = self.data[itime, ...]
        self.step = self.step[itime]
        self.dim -= 1

    def copy(self):
        cp=DataClass()
        for attr in self.__dict__.keys():
            if attr != 'file':
                setattr(cp,attr,copy.deepcopy(getattr(self,attr)))
            else: 
                setattr(cp,attr,getattr(self,attr))                
        return cp
    
    def __str__(self):
        string='---------------------------------------------------\n'
        string+='Variable: '+self.name+', size='+str(self.data.shape)+', coords='+'('+','.join(self.coordinates.keys())+')\n'
        string+='Read from file: '+self.file.name+'\n'
        string+='Time : '+self.attributes['time']+'\n'
        string+='---------------------------------------------------\n'
        string+=str(self.data)+'\n'
        string+='---------------------------------------------------\n'
        string+='Coordinates:\n'
        for coord in self.coordinates.keys():
            string+='   '+coord+' : '+str(self.coordinates[coord].shape)+'\n'
            string+='   '+str(self.coordinates[coord])+'\n'
        string+='---------------------------------------------------\n'
        string+='Attributes:\n'
        for atr in self.attributes.keys():
            string+='   '+atr+' : "'+str(self.attributes[atr])+'"\n'
        return string

    def assign_topo(self):
        d = self.file.get_variable(['HGT'], itime=0)

        # HGT are defined on horizontal C-grid full grids
        if 'west_east_stag' in self.dimensions: # a U-like grid
            stag_topo = 0.5 * (d['HGT'].data[:,:-1] + d['HGT'].data[:,1:])
            stag_topo = np.pad(stag_topo, ((0, 0), (1, 1)), 'edge')
        elif 'south_north_stag' in self.dimensions: # a V-like grid
            stag_topo = 0.5 * (d['HGT'].data[:-1,:] + d['HGT'].data[1:,:])
            stag_topo = np.pad(stag_topo, ((1, 1), (0, 0)), 'edge')
        else:
            stag_topo = d['HGT'].data
        
        self.attributes['topograph'] = stag_topo.astype('float32')
    
    def assign_heights(self):

        if 'bottom_top_stag' in self.dimensions: # a W-like grid
            Z = self.file.get_variable(['Zw'], itime=0)['Zw'].data
        else:
            Z = self.file.get_variable(['Zm'], itime=0)['Zm'].data

        # Z-mass and Z-W are both defined on horizontal C-grid full grids

        if 'west_east_stag' in self.dimensions: # a U-like grid
            Z = 0.5 * (Z[:,:,:-1] + Z[:,:,1:])
            Z = np.pad(Z, ((0, 0), (0, 0), (1, 1)), 'edge')
        elif 'south_north_stag' in self.dimensions: # a V-like grid
            Z = 0.5 * (Z[:,:-1,:] + Z[:,1:,:])
            Z = np.pad(Z, ((0, 0), (1, 1), (0, 0)), 'edge')
        
        if Z.shape == self.data.shape:
            self.attributes['z-levels'] = Z.astype('float32')
        else:
            raise IOError('z-levels have different dimension with the variable')
        
        self.assign_topo()
        
    # Redefine operators

    # enable slice like an array
    def __getitem__(self,key):
        return self.data[key]

    def __add__(self, x):
        cp=None
        if isinstance(x,(int,float,bool,np.ndarray )): # We sum by a scalar
            cp=self.copy()
            cp.data+=x
        elif isinstance(x, DataClass): # Sum by another variable
            if self.data.shape == x.data.shape and self.coordinates.keys() == x.coordinates.keys():
                cp=self.copy()
                cp.data+=x.data

                # copy the attributes from x
                keys=self.attributes.keys()
                for att in x.attributes.keys():
                    if att not in keys:
                        cp.attributes[att]=x.attributes[att]
        return cp

    def __radd__(self, x): # Reverse addition
        cp=None
        if isinstance(x,(int,float,bool,np.ndarray )): # We sum by a scalar
            cp=self.copy()
            cp.data+=x
        elif isinstance(x, DataClass): # Sum by another variable
            if self.data.shape == x.data.shape and self.coordinates.keys() == x.coordinates.keys():
                cp=self.copy()
                cp.data+=x.data
                keys=self.attributes.keys()
                for att in x.attributes.keys():
                    if att not in keys:
                        cp.attributes[att]=x.attributes[att]
        return cp
    
    
    def __sub__(self, x):
        cp=None
        if isinstance(x,(int,float,bool,np.ndarray )): # We subtract by a scalar
            cp=self.copy()
            cp.data-=x
        elif isinstance(x, DataClass): # Substract by another variable
            if self.data.shape == x.data.shape and self.coordinates.keys() == x.coordinates.keys():
                cp=self.copy()
                cp.data-=x.data
                keys=self.attributes.keys()
                for att in x.attributes.keys():
                    if att not in keys:
                        cp.attributes[att]=x.attributes[att]
        return cp

    def __rsub__(self, x): # Reverse subtraction (non-commutative)
        cp=None
        if isinstance(x,(int,float,bool,np.ndarray )): # We subtract by a scalar
            cp=self.copy()
            cp.data=x-cp.data
        elif isinstance(x, DataClass): # Substract by another variable
            if self.data.shape == x.data.shape and self.coordinates.keys() == x.coordinates.keys():
                cp=self.copy()
                cp.data=x.data-cp.data
                keys=self.attributes.keys()
                for att in x.attributes.keys():
                    if att not in keys:
                        cp.attributes[att]=x.attributes[att]
        return cp


    def __mul__(self, x):
        cp=None
        if isinstance(x,(int,float,bool,np.ndarray )): # We muliply by a scalar
            cp=self.copy()
            cp.data*=x
        elif isinstance(x, DataClass): # Multiply by another variable
            if self.data.shape == x.data.shape and self.coordinates.keys() == x.coordinates.keys():
                cp=self.copy()
                cp.data*=x.data
                keys=self.attributes.keys()
                for att in x.attributes.keys():
                    if att not in keys:
                        cp.attributes[att]=x.attributes[att]
        return cp
        

    def __rmul__(self, x):
        cp=None
        if isinstance(x,(int,float,bool,np.ndarray )): # We muliply by a scalar
            cp=self.copy()
            cp.data*=x
        elif isinstance(x, DataClass): # Multiply by another variable
            if self.data.shape == x.data.shape and self.coordinates.keys() == x.coordinates.keys():
                cp=self.copy()
                cp.data*=x.data
                keys=self.attributes.keys()
                for att in x.attributes.keys():
                    if att not in keys:
                        cp.attributes[att]=x.attributes[att]
        return cp
        
    def __div__(self, x):
        cp=None
        if isinstance(x,(int,float,bool,np.ndarray )): # We divide by a scalar
            cp=self.copy()
            cp.data/=x
        elif isinstance(x, DataClass): # divide by another variable
            if self.data.shape == x.data.shape and self.coordinates.keys() == x.coordinates.keys():
                cp=self.copy()
                cp.data/=x.data
                keys=self.attributes.keys()
                for att in x.attributes.keys():
                    if att not in keys:
                        cp.attributes[att]=x.attributes[att]
        return cp
            
    def __rdiv__(self, x): # Reverse divsion (non-commutative)
        cp=None
        if isinstance(x,(int,float,bool,np.ndarray )): # We divide by a scalar
            cp=self.copy()
            cp.data=x/cp.data
        elif isinstance(x, DataClass): # divide by another variable
            if self.data.shape == x.data.shape and self.coordinates.keys() == x.coordinates.keys():
                cp=self.copy()
                cp.data=x.data/cp.data
                keys=self.attributes.keys()
                for att in x.attributes.keys():
                    if att not in keys:
                        cp.attributes[att]=x.attributes[att]
        return cp
            
    def __pow__(self, x):
        cp=None
        if isinstance(x,(int,float,bool,np.ndarray )): # We divide by a scalar
            cp=self.copy()
            cp.data**x
        elif isinstance(x, DataClass): # divide by another variable
            if self.data.shape == x.data.shape and self.coordinates.keys() == x.coordinates.keys():
                cp=self.copy()
                cp.data**x.data
                keys=self.attributes.keys()
                for att in x.attributes.keys():
                    if att not in keys:
                        cp.attributes[att]=x.attributes[att]
        return cp
    
    def __rpow__(self, x): # Reverse divsion (non-commutative)
        cp=None
        if isinstance(x,(int,float,bool,np.ndarray )): # We divide by a scalar
            cp=self.copy()
            cp.data=x**cp.data
        elif isinstance(x, DataClass): # divide by another variable
            if self.data.shape == x.data.shape and self.coordinates.keys() == x.coordinates.keys():
                cp=self.copy()
                cp.data=x.data**cp.data
                keys=self.attributes.keys()
                for att in x.attributes.keys():
                    if att not in keys:
                        cp.attributes[att]=x.attributes[att]
        return cp
