import os

import numpy as np
import matplotlib.pyplot as plt
import pickle
import seaborn as sns
import vdmlab as vdm

from tuning_curves_functions import get_tc, get_odd_firing_idx, linearize

import info.R063d2_info as r063d2
import info.R063d3_info as r063d3
import info.R063d4_info as r063d4
import info.R063d5_info as r063d5
import info.R063d6_info as r063d6
import info.R066d1_info as r066d1
import info.R066d2_info as r066d2
import info.R066d3_info as r066d3
import info.R066d4_info as r066d4

thisdir = os.path.dirname(os.path.realpath(__file__))

pickle_filepath = os.path.join(thisdir, 'cache', 'pickled')
output_filepath = os.path.join(thisdir, 'plots', 'sequence')

sns.set_style('white')
sns.set_style('ticks')


infos = [r063d2]
# infos = [r063d2, r063d3, r063d4, r063d5, r063d6, r066d1, r066d2, r066d3, r066d4]

for info in infos:

    for trajectory in ['u', 'shortcut']:

        print(info.session_id, trajectory)
        pos = info.get_pos(info.pxl_to_cm)
        csc = info.get_csc()
        spikes = info.get_spikes()

        tc = get_tc(info, pos, pickle_filepath)

        filename = info.session_id + '_spike_heatmaps.pkl'
        pickled_spike_heatmaps = os.path.join(pickle_filepath, filename)
        if os.path.isfile(pickled_spike_heatmaps):
            with open(pickled_spike_heatmaps, 'rb') as fileobj:
                spike_heatmaps = pickle.load(fileobj)
        else:
            spikes = info.get_spikes()

            all_neurons = list(range(1, len(spikes['time'])))
            spike_heatmaps = vdm.get_heatmaps(all_neurons, spikes, pos)
            with open(pickled_spike_heatmaps, 'wb') as fileobj:
                pickle.dump(spike_heatmaps, fileobj)

        t_start = info.task_times['prerecord'][0]
        t_stop = info.task_times['postrecord'][1]
        linear, zone = linearize(info, pos)

        # swr_times, swr_idx, filtered_butter = vdm.detect_swr_hilbert(csc, fs=info.fs)

        sort_idx = vdm.get_sort_idx(tc[trajectory])

        odd_firing_idx = get_odd_firing_idx(tc[trajectory])


        all_fields = vdm.find_fields(tc[trajectory])

        # u_compare = vdm.find_fields(tc['u'], hz_thres=3)
        # shortcut_compare = vdm.find_fields(tc['shortcut'], hz_thres=3)
        # novel_compare = vdm.find_fields(tc['novel'], hz_thres=3)
        #
        # u_fields_unique = vdm.unique_fields(all_u_fields, shortcut_compare, novel_compare)
        # shortcut_fields_unique = vdm.unique_fields(all_shortcut_fields, u_compare, novel_compare)
        # novel_fields_unique = vdm.unique_fields(all_novel_fields, u_compare, shortcut_compare)

        fields_size = vdm.sized_fields(all_fields, max_length=15)

        with_fields = vdm.get_single_field(fields_size)

        sequence = info.sequence[trajectory]
        this_linear = linear[trajectory]

        these_fields = []
        for key in with_fields:
            these_fields.append(key)

        field_spikes = []
        field_tc = []
        for idx in sort_idx:
            if idx not in odd_firing_idx:
                if idx in these_fields:
                    field_spikes.append(spikes['time'][idx])
                    field_tc.append(tc[trajectory][idx])

        for i, (start_time, stop_time, start_time_swr, stop_time_swr) in enumerate(zip(sequence['run_start'],
                                                                                       sequence['run_stop'],
                                                                                       sequence['swr_start'],
                                                                                       sequence['swr_stop'])):
            lfp_pos_y = 2
            rows = len(field_spikes) + lfp_pos_y + 1
            cols = 7

            spike_loc = lfp_pos_y + 1/rows

            fig = plt.figure()

            ax1 = plt.subplot2grid((rows, cols), (rows-lfp_pos_y, 1),  colspan=4)
            max_position = np.zeros(len(this_linear['time']))
            #         this_linear['position'] *= (1.0/np.max(this_linear['position']))
            max_position.fill(np.max(this_linear['position']))
            ax1.plot(this_linear['time'], max_position, color='#bdbdbd', lw=1)

            ax1.plot(this_linear['time'], this_linear['position'], 'k', lw=1)
            ax1.set_xlim([start_time, stop_time])
            plt.subplots_adjust(hspace=0)
            # plt.subplots_adjust(hspace=0.01)
            vdm.add_scalebar(ax1, matchy=False, loc=9)
            plt.setp(ax1, xticks=[], xticklabels=[], yticks=[])

            for ax_loc in range(0, rows-lfp_pos_y-1):
                ax = plt.subplot2grid((rows, cols), (ax_loc, 1), colspan=4, sharex=ax1)
                spike_y = (ax_loc * spike_loc + lfp_pos_y)
                ax.plot(field_spikes[ax_loc], np.ones(len(field_spikes[ax_loc]))+spike_y, '|',
                         color=sequence['colours'][ax_loc], ms=sequence['ms'], mew=1)
                ax.set_xlim([start_time, stop_time])
                plt.subplots_adjust(hspace=0)
            #     ax.axes.get_yaxis().set_visible(False)
            #     ax.axes.get_xaxis().set_visible(False)
            #     ax.axes.set_xticks([])
                plt.setp(ax, xticks=[], xticklabels=[], yticks=[])

            ax2 = plt.subplot2grid((rows, cols), (rows-lfp_pos_y, 5), colspan=2)
            ax2.plot(csc['time'], csc['data']*1000+1.25, 'k', lw=1)
            ax2.set_xlim([start_time_swr, stop_time_swr])
            # plt.subplots_adjust(hspace=0.01)
            vdm.add_scalebar(ax2, matchy=False, loc=4)
            # plt.plot(csc['time'], filtered_butter*1000+0.5, 'b', lw=1)
            plt.setp(ax2, xticks=[], xticklabels=[], yticks=[])

            for ax_loc in range(0, rows-lfp_pos_y-1):
                ax = plt.subplot2grid((rows, cols), (ax_loc, 5), colspan=2, sharex=ax2)
                spike_y = (ax_loc * spike_loc + lfp_pos_y)
                ax.plot(field_spikes[ax_loc], np.ones(len(field_spikes[ax_loc]))+spike_y, '|',
                         color=sequence['colours'][ax_loc],
                         ms=sequence['ms'], mew=1)
                ax.set_xlim([start_time_swr, stop_time_swr])
                plt.subplots_adjust(hspace=0)
                ax.axes.get_yaxis().set_visible(False)
            #     plt.setp(ax, xticks=[], xticklabels=[], yticks=[], frame_on=False)

            x = list(range(0, np.shape(field_tc)[1]))

            for ax_loc in range(0, rows-lfp_pos_y-1):
                ax = plt.subplot2grid((rows, cols), (ax_loc, 0))
                ax.plot(field_tc[ax_loc], color=sequence['colours'][ax_loc])
                ax.fill_between(x, 0, field_tc[ax_loc], facecolor=sequence['colours'][ax_loc])
                max_loc = np.where(field_tc[ax_loc] == np.max(field_tc[ax_loc]))[0][0]
                ax.text(max_loc-3, 1, str(int(np.ceil(np.max(field_tc[ax_loc])))), fontsize=8)
                ax.spines['right'].set_visible(False)
                ax.spines['top'].set_visible(False)
                plt.setp(ax, xticks=[], xticklabels=[], yticks=[])

            ax3 = plt.subplot2grid((rows, cols), (rows-lfp_pos_y+1, 1), colspan=4, sharex=ax1)
            # ax3.plot(this_linear['time'], np.zeros(len(this_linear['time'])), color='#edf8b1', lw=1)
            ax3.set_xlim([start_time, stop_time])
            plt.subplots_adjust(hspace=0)
            # vdm.add_scalebar(ax1, matchy=False, loc=1)
            plt.setp(ax3, xticks=[], xticklabels=[], yticks=[], frame_on=False)

            ax4 = plt.subplot2grid((rows, cols), (rows-lfp_pos_y+1, 5), colspan=2, sharex=ax2)
            ax4.set_xlim([start_time_swr, stop_time_swr])
            # vdm.add_scalebar(ax4, matchy=False, loc=1)
            plt.setp(ax4, xticks=[], xticklabels=[], yticks=[], frame_on=False)

            # plt.tight_layout()
            fig.subplots_adjust(hspace=0, wspace=0.1)
            sns.despine()
            plt.show()
            # filename = info.session_id + '_sequence-' + trajectory + str(i) + '.png'
            # savepath = os.path.join(output_filepath, filename)
            # plt.savefig(savepath, dpi=300, bbox_inches='tight')
            # plt.close()
