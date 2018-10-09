# -*- coding: utf-8 -*-
__author__ = 'raek'

from varsomdata import getforecastapi as gfa
from varsomdata import makepickle as mp
import matplotlib as mpl
import pylab as plb
import setenvironment as thisenv
import setcoreenvironment as env
import numpy as np
from utilities import readfile as rf
from varsomdata import getkdvelements as gkdv
from varsomdata import getmisc as gm


def pickle_warnings(regions, date_from, date_to, pickle_file_name):
    '''All forecasted warnings and problems are selected from regObs or the avalanche api.
    Dangers and problems are connected and neatly pickel'd for later use.

    :param regions:            list [int] RegionID as given in regObs [101-199]
    :param date_from:          string as 'yyyy-mm-dd'
    :param date_to:            string as 'yyyy-mm-dd'
    :param pickle_file_name:   filename including directory as string
    :return:
    '''

    warnings = []

    for r in regions:

        # get all warning and problems for this region and then loop though them joining them where dates match.
        region_warnings = gfa.get_warnings(r, date_from, date_to)
        #name = gro.get_forecast_region_name(r)
        '''
        problems = gro.get_problems_from_AvalancheWarnProblemV(r, date_from, date_to)

        print('matrix.py -> pickle_warnings: {0} problems found for {1}'.format(len(problems), name))

        for i in range(0, len(region_warnings), 1):
            for j in range(0, len(problems), 1):
                if region_warnings[i].date == problems[j].date:
                    region_warnings[i].add_problem(problems[j])
        '''
        warnings += region_warnings

    '''
    # make sure all problems are ordered from lowest id (main problem) to largest.
    for w in warnings:
        w.avalanche_problems = sorted(w.avalanche_problems, key=lambda AvalancheProblem: AvalancheProblem.order)
    '''
    mp.pickle_anything(warnings, pickle_file_name)


def pickle_data_set(warnings, file_name, use_ikke_gitt=False):
    '''Data preperation continued. Takes the warnings which is a list of class AvalancheDanger objects and makes a dictionary
    data set of if. The value indexes relate to each other. I.e. distribution, level, probability etc.
    at the nth index originate from the same problem.

    The data set also includes information on what the xKDV tables in regObs contains and preferred colors when
    plotting.

    :param warnings:        list of AvalancheDanger objects
    :param file_name:       full path and filename to pickle the data to
    :param use_ikke_gitt:   If I dont whant to use the ID = 0 (Ikke gitt) values they can be omitted all in all.

    :return:
    '''

    level_list = []
    size_list = []
    trigger_list = []
    probability_list = []
    distribution_list = []

    for w in warnings:
        if w.danger_level > 0 and len(w.avalanche_problems) > 0:
            # The first problem in avalanche_problems is used. This is the main problem.
            level_list.append(w.danger_level)
            try:
                size_list.append(w.avalanche_problems[0].aval_size)
            except:
                size_list.append('Ikke gitt')
            trigger_list.append(w.avalanche_problems[0].aval_trigger)
            probability_list.append(w.avalanche_problems[0].aval_probability)
            distribution_list.append(w.avalanche_problems[0].aval_distribution)

        # Test is lengths match and give warning if not.
        control = (len(level_list) + len(size_list) + len(trigger_list) + len(probability_list) + len(distribution_list))/5
        if not control == len(level_list):
            print("runForMatrix -> pickle_data_set: list-lenghts dont match. Error in data.")

    level_keys = [v for v in gkdv.get_kdv('AvalancheDangerKDV').keys()]
    size_keys = [v.Name for v in gkdv.get_kdv('DestructiveSizeKDV').values()]
    triggers_keys = [v.Name for v in gkdv.get_kdv('AvalTriggerSimpleKDV').values()]
    probability_keys = [v.Name for v in gkdv.get_kdv('AvalProbabilityKDV').values()]
    distribution_keys = [v.Name for v in gkdv.get_kdv('AvalPropagationKDV').values()]

    level_colors = ['0.5','#ccff66', '#ffff00', '#ff9900', '#ff0000', 'k']

    if use_ikke_gitt == False:
        level_keys.pop(0)
        size_keys.pop(0)
        triggers_keys.pop(0)
        probability_keys.pop(0)
        distribution_keys.pop(0)

        level_colors.pop(0)

    data_set = {'level': {'values': level_list, 'keys': level_keys, 'colors':level_colors},
                'size': {'values': size_list, 'keys': size_keys, 'colors':['0.7']},
                'trigger': {'values': trigger_list, 'keys': triggers_keys, 'colors':['0.7']},
                'probability': {'values': probability_list, 'keys': probability_keys, 'colors':['0.7']},
                'distribution': {'values': distribution_list, 'keys': distribution_keys, 'colors':['0.7']}}

    mp.pickle_anything(data_set, file_name)


