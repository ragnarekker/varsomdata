#! /usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'raek'

'''Setup work environment

@var data_folder:   Folder where all data files are stored. These are csv's as output or pickles for local storage.
@var
@var
@var

'''

import sys


if sys.platform == 'darwin':

    root_folder = '/Users/ragnarekker/Documents/github/varsomdata/varsomdata/'
    data_folder = root_folder + 'datafiles/'
    plot_folder = root_folder + 'plots/'
    kdv_elements_folder = root_folder + 'localstorage/'
    input_folder = root_folder + 'input/'
    local_storage = root_folder + 'localstorage/'
    output_folder = root_folder + 'output/'

    web_root_folder = '/Users/ragnarekker/Documents/github/BottleSite/'
    web_images_folder = web_root_folder + 'images/'
    web_view_folder = web_root_folder + 'views/'

    
elif sys.platform == 'win32':

    root_folder = 'C:\\Users\\raek\\github\\varsomdata\\varsomdata\\'
    data_folder = root_folder + 'datafiles\\'
    plot_folder = root_folder + 'plots\\'
    kdv_elements_folder = root_folder + 'localstorage\\'
    input_folder = root_folder + 'input\\'
    local_storage = root_folder + 'localstorage\\'
    output_folder = root_folder + 'output\\'

    web_root_folder = 'C:\\Users\\raek\\github\\BottleSite\\'
    web_images_folder = web_root_folder + 'images\\'
    web_view_folder = web_root_folder + 'views\\'

    
else:
    print "The current operating system is not supported!"


api_version = "v1.0.1"
old_api_version = "v0.9.9"
registration_basestring = 'http://www.regobs.no/Registration/'
log = []
