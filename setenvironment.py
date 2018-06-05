# -*- coding: utf-8 -*-
import sys as sys
import os as os

__author__ = 'raek'

# If repository is used to run a scheduled task and output is saved on separate paths, set this to true
operational = False

if sys.platform == 'darwin':
    root_folder = '/Users/ragnarekker/Dropbox/Kode/Python/varsomdata/'
    local_storage = root_folder + 'localstorage/'
    output_folder = root_folder + 'output/'
    plot_folder = output_folder + 'plots/'

    if operational:
        web_root_folder = '/Users/ragnarekker/Dropbox/Kode/Python/BottleSite/'
        web_pickle_folder = web_root_folder
        web_images_folder = web_root_folder + 'images/'
        web_images_regiondata_folder = web_images_folder + 'regionplots/'
        web_images_regobsdata_folder = web_images_folder + 'regobsplots/'
        web_images_observerdata_folder = web_images_folder + 'observerplots/'
        web_images_svvdata_folder = web_images_folder + 'svvplots/'
        web_view_folder = web_root_folder + 'views/'
    else:
        web_root_folder = root_folder
        web_pickle_folder = output_folder
        web_images_folder = plot_folder
        web_images_regiondata_folder = web_images_folder + 'regionplots/'
        web_images_regobsdata_folder = web_images_folder + 'regobsplots/'
        web_images_observerdata_folder = web_images_folder + 'observerplots/'
        web_images_svvdata_folder = web_images_folder + 'svvplots/'
        web_view_folder = output_folder + 'views/'

elif sys.platform == 'win32':
    root_folder = 'C:\\Users\\raek\\Dropbox\\Kode\\Python\\varsomdata\\'
    local_storage = root_folder + 'localstorage\\'
    output_folder = root_folder + 'output\\'
    plot_folder = output_folder + 'plots\\'

    if operational:
        web_root_folder = 'C:\\Users\\raek\\Dropbox\\Kode\\Python\\BottleSite\\'
        web_pickle_folder = web_root_folder
        web_images_folder = web_root_folder + 'images\\'
        web_images_regiondata_folder = web_images_folder + 'regionplots\\'
        web_images_regobsdata_folder = web_images_folder + 'regobsplots\\'
        web_images_observerdata_folder = web_images_folder + 'observerplots\\'
        web_images_svvdata_folder = web_images_folder + 'svvplots\\'
        web_view_folder = web_root_folder + 'views\\'
    else:
        web_root_folder = root_folder
        web_pickle_folder = output_folder
        web_images_folder = plot_folder
        web_images_regiondata_folder = web_images_folder + 'regionplots\\'
        web_images_regobsdata_folder = web_images_folder + 'regobsplots\\'
        web_images_observerdata_folder = web_images_folder + 'observerplots\\'
        web_images_svvdata_folder = web_images_folder + 'svvplots\\'
        web_view_folder = output_folder + 'views\\'

else:
    print("The current operating system is not supported!")

if root_folder:
    try:
        # If folders doesnt exist, make them.
        if not os.path.exists(local_storage):
            os.makedirs(local_storage)
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        if not os.path.exists(plot_folder):
            os.makedirs(plot_folder)

        if not os.path.exists(web_pickle_folder):
            os.makedirs(web_pickle_folder)
        if not os.path.exists(web_images_folder):
            os.makedirs(web_images_folder)
        if not os.path.exists(web_images_regiondata_folder):
            os.makedirs(web_images_regiondata_folder)
        if not os.path.exists(web_images_regobsdata_folder):
            os.makedirs(web_images_regobsdata_folder)
        if not os.path.exists(web_images_observerdata_folder):
            os.makedirs(web_images_observerdata_folder)
        if not os.path.exists(web_images_svvdata_folder):
            os.makedirs(web_images_svvdata_folder)
        if not os.path.exists(web_view_folder):
            os.makedirs(web_view_folder)

    except:
        error_msg = sys.exc_info()[0]
        print("setenvironment.py: Error creating folders: {}.".format(error_msg))