def plot_histogram(data_series, data_labels, file_name, data_colors=None, figure_title='', figure_text='', file_ext='.png'):
    '''Takes a data series and plots the count of each event given in data labels list.
    The plot is saved to file.

    :param title:           string
    :param data_series:     a list of values. Type of values must match elements in data labels.
    :param data_labels:     list of values. Types must match elements in the data series.
    :param filename:        String. filename including path
    :param data_colors:     list of strings. List must match data_labels in length and color for content. List of
                            length one may also be applied. Default is 'k' which gives black columns.
    :param figure_text:     String placed in textbox to the right in the middle.

    :return:
    '''

    if data_colors == None:
        data_colors = 'k' * len(data_labels)

    if figure_title == '':
        figure_title = file_name

    # Figure dimensions
    fig = plb.figure(figsize=(12, 5))
    plb.clf()
    plb.title(figure_title)

    # look up and count each occurence in the dataset
    level_distribution = []
    for dl in data_labels:
        level_distribution.append(data_series.count(dl))

    # add coordinates to a vline plot
    plb.vlines(0, 0, 0, lw=20)                # add whitespace to the left
    x = range(1, len(data_labels)+1, 1)     # odd numbering because of white spaces
    for i in x:
        plb.vlines(i, 0, data_series.count(data_labels[i-1]), lw=30, colors=data_colors[i-1])
    plb.vlines(i+1, 0, 0, lw=20)              # add whitespace to the right

    x_ticks = data_labels
    plb.xticks(x, x_ticks)

    if figure_text != '':
        plb.text(len(data_labels)*0.8, len(data_series)*0.35, figure_text, bbox=dict(facecolor='0.9', alpha=0.9))

    # This saves the figure til file
    plb.savefig(file_name+file_ext)
    plb.close(fig)


