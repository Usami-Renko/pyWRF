# -*- coding: utf-8 -*-

'''
@Description: 
@Author: Hejun Xie
@Date: 2020-01-02 16:29:13
@LastEditors  : Hejun Xie
@LastEditTime : 2020-01-02 16:30:32
'''

import pyWRF as pw
file_h = pw.open_file('../../cosmo_pol/pathos/WRF/wsm6/wrfout_d03_2013-10-06_00_00_00')

# [1]. Zw Zm RHO
Zw = file_h.get_variable('Zw', assign_heights=False)
Zm = file_h.get_variable('Zm', assign_heights=False)
RHO = file_h.get_variable('RHO', assign_heights=False)
print(Zw[:,0,0])
print(Zm[:,0,0])
print(RHO[:,0,0])

# [2]. U V GRIDS
d = file_h.get_variable(['U','V','P'], assign_heights=True)
print(d['U'].attributes['z-levels'][0, 0, :])
print(d['P'].attributes['z-levels'][0, 0, :])
print(d['V'].attributes['z-levels'][0, :, 0])
print(d['P'].attributes['z-levels'][0, :, 0])

# [3]. W GRIDS
d = file_h.get_variable(['W', 'P'], assign_heights=True)
print(d['W'].attributes['z-levels'][:, 0, 0])
print(d['P'].attributes['z-levels'][:, 0, 0])

# [4]. Full test
d = file_h.get_variable(['P', 'T', 'U', 'V', 'W', 'QR_v', 'QC_v', 'QI_v', 'QS_v', 'QG_v'], assign_heights=True)