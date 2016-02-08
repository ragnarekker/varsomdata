# -*- coding: utf-8 -*-
__author__ = 'raek'

import fencoding as fe
import getdangers as gd
import getobservations as go
import getkdvelements as gkdv
import setenvironment as env
import datetime as dt
import readfile as rf
import makepickle as mp
import matplotlib as mpl
import pylab as plb


if __name__ == "__main__":

    # region_id = [112, 117, 116, 128]

    ## Get all regions
    region_id = []
    ForecastRegionKDV = gkdv.get_kdv('ForecastRegionKDV')
    for k, v in ForecastRegionKDV.iteritems():
        if 99 < k < 150 and v.IsActive is True:
            region_id.append(v.ID)

    from_date = dt.date(2014, 11, 30)
    to_date = dt.date(2015, 6, 1)
    #to_date = dt.date.today()

    pickle_file_name_1 = '{0}runlevelanddangersign part 1.pickle'.format(env.local_storage)
    pickle_file_name_2 = '{0}runlevelanddangersign part 2.pickle'.format(env.local_storage)

    all_danger_levels = gd.get_all_dangers(region_id, from_date, to_date)
    all_danger_signs = go.get_danger_sign(from_date, to_date, region_ids=region_id, geohazard_tid=10)
    mp.pickle_anything([all_danger_levels, all_danger_signs], pickle_file_name_1)

    all_danger_levels, all_danger_signs = mp.unpickle_anything(pickle_file_name_1)

    # for counting days with danger levels
    level_count = []
    data = {1:[], 2:[], 3:[], 4:[], 5:[]}
    for dl in all_danger_levels:
        if dl.source == 'Varsel' and dl.danger_level is not 0:
            level_count.append(dl.danger_level)
            for ds in all_danger_signs:
                if dl.date == ds.DtObsTime.date() and dl.region_name in ds.ForecastRegionName:
                    print '{0}'.format(dl.date)
                    data[dl.danger_level].append(fe.remove_norwegian_letters(ds.DangerSignName))
    mp.pickle_anything([data, level_count], pickle_file_name_2)

    data, level_count = mp.unpickle_anything(pickle_file_name_2)

    # pick out a list of danger signs
    DangerSignKDV = gkdv.get_kdv('DangerSignKDV')
    danger_signs = []
    for k, v in DangerSignKDV.iteritems():
        if 0 < k < 100 and v.IsActive is True:
            danger_signs.append(v.Name)

    # change order in danger signs
    a = danger_signs[8]
    danger_signs.insert(5, a)
    b = danger_signs[9]
    danger_signs.pop(9)

    fg_1 = []
    fg_2 = []
    fg_3 = []
    fg_4 = []
    fg_5 = []

    for k,v in data.iteritems():
        for ds in danger_signs:
            if k is 1: fg_1.append(v.count(ds))
            if k is 2: fg_2.append(v.count(ds))
            if k is 3: fg_3.append(v.count(ds))
            if k is 4: fg_4.append(v.count(ds))
            if k is 5: fg_5.append(v.count(ds))

    plot_data = [fg_1, fg_2, fg_3, fg_4, fg_5]

    fg_1_norm = [n / float(max(1,sum(fg_1))) for n in fg_1]
    fg_2_norm = [n / float(max(1,sum(fg_2))) for n in fg_2]
    fg_3_norm = [n / float(max(1,sum(fg_3))) for n in fg_3]
    fg_4_norm = [n / float(max(1,sum(fg_4))) for n in fg_4]
    fg_5_norm = [n / float(max(1,sum(fg_5))) for n in fg_5]

    plot_data_norm = [fg_1_norm, fg_2_norm, fg_3_norm, fg_4_norm, fg_5_norm]

    plot_legend = danger_signs
    plot_labels = ['1 Litern', '2 Moderat', '3 Betydlig', '4 Stor', '5 Meget stor']

    plot_data_norm_sum = []
    for fg in plot_data_norm:
        fg_sum = []
        last_sum = 0
        for d in fg:
            fg_sum.append(last_sum + d)
            last_sum = last_sum + d
        plot_data_norm_sum.append(fg_sum)

    plot_colors = ['#008000',   # ingen faretegn observert
                   '#0000cc',   # ferske skred
                   '#0000ff',   # drønn i snøen
                   '#3333ff',   # ferske sprekker
                   '#6666ff',   # stort snøfall
                   '#ccccff',   # Fersk vindtransportert snø
                   '#336699',   # Rimkrystaller
                   '#ff3333',   # Rask temperaturstigning
                   '#ff6666',   # Mye vann i snøen
                   '#777777']   # Annet

   # Figure dimensions
    fsize = (15, 15)
    fig = plb.figure(figsize=fsize)
    #plb.clf()
    ax = fig.add_subplot(111)
    plb.subplots_adjust(top=0.95, bottom=0.15, left=0.02, right=0.98)

    for j in range(0, len(plot_data_norm_sum), 1 ):
        fg = plot_data_norm_sum[j]
        last_coordinate = 0
        for i in range(0, len(fg), 1):
            plb.vlines(j*100+100, last_coordinate, fg[i], lw = 145, colors=plot_colors[i])
            last_coordinate = fg[i]

    # legend, botom left corner
    legend_x = 510
    legend_y = 0.50
    box_size_x = 20
    box_size_y = 0.03

    for i in range(0, len(danger_signs), 1):
        rect = mpl.patches.Rectangle((legend_x, legend_y + i * 0.05), box_size_x , box_size_y, facecolor=plot_colors[i], edgecolor="none")
        ax.add_patch(rect)
        plb.text(legend_x + 40, legend_y + i * 0.05 + 0.005, '{0}'.format(danger_signs[i]))

    # top and botom lables
    for i in range(1, 5, 1):
        plb.text(100*i-42, 1.08, 'Faretegn = {0}'.format( sum(plot_data[i-1]) ))
        plb.text(100*i-42, 1.04, 'Dager varslet = {0}'.format(level_count.count(i)))
        plb.text(100*i-20, -0.04, '{0}'.format(plot_labels[i-1]))

    # title
    plb.text(50, 1.165, 'Faretegn fordelt paa varselt faregrad vintern 2014-15', fontsize=30)

    plb.xlim(0, 700)
    plb.ylim(-0.05, 1.25)
    plb.axis('off')

    file_name = 'Danger level and danger sign 2014-15.png'
    plb.savefig("{0}{1}".format(env.plot_folder, file_name))