def plot_histogram_on_danger_level(key, data_set, file_name, normalized=False, figure_title='', file_ext='.png'):
    """Messy but generic for its use. Plots a histogram on the requested data series for each danger level.

    :param key:             which series in data_set is to be plotted.
    :param data_set:        a data set as made in the method pickle_data_set in thins file.
    :param file_name:       String. filename including path.
    :param normalized:      Bool. The values pr key_value are normalized for better visualizatioin. Default False.
    :param figure_title:    String. If not specified it becomes same as filename
    :param file_ext:        String. Default extencion is png if no other extencion is specified.

    :return:
    """

    if figure_title == '':
        figure_title = file_name


    data_keys = data_set[key]['keys']
    data_values = data_set[key]['values']

    level_keys = data_set['level']['keys']
    level_values = data_set['level']['values']
    level_colors =  data_set['level']['colors']

    if normalized:
        figure_title = figure_title + "(normalized)"
        file_name = file_name + "_norm"
        # Get danger level distribution used for normalizing
        level_distribution = []
        for dl in level_keys:
            level_distribution.append(level_values.count(dl))


    # this list is expanded as it loops trough the for loops below. Index given by [level_keys]
    numbers = []
    for i in range(0, len(data_values), 1):
        for j in range(0, len(level_keys), 1):
            numbers.append([])
            if level_values[i] == level_keys[j]:
                # collect all data events on the danger level they occur
                numbers[j].append(data_values[i])


    # this nested list is indexed [level_keys][data_keys]. I is expanded as it loops trough the for loops below.
    more_numbers = []
    for i in range(0, len(level_keys), 1):
        more_numbers.append([])
        for j in range(0, len(data_keys), 1):
            # count occurrences of data pr danger level
            if normalized and level_distribution[i] > 0:
                more_numbers[i].append([numbers[i].count(data_keys[j]) / float(level_distribution[i]),
                                       level_colors[i]]) # normalizing by danger level
            else:
                more_numbers[i].append([numbers[i].count(data_keys[j]), level_colors[i]])

    # Figure dimensions
    fig = plb.figure(figsize=(20, 10))
    plb.clf()
    plb.title(figure_title)

    # prepare data set for plotting
    plot_numbers = [[0,'0']]                            # give som space from the y-axis. Add an empty item.
    for i in range(0, len(data_keys), 1):
        for j in range(0, len(level_keys), 1):
            plot_numbers.append(more_numbers[j][i])

    # add coordinates to a vline plot
    x = range(0, len(data_keys)*len(level_keys)+1, 1)   # +1 because of the empty item in plot_numbers
    for i in x:
        plb.vlines(i, 0, plot_numbers[i][0], lw=25, color=plot_numbers[i][1])

    # Dynamic location of labels
    ticks_place = []
    ticks_place.append(3)
    for dk in data_keys:
        if ticks_place[-1] <= len(x):
            ticks_place.append(ticks_place[-1]+len(level_keys))

    plb.xticks(ticks_place, data_keys)

    # This saves the figure to file
    plb.savefig(file_name+file_ext)
    plb.close(fig)

    return


def plot_histogram_on_given_problem(problem_combo , warnings, file_name, figure_title='', file_ext=".png"):
    '''
    Plots histogram of occurences pr dangerlevel for a given avalanche problem (combination of distribution,
    probability, size and trigger). This method uses the more genereic plot_histogram function.

    :param problem_combo:   dictionary of {distribution : value, probability : value, size : value, trigger : value}
    :param warnings:        list of all warnings in selected timespan
    :param file_name:       String. filename including path.
    :param figure_title:    String. If not specified it becomes same as filename
    :param file_ext:        String. Default extencion is png if no other extencion is specified.

    :return:
    '''

    if figure_title == '':
        figure_title = file_name

    # loop trough warnings and look up problems matching the problem_combo. Plot the result.
    level_list = []

    for w in warnings:
        if w.danger_level > 0 and len(w.avalanche_problems) > 0:
            p = w.avalanche_problems[0]
            if (p.aval_distribution == problem_combo['distribution'] and
                    p.aval_probability == problem_combo['probability'] and
                    p.aval_size == problem_combo['size'] and
                    p.aval_trigger == problem_combo['trigger']):
                level_list.append(w.danger_level)

    level_keys = gkdv.get_kdv('AvalancheDangerKDV').keys()
    level_colors = ['0.5','#ccff66', '#ffff00', '#ff9900', '#ff0000', 'k']

    fig_text = 'Plottet viser tilfeller pr faregrad av \n' \
               'skredproblemer med egenskaper: \n' \
               '{2}, {3}, {4} og\n' \
               '{5}. \n \n' \
               'Denne kombinasjonen har vaert brukt\n' \
               '{0} ganger i totalt {1} produserte\n' \
               'varsel. Utvalget henter bare fra \n' \
               'hovedskredproblemer.' \
        .format(len(level_list), len(warnings),
                problem_combo['distribution'], problem_combo['probability'], problem_combo['size'] ,problem_combo['trigger'])

    plot_histogram(level_list, level_keys, file_name, data_colors=level_colors, figure_title=figure_title, figure_text=fig_text, file_ext=file_ext)

    return


def plot_all_histograms(data_set, date_from, date_to, warnings):
    """

    :return:
    """

    plot_folder = thisenv.plot_folder

    plot_histogram(data_set['level']['values'], data_set['level']['keys'],
                '{0}Histogram of levels {1} to {2}'.format(plot_folder, date_from, date_to), figure_title='frequency of levels')
    plot_histogram(data_set['size']['values'], data_set['size']['keys'],
                '{0}Histogram of sizes {1} to {2}'.format(plot_folder, date_from, date_to), figure_title='frequency of sizes')
    plot_histogram(data_set['trigger']['values'], data_set['trigger']['keys'],
                '{0}Histogram of triggers {1} to {2}'.format(plot_folder, date_from, date_to), figure_title='frequency of triggers')
    plot_histogram(data_set['probability']['values'], data_set['probability']['keys'],
                '{0}Histogram of probabilities {1} to {2}'.format(plot_folder, date_from, date_to), figure_title='frequency of probabilities')
    plot_histogram(data_set['distribution']['values'], data_set['distribution']['keys'],
                '{0}Histogram of distribution {1} to {2}'.format(plot_folder, date_from, date_to), figure_title='frequency of distribution')

    plot_histogram_on_danger_level('size', data_set,
                '{0}Histogram of size on danger level {1} to {2}'.format(plot_folder, date_from, date_to))
    plot_histogram_on_danger_level('trigger', data_set,
                '{0}Histogram of triggers on danger level {1} to {2}'.format(plot_folder, date_from, date_to))
    plot_histogram_on_danger_level('probability', data_set,
                '{0}Histogram of probabilities on danger level {1} to {2}'.format(plot_folder, date_from, date_to))
    plot_histogram_on_danger_level('distribution', data_set,
                '{0}Histogram of distribution on danger level {1} to {2}'.format(plot_folder, date_from, date_to))

    plot_histogram_on_danger_level('size', data_set,
                '{0}Histogram of size on danger level {1} to {2}'.format(plot_folder, date_from, date_to), normalized=True)
    plot_histogram_on_danger_level('trigger', data_set,
                '{0}Histogram of triggers on danger level {1} to {2}'.format(plot_folder, date_from, date_to), normalized=True)
    plot_histogram_on_danger_level('probability', data_set,
                '{0}Histogram of probabilities on danger level {1} to {2}'.format(plot_folder, date_from, date_to), normalized=True)
    plot_histogram_on_danger_level('distribution', data_set,
                '{0}Histogram of distribution on danger level {1} to {2}'.format(plot_folder, date_from, date_to), normalized=True)

    problem_combo = {
        'size': '2 - Smaa',
        'trigger': 'Liten tilleggsbelastning',
        'probability': 'Mulig',
        'distribution': 'Noen bratte heng'}

    plot_histogram_on_given_problem(problem_combo, warnings,
                                    '{0}Histogram on {3}-{4}-{5}-{6} {1} to {2}'
                                        .format(plot_folder, date_from, date_to, problem_combo['distribution'],
                                                problem_combo['probability'], problem_combo['size'][0], problem_combo['trigger']),
                                    figure_title='Faregrader pr skredproblem ({0} til {1})'.format(date_from, date_to))


