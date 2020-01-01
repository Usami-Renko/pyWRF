# -*- coding: utf-8 -*-

'''
@Description: get derived variables from WRF original variables
@Author: Hejun Xie
@Date: 2019-12-31 16:04:27
@LastEditors  : Hejun Xie
@LastEditTime : 2020-01-01 23:34:34
'''

# WRF CONSTANTS
WRF_R_D = 287.05
WRF_R_V = 451.51
WRF_RDV = WRF_R_D / WRF_R_V
WRF_O_M_RDV = 1.0 - WRF_RDV
WRF_RVD_M_O = WRF_R_V / WRF_R_D - 1.0
WRF_G = 9.81

DERIVED_VARS=['N', 'QV_v', 'QR_v', 'QS_v', 'QG_v', 'QC_v', 'QI_v', 'RHO', 'Pw', 'P', 'T', 'Zw', 'Zm']

import numpy as np

def get_derived_var(file_instance, varname, options):
    derived_var = None
    try:
        if varname == "N":
            d = file_instance.get_variable(['T','Pw','P'],**options)
            derived_var=(77.6/d['T'])*(0.01*d['P']+4810*(0.01*d['Pw'])/d['T'])
            derived_var.attributes['long_name']='Refractivity'
            derived_var.attributes['units']='-'
        elif varname == "QV_v":  # Water vapour mass density
            d = file_instance.get_variable(['QV','RHO'],**options)
            derived_var = d['QV']*d['RHO']
            derived_var.name = 'QV_v'
            derived_var.attributes['units'] = 'kg/m3'
            derived_var.attributes['long_name'] = 'Water vapor mass density'
        elif varname == "QR_v":  # Rain water mass density
            d = file_instance.get_variable(['QR','RHO'],**options)
            derived_var = d['QR']*d['RHO']
            derived_var.name='QR_v'
            derived_var.attributes['units']='kg/m3'
            derived_var.attributes['long_name']='Rain mass density'
        elif varname == "QS_v":  # Snow water mass density
            d = file_instance.get_variable(['QS','RHO'],**options)
            derived_var=d['QS']*d['RHO']
            derived_var.name='QS_v'
            derived_var.attributes['units']='kg/m3'
            derived_var.attributes['long_name']='Snow mass density'
        elif varname == "QG_v":  # Graupel water mass density
            d = file_instance.get_variable(['QG','RHO'],**options)
            derived_var=d['QG']*d['RHO']
            derived_var.name='QG_v'
            derived_var.attributes['units']='kg/m3'
            derived_var.attributes['long_name']='Graupel mass density'
        elif varname == "QC_v":  # Cloud water mass density
            d = file_instance.get_variable(['QC','RHO'],**options)
            derived_var=d['QC']*d['RHO']
            derived_var.name='QC_v'
            derived_var.attributes['units']='kg/m3'
            derived_var.attributes['long_name']='Cloud mass density'
        elif varname == "QI_v":  # Ice cloud water mass density
            d = file_instance.get_variable(['QI','RHO'],**options)
            derived_var=d['QI']*d['RHO']
            derived_var.name='QI_v'
            derived_var.attributes['units']='kg/m3'
            derived_var.attributes['long_name']='Ice crystals mass density'
        elif varname == 'RHO': # AIR DENSITY
            d = file_instance.get_variable(['P','T','QV','QR','QC','QI','QS'],**options)
            derived_var=d['P']/(d['T']*WRF_R_D*((d['QV']*WRF_RVD_M_O\
            -d['QR']-d['QC']-d['QI']-d['QS'])+1.0))
            derived_var.name='RHO'
            derived_var.attributes['long_name']='Air density'
            derived_var.attributes['units']='kg/m3'
        elif varname == 'Pw': # Vapor pressure
            d = file_instance.get_variable(['P','QV'],**options)
            derived_var=(d['P']*d['QV'])/(d['QV']*(1-0.6357)+0.6357)
            derived_var.attributes['long_name']='Vapor pressure'
            derived_var.attributes['units']='Pa'
        elif varname == 'P':
            d = file_instance.get_variable(['Pp', 'PB'], **options)
            derived_var=(d['P']+d['PB'])
            derived_var.attributes['long_name']='Pressure'
            derived_var.attributes['units']='Pa'
        elif varname == 'T':
            d = file_instance.get_variable(['Thetap', 'T00', 'P', 'P00'], **options)
            derived_var=(d['Thetap']+d['T00'].data)*(d['P']/d['P00'].data)**0.2857
            derived_var.attributes['long_name']='Temperature'
            derived_var.attributes['units']='K'
        elif varname == 'Zw':
            d = file_instance.get_variable(['PHB', 'PH'], **options)
            derived_var=(d['PHB']+d['PH'])/WRF_G
            derived_var.attributes['long_name']='Height on velocity(full) levels'
            derived_var.attributes['units']='m'
        elif varname == 'Zm':
            # Note that on eta coordinates, the half level always divide the full level in half
            # there is an aproximation that the height on half level is the geometric average of the neighbouring two full levels
            # isothermal layer approximation
            d = file_instance.get_variable(['Zw'], **options)
            derived_var=(d['Zw'][:-1]*d['Zw'][1:])**0.5/WRF_G
            derived_var.attributes['long_name']='Height on mass(half) levels'
            derived_var.attributes['units']='m'
        else:
            raise ValueError('Could not compute derived variable, please specify a valid variable name')
    except:
        raise ValueError('Could not compute specified derived variable, check if all the necessary variables are in the input file_instance.')        
    return derived_var
