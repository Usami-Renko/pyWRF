# -*- coding: utf-8 -*-

'''
@Description: a small class to handle a variable and its attributes in WRF output
@Author: Hejun Xie
@Date: 2019-12-31 16:04:11
@LastEditors  : Hejun Xie
@LastEditTime : 2019-12-31 19:30:58
'''

import numpy as np
from collections import OrderedDict
import copy
import glob, os
import datetime
import warnings

class DataClass:
    # This is just a small class that contains the content of a variable, to facilitate manipulation of data.
    def __init__(self, file='', varname='', get_proj_info=True):
        if file != '' and varname != '':
            self.create(file, varname, get_proj_info)
    
    def create(self, file, varname, get_proj_info):
        pass

    def copy(self):
        pass

    
    # Redefine operators

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
    
    def __str__(self):
        pass

    def assign_heights(self):
        pass