class M3Element:

    def __init__(self):

        self.danger_level_list = []         # list of int
        self.danger_level_average = None    # float
        self.danger_level_standard_dev = None   # float
        self.occurrences = None            # int

        self.avalanche_size = None          # string
        self.trigger = None                 # string
        self.probability = None             # string
        self.distribution = None            # string

        self.x = None                       # x coordinate for plotting
        self.y = None                       # y coordinate for plotting

        self.label_size = None              # string
        self.label_trigger = None           # string
        self.label_probalility = None       # string
        self.label_distribution = None      # string

        self.colour = 'white'               # string, should always be overwritten.
        self.recomended_danger_level = None  # int
        self.recomended_colour = 'white'    # string, should always be overwritten.

    def add_configuration_row(self, row):
        """
        E.g.:
        avalanche_size;trigger;probability;distribution;x;y;label_size;label_trigger;label_probalility;label_distribution
        1 - Harmloest;Stor tilleggsbelastning, Liten tilleggsbelastning;Lite sannsynlig;Isolerte faresoner;100;100;1;HT;unlikely;isolated slopes

        :param row:
        :return:
        """

        self.avalanche_size = row[0]          # []
        self.trigger = row[1]                 # []
        self.probability = row[2]             # []
        self.distribution = row[3]            # []

        self.x = row[4]                       # x coordinate for plotting
        self.y = row[5]                       # y coordinate for plotting

        self.label_size = row[6]              # string
        self.label_trigger = row[7]           # string
        self.label_probalility = row[8]       # string
        self.label_distribution = row[9]      # string

        self.colour = row[10]                 # string

        if len(row) > 11:
            if row[11] != '':
                self.recomended_danger_level = int(row[11])  # int
            else:
                self.recomended_danger_level = 0
        else:
            self.recomended_danger_level = 0  # int
        self.set_recomended_colour()

    def add_danger_level(self, level):
        self.danger_level_list.append(level)
        self.occurrences = len(self.danger_level_list)


    def set_level_average(self):
        if not len(self.danger_level_list) == 0:
            self.danger_level_average = 1.*sum(self.danger_level_list)/len(self.danger_level_list)
            self.set_colour()


    def set_level_standard_dev(self):
        if not len(self.danger_level_list) == 0:
            list = np.array(self.danger_level_list)
            self.danger_level_standard_dev = np.std(list, axis=0)


    def set_colour(self):
        if self.occurrences is not None:
            if round(self.danger_level_average) == 1:
                self.colour = '#ccff66'
            elif round(self.danger_level_average) == 2:
                self.colour = '#ffff00'
            elif round(self.danger_level_average) == 3:
                self.colour = '#ff9900'
            elif round(self.danger_level_average) == 4:
                self.colour = '#ff0000'
            elif round(self.danger_level_average) == 5:
                self.colour = 'k'
            else:
                self.colour = 'pink'        # pink means something whent wrong


    def set_recomended_colour(self):
        if self.recomended_danger_level == 0:
            self.recomended_colour = 'gray'
        elif self.recomended_danger_level == 1:
            self.recomended_colour = '#ccff66'
        elif self.recomended_danger_level == 2:
            self.recomended_colour = '#ffff00'
        elif self.recomended_danger_level == 3:
            self.recomended_colour = '#ff9900'
        elif self.recomended_danger_level == 4:
            self.recomended_colour = '#ff0000'
        elif self.recomended_danger_level == 5:
            self.recomended_colour = 'k'
        else:
            self.recomended_colour = 'pink' # pink means something whent wrong


def pickle_M3(data_set, config_file_name, pickle_m3_file_name):
    """Makes a list of elements matching the m3 matrix. Uses a configuration file as for the matrix elements and
     runs through all warnings adding occurances and danger level used at each combination of the matrix.

    :param data_set:
    :param pickle_m3_file_name:
    :return:
    """

    config_file_name = '{0}{1}'.format(env.input_folder, config_file_name)
    m3_elements = rf.read_configuration_file(config_file_name, M3Element)

    # read out the data_set and add to M3Elements
    for i in range(0, len(data_set['level']['values']), 1):

        size = data_set['size']['values'][i]
        if size is None:
            size = '0 - Ikke gitt'
            print('matrix.py -> picke_M3 -> Warning: Encountered occurrence where avalanche size is None. Set to 0 - Ikke gitt.')
        trigger = data_set['trigger']['values'][i]
        probability = data_set['probability']['values'][i]
        distribution = data_set['distribution']['values'][i]

        for e in m3_elements:

            m3_size = e.avalanche_size
            m3_trigger = e.trigger
            m3_probability = e.probability
            m3_distribution = e.distribution

            if size.strip() in m3_size and trigger.strip() in m3_trigger and probability.strip() in m3_probability and distribution.strip() in m3_distribution:
                level = data_set['level']['values'][i]
                e.add_danger_level(level)

    # count all levels added (for debug only) for control and make some stats
    count = 0
    for e in m3_elements:
        count += len(e.danger_level_list)
        e.set_level_average()
        e.set_level_standard_dev()

    mp.pickle_anything(m3_elements, pickle_m3_file_name)


