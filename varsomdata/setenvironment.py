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


if sys.platform == 'linux2' or sys.platform == 'darwin':
    data_folder = 'datafiles/'
    plot_folder = 'plots/'
    kdv_elements_folder = 'localstorage/'
    input_folder = 'input/'
    local_storage = 'localstorage/'
    output_folder = 'output/'

    
elif sys.platform == 'win32':
    data_folder = 'datafiles\\'
    plot_folder = 'plots\\'
    kdv_elements_folder = 'localstorage\\'
    input_folder = 'input\\'
    local_storage = 'localstorage\\'
    output_folder = 'output\\'

    
else:
    print "The current operating system is not supported!"


api_version = "v0.9.9"
registration_basestring = 'http://www.regobs.no/Registration/'
log = []
