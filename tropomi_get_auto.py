from netCDF4 import Dataset
import numpy as np
import glob
import math


def get_TROPOMI(f, longitude, latitude):
    lon = f.groups['PRODUCT'].variables['longitude'][0][:]
    lat = f.groups['PRODUCT'].variables['latitude'][0][:]
    time = f.groups['PRODUCT'].variables['time_utc'][0][:]
    units = f.groups['PRODUCT'].variables['nitrogendioxide_tropospheric_column'].units
    NO2_trop = f.groups['PRODUCT'].variables['nitrogendioxide_tropospheric_column'][0][:]
    NO2_trop_err = f.groups['PRODUCT'].variables['nitrogendioxide_tropospheric_column_precision'][0][:]
    list_1 = []
    for i in range(0, len(NO2_trop)):
        for j in range(0, len(NO2_trop[0])):
            if lon[i][j] >= longitude - 0.5 and lon[i][j] <= longitude + 0.5:
                if lat[i][j] >= latitude - 0.5 and lat[i][j] <= latitude + 0.5:
                    if math.isnan(NO2_trop[i][j]) == False:
                        list_1.append((i, j))
    if len(list_1) == 0:
        print('all the qualified coincident data is NaN')
        return [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    else:

        dist = []

        for i in list_1:
            dist.append((lon[i[0]][i[1]] - longitude) ** 2 + (lat[i[0]][i[1]] - latitude) ** 2)
        for i in range(len(dist)):
            if dist[i] == min(dist):
                dist_min = list_1[i]
        lon_min = lon[dist_min[0]][dist_min[1]]
        lat_min = lat[dist_min[0]][dist_min[1]]
        NO2_col_min = NO2_trop[dist_min[0]][dist_min[1]]
        NO2_col_err_min = NO2_trop_err[dist_min[0]][dist_min[1]]
        time_min = time[dist_min[0]]
        return [lon_min, lat_min, NO2_col_min, NO2_col_err_min, units, time_min]

def get_TROPOMI_sim(f, longitude, latitude):
    lon = f.groups['PRODUCT'].variables['longitude'][0][:]
    lat = f.groups['PRODUCT'].variables['latitude'][0][:]
    time = f.groups['PRODUCT'].variables['time_utc'][0][:]
    time = np.transpose(np.tile(time, (lon.shape[1], 1)))
    NO2_trop = f.groups['PRODUCT'].variables['nitrogendioxide_tropospheric_column'][0][:]
    NO2_trop_err = f.groups['PRODUCT'].variables['nitrogendioxide_tropospheric_column_precision'][0][:]
    indx = (lon>= longitude - 0.5) & (lon <= longitude + 0.5) & (lat >= latitude - 0.5) & (lat <= latitude + 0.5)
    lon_list = lon[indx]
    lat_list = lat[indx]
    time_list = time[indx]
    no2_trop_list = NO2_trop[indx]
    no2_trop_err_list = NO2_trop_err[indx]
    if len(lon_list) == 0:
        #print('all the qualified coincident data is NaN')
        return [np.nan, np.nan, np.nan, np.nan, np.nan]
    else:
        dist = []
        for i in range(len(lon_list)):
            dist.append((lon_list[i] - longitude) ** 2 + (lat_list[i]- latitude) ** 2)
            if dist[i] == min(dist):
                dist_min = i
        lon_min = lon_list[dist_min]
        lat_min = lat_list[dist_min]
        NO2_col_min = no2_trop_list[dist_min]
        NO2_col_err_min = no2_trop_err_list[dist_min]
        time_min = time_list[dist_min]
        print('data found for {}'.format(longitude))
        return [lon_min, lat_min, NO2_col_min, NO2_col_err_min, time_min]



def read_site_info():
    site_file = open('./longitude-and-latitude.txt', 'r')
    site_names = []
    site_lons = []
    site_lats = []
    while True:
        line = site_file.readline()
        if not line:
            break
        site_names.append(line.split(',')[0])
        site_lons.append(float(line.strip().split(',')[1].split(' ')[3]))
        site_lats.append(float(line.strip().split(',')[1].split(' ')[6]))
    site_file.close()
    return site_names, site_lons, site_lats

if __name__ == '__main__':
    site_names, site_lons, site_lats = read_site_info()
    tropomi_filepath = '/Volumes/share-wrf3/TROPOMI/NO2/*.nc'
    tropomi_files = glob.glob(tropomi_filepath)
    site_datas = [None] * len(site_names)
    read_files = []
    for i in range(len(site_names)):
        site_datas[i] = []

    for file in tropomi_files:
        read_files.append(file)
        np.save('tropomi_log.npy', np.array(read_files))
        try:
            f = Dataset(file, mode='r')
            for i in range(len(site_names)):
                this_data = get_TROPOMI_sim(f, site_lons[i], site_lats[i])
                site_datas[i].append(this_data)
                this_site_save_file = './{}.npy'.format(site_names[i])
                np.save(this_site_save_file, np.array(site_datas[i]))
        except:
            print('Can not read file {}'.format(file))