def plot_m3(m3_elements, plot_m3_file_name, file_ext=".png"):
    """
    M3:
    https://docs.google.com/spreadsheets/d/1HwYqMt5MSctqdbY92MbipAjnv_FJUPBvVYp5HBC_2HU/edit#gid=0

    Plot-control
    http://miscellaneousprogtips.blogspot.no/2012/02/get-more-control-over-your.html?m=1


    """
    short_list = []
    for e in m3_elements:
        if e.occurrences is not None:
            short_list.append(e)

    # Figure dimensions
    fsize = (20, 9)
    fig = plb.figure(figsize=fsize)
    #plb.clf()
    ax = fig.add_subplot(111)
    plb.subplots_adjust(top=0.9, bottom=0.15, left=0.02, right=0.98)

    strange_elements = []
    box_size = 100

    # grid and axis labels
    for i in range(0,1800,200):
            plb.vlines(i, 0, 600, lw=1, color='0.8')
            plb.vlines(i+100, 0, 550, lw=1, color='0.8')
            plb.text(i+45, 520, 'HT')
            plb.text(i+145, 520, 'NT')

    for i in range(0,600,100):
        plb.hlines(i, -100, 1800, lw=1, color='0.8')

    plb.text(500, 690, 'Probabiltiy of triggering (distribution + probability at certain trigger)')

    plb.text(200, 620, 'isolated/extreme slopes')
    plb.text(800, 620, 'some steep slopes')
    plb.text(1400, 620, 'many / most(?) steep slopes')

    for i in range(0, 1800, 600):
        plb.text(i+50, 570, 'unlikely(?)')
        plb.text(i+250, 570, 'possible')
        plb.text(i+450, 570, 'expected')

    for i in range(1,6,1):
        plb.text(-50, i*100-50, '{0}'.format(i))

    for e in m3_elements:
        if not e.x == '0' and not e.y == '0':
            x = int(e.x)-box_size
            y = int(e.y)-box_size
            rect = mpl.patches.Rectangle((x, y), box_size , box_size, facecolor=e.colour)
            ax.add_patch(rect)

            if e.occurrences is not None:
                plb.text(x+10, y+35, 'n={0}\n m={1}\n  sd={2}'.format(e.occurrences, round(e.danger_level_average,1) , round(e.danger_level_standard_dev,2)))

                # small histograms
                n = e.occurrences
                n1 = e.danger_level_list.count(1)
                rect_1 = mpl.patches.Rectangle((x+7+box_size/6*0, y+3), box_size/6, box_size/4*n1/n, facecolor='k', edgecolor="none")
                ax.add_patch(rect_1)
                n2 = e.danger_level_list.count(2)
                rect_2 = mpl.patches.Rectangle((x+7+box_size/6*1, y+3), box_size/6, box_size/4*n2/n, facecolor='k', edgecolor="none")
                ax.add_patch(rect_2)
                n3 = e.danger_level_list.count(3)
                rect_3 = mpl.patches.Rectangle((x+7+box_size/6*2, y+3), box_size/6, box_size/4*n3/n, facecolor='k', edgecolor="none")
                ax.add_patch(rect_3)
                n4 = e.danger_level_list.count(4)
                rect_4 = mpl.patches.Rectangle((x+7+box_size/6*3, y+3), box_size/6, box_size/4*n4/n, facecolor='k', edgecolor="none")
                ax.add_patch(rect_4)
                n5 = e.danger_level_list.count(5)
                rect_5 = mpl.patches.Rectangle((x+7+box_size/6*4, y+3), box_size/6, box_size/4*n5/n, facecolor='k', edgecolor="none")
                ax.add_patch(rect_5)
        else:
            # if elements are given coordinates 0 they are an illegal combination. Append them to this list for debug purposes
            strange_elements.append(e)

    plb.hlines(0, -100, 1800, lw=2, color='k')
    plb.hlines(500, -100, 1800, lw=2, color='k')
    plb.hlines(600, 0, 1800, lw=2, color='k')

    plb.vlines(0, 0, 650, lw=2, color='k')
    plb.vlines(600, 0, 650, lw=2, color='k')
    plb.vlines(1200, 0, 650, lw=2, color='k')
    plb.vlines(1800, 0, 650, lw=2, color='k')

    plb.xlim(-100, 1810)
    plb.ylim(-10, 700)
    plb.axis('off')
    plb.savefig(plot_m3_file_name+file_ext)
    plb.close()

    a = 1


