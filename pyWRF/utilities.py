# -*- coding: utf-8 -*-

'''
@Description: 
@Author: Hejun Xie
@Date: 2019-12-31 16:04:57
@LastEditors: Hejun Xie
@LastEditTime: 2020-07-16 16:54:54
'''

import sys
import numpy as np
import pyproj

def WGS_to_WRF(coords_WGS, proj_info):
    # convert from tuple to np.ndarrray
    if isinstance(coords_WGS, tuple):
        coords_WGS=np.vstack(coords_WGS)
    # check if input is an array
    if isinstance(coords_WGS, np.ndarray):
        if coords_WGS.shape[0]<coords_WGS.shape[1]:
            coords_WGS=coords_WGS.T
        lon = coords_WGS[:,1]
        lat = coords_WGS[:,0]
        input_is_array=True
    else:
        lon=coords_WGS[1]
        lat=coords_WGS[0]
        input_is_array=False
    
    wrf_proj = pyproj.Proj(proj='lcc', # projection type: Lambert Conformal Conic
                       lat_1=proj_info['TRUELAT1'], lat_2=proj_info['TRUELAT2'], # Cone intersects with the sphere
                       lat_0=proj_info['MOAD_CEN_LAT'], lon_0=proj_info['STAND_LON'], # Center point
                       a=6370000, b=6370000) # This is it! The Earth is a perfect sphere

    # Easting and Northings of the domains center point
    wgs_proj = pyproj.Proj(proj='latlong', datum='WGS84')

    python_version = sys.version_info

    # python3 or python2
    if sys.version_info[0] >= 3:
        transformer = pyproj.Transformer.from_proj(wgs_proj, wrf_proj)

    if sys.version_info[0] >= 3:
        cen_lambert_x, cen_lambert_y = transformer.transform(proj_info['CEN_LON'], proj_info['CEN_LAT'])
    else:
        cen_lambert_x, cen_lambert_y = pyproj.transform(wgs_proj, wrf_proj, proj_info['CEN_LON'], proj_info['CEN_LAT'])

    nx, ny = proj_info['nI'], proj_info['nJ']
    dx, dy = proj_info['DX'], proj_info['DY']

    if sys.version_info[0] >= 3:
        proj_lambert_x, proj_lambert_y = transformer.transform(lon, lat)
    else:
        proj_lambert_x, proj_lambert_y = pyproj.transform(wgs_proj, wrf_proj, lon, lat)

    x = proj_lambert_x - (cen_lambert_x - dx * (nx - 1) / 2.)
    y = proj_lambert_y - (cen_lambert_y - dy * (ny - 1) / 2.)

    index_x, index_y = x / dx, y / dy

    if input_is_array:
        coords_WRF = np.vstack((index_x, index_y)).T
    else:
        coords_WRF = np.asarray([index_x, index_y])
    
    return coords_WRF.astype('float32')

if __name__ == "__main__":
    # unit test
    dic_proj = {'TRUELAT1':30., 'TRUELAT2':60.,
                'MOAD_CEN_LAT':30., 'STAND_LON':125.,
                'CEN_LAT':28.8117, 'CEN_LON':123.2079,
                'DX':3000., 'DY':3000.,
                'nI':360, 'nJ':222}
    
    coords_WGS = np.array([[25.610306, 118.02133], [31.735355, 128.86807]])

    coords_WRF = WGS_to_WRF(coords_WGS, dic_proj)

    print(coords_WRF)
