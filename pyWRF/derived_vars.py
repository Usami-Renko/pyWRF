# -*- coding: utf-8 -*-

'''
@Description: get derived variables from WRF original variables
@Author: Hejun Xie
@Date: 2019-12-31 16:04:27
@LastEditors  : Hejun Xie
@LastEditTime : 2019-12-31 19:13:58
'''

# WRF CONSTANTS
WRF_R_D = 287.05
WRF_R_V = 451.51
WRF_RDV = WRF_R_D / WRF_R_V
WRF_O_M_RDV = 1.0 - WRF_RDV
WRF_RVD_M_O = WRF_R_V / WRF_R_D - 1.0

DERIVED_VARS=['N', 'QV_v', 'QR_v', 'QS_v', 'QG_v', 'QC_v', 'QI_v', 'RHO']

import numpy as np

def get_derived_var(file_instance, varname, options):
    derived_var = None
    try:
        if varname == "N":
            pass
        elif varname == "QV_v":  # Water vapour mass density
            pass
        elif varname == "QR_v":  # Rain water mass density
            pass
        elif varname == "QS_v":  # Snow water mass density
            pass
        elif varname == "QG_v":  # Graupel water mass density
            pass
        elif varname == "QC_v":  # Cloud water mass density
            pass
        elif varname == "QI_v":  # Ice cloud water mass density
            pass
        elif varname == 'RHO': # AIR DENSITY
            pass
        else:
            raise ValueError('Could not compute derived variable, please specify a valid variable name')
    except:
        raise ValueError('Could not compute specified derived variable, check if all the necessary variables are in the input file_instance.')        
    return derived_var