def plot_m3_v2(m3_elements, plot_file_name, file_ext=".png"):

  # Figure dimensions
    fsize = (24, 9)
    fig = plb.figure(figsize=fsize)
    #plb.clf()
    ax = fig.add_subplot(111)
    plb.subplots_adjust(top=0.9, bottom=0.15, left=0.02, right=0.98)

    strange_elements = []
    box_size = 100

    # Grid and axis lables

    for i in range(0,2400,300):
        plb.text(i+45, 520, 'High')
        plb.vlines(i+100, 0, 550, lw=1, color='0.8')
        plb.text(i+145, 520, 'Low')
        plb.vlines(i+200, 0, 550, lw=1, color='0.8')
        plb.text(i+245, 520, 'Nat')
        plb.vlines(i, 0, 600, lw=1, color='0.8')

    for i in range(0, 2400, 600):
        plb.text(i+100, 570, 'Possible')
        plb.text(i+400, 570, 'Likely')
        plb.vlines(i, 0, 650, lw=1, color='0.8')

    plb.text(250, 620, 'Isolated', fontsize=20)
    plb.text(850, 620, 'Some', fontsize=20)
    plb.text(1450, 620, 'Many', fontsize=20)
    plb.text(2050, 620, 'Most', fontsize=20)

    plb.text(750, 690, 'Probability of triggering (stability, likelyhood and distribution)', fontsize=20)

    for e in m3_elements:
        if not e.x == '0' and not e.y == '0':
            x = int(e.x)-box_size
            y = int(e.y)-box_size
            rect = mpl.patches.Rectangle((x, y), box_size , box_size, facecolor=e.colour)
            ax.add_patch(rect)

            circ = mpl.patches.Circle((x+box_size*0.85, y+box_size*0.85), box_size/11, facecolor=e.recomended_colour, edgecolor='k')
            ax.add_patch(circ)

            if e.occurrences is not None:
                plb.text(x+10, y+50, 'n={0}\n m={1}'.format(e.occurrences, round(e.danger_level_average,1)))

                # small histograms
                n = e.occurrences
                n1 = e.danger_level_list.count(1)
                rect_1 = mpl.patches.Rectangle((x+7+box_size/6*0, y+3), box_size/6, box_size/3*n1/n, facecolor='k', edgecolor="none")
                ax.add_patch(rect_1)
                n2 = e.danger_level_list.count(2)
                rect_2 = mpl.patches.Rectangle((x+7+box_size/6*1, y+3), box_size/6, box_size/3*n2/n, facecolor='k', edgecolor="none")
                ax.add_patch(rect_2)
                n3 = e.danger_level_list.count(3)
                rect_3 = mpl.patches.Rectangle((x+7+box_size/6*2, y+3), box_size/6, box_size/3*n3/n, facecolor='k', edgecolor="none")
                ax.add_patch(rect_3)
                n4 = e.danger_level_list.count(4)
                rect_4 = mpl.patches.Rectangle((x+7+box_size/6*3, y+3), box_size/6, box_size/3*n4/n, facecolor='k', edgecolor="none")
                ax.add_patch(rect_4)
                n5 = e.danger_level_list.count(5)
                rect_5 = mpl.patches.Rectangle((x+7+box_size/6*4, y+3), box_size/6, box_size/3*n5/n, facecolor='k', edgecolor="none")
                ax.add_patch(rect_5)

        else:
            # if elements are given coordinates 0 they are an illegal combination. Append them to this list for debug purposes
            strange_elements.append(e)

    # more labels and grid
    plb.text(-100, 330, 'Avalanche size', fontsize=20, rotation=90)

    for i in range(1,6,1):
        plb.text(-40, i*100-50, '{0}'.format(i), fontsize=15)
        plb.hlines(i*100, -50, 2400, lw=1, color='0.8')


    plb.hlines(0, -100, 2400, lw=2, color='k')
    plb.hlines(500, -100, 2400, lw=2, color='k')
    plb.hlines(600, 0, 2400, lw=2, color='k')

    plb.vlines(0, 0, 650, lw=2, color='k')
    plb.vlines(600, 0, 650, lw=2, color='k')
    plb.vlines(1200, 0, 650, lw=2, color='k')
    plb.vlines(1800, 0, 650, lw=2, color='k')
    plb.vlines(2400, 0, 650, lw=2, color='k')

    plb.xlim(-100, 2410)
    plb.ylim(-10, 700)
    plb.axis('off')
    plb.savefig(plot_file_name+file_ext)
    plb.close()

    return


