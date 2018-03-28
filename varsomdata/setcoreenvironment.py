# -*- coding: utf-8 -*-
import sys as sys
import os as os

__author__ = 'ragnarekker'

if sys.platform == 'darwin':
    root_folder = '/Users/ragnarekker/Dropbox/Kode/Python/varsomdata/varsomdata/'
    kdv_elements_folder = root_folder + 'localstorage/'
    input_folder = root_folder + 'input/'
    forecast_region_shapes = root_folder + 'input/forecastregionshapes/'
    local_storage = root_folder + 'localstorage/'
    log_folder = root_folder + 'logs/'

elif sys.platform == 'win32':
    root_folder = 'C:\\Users\\raek\\Dropbox\\Kode\\Python\\varsomdata\\varsomdata\\'
    kdv_elements_folder = root_folder + 'localstorage\\'
    input_folder = root_folder + 'input\\'
    forecast_region_shapes = root_folder + 'input\\forecastregionshapes\\'
    local_storage = root_folder + 'localstorage\\'
    log_folder = root_folder + 'logs\\'

else:
    print("The current operating system is not supported!")
    root_folder = None

if root_folder:
    try:
        # If log folder doesnt exist, make it.
        if not os.path.exists(kdv_elements_folder):
            os.makedirs(kdv_elements_folder)
        if not os.path.exists(input_folder):
            os.makedirs(input_folder)
        if not os.path.exists(forecast_region_shapes):
            os.makedirs(forecast_region_shapes)
        if not os.path.exists(local_storage):
            os.makedirs(local_storage)
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)

    except:
        error_msg = sys.exc_info()[0]
        print("setcoreenvironment.py: Error creating folders: {}.".format(error_msg))

odata_version = 'v3.2.0'
web_api_version = 'v3.2.0'
forecast_api_version = 'v3.0.0'
registration_basestring = 'http://www.regobs.no/Registration/'