if __name__ == "__main__":

    regions = gm.get_forecast_regions(year='2016-17')
    date_from = "2016-12-01"
    date_to = "2017-06-01"
    pickle_warnings_file_name = '{0}{1}'.format(thisenv.local_storage, 'runForMatrix warnings.pickle')
    pickle_data_set_file_name = '{0}{1}'.format(thisenv.local_storage, 'runForMatrix data set.pickle')

    pickle_m3_file_name = '{0}{1}'.format(thisenv.local_storage, 'runForMatix m3.pickle')
    plot_m3_file_name = '{0}m3 {1}-{2}'.format(thisenv.plot_folder, date_from[0:4], date_to[2:4])

    pickle_m3_v2_file_name = '{0}{1}'.format(thisenv.local_storage, 'runForMatix m3.v2.pickle')
    plot_m3_v2_file_name = '{0}m3 {1}-{2}.v2'.format(thisenv.plot_folder, date_from[0:4], date_to[2:4])


    ######################################################################################
    ####### With something pickled you don't need to read on the api all the time ########
    #
    pickle_warnings(regions, date_from, date_to, pickle_warnings_file_name)
    warnings = mp.unpickle_anything(pickle_warnings_file_name)
    pickle_data_set(warnings, pickle_data_set_file_name, use_ikke_gitt=False)
    data_set = mp.unpickle_anything(pickle_data_set_file_name)
    #
    ######################################################################################


    # plot_all_histograms(data_set, date_from, date_to, warnings)

    # pickle_M3(data_set, 'matrixconfiguration.csv', pickle_m3_file_name)
    # m3_elements = mp.unpickle_anything(pickle_m3_file_name)
    # plot_m3(m3_elements, plot_m3_file_name, file_ext=".png")

    pickle_M3(data_set, 'matrixconfiguration.v2.csv', pickle_m3_v2_file_name)
    m3_v2_elements = mp.unpickle_anything(pickle_m3_v2_file_name)
    plot_m3_v2(m3_v2_elements, plot_m3_v2_file_name)


    a = 1

