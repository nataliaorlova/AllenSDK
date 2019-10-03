"""
Created on Sunday July 15 2018

@author: marinag
"""

from .process_sync import filter_digital, calculate_delay  # NOQA: E402
from allensdk.brain_observatory.sync_dataset import Dataset as SyncDataset  # NOQA: E402
import numpy as np
import scipy.stats as sps

def get_sync_data(sync_file):

        sync_dataset = SyncDataset(sync_file)
        meta_data = sync_dataset.meta_data
        sample_freq = meta_data['ni_daq']['counter_output_freq']
        vs2p_f = sync_dataset.get_edges('falling', sync_dataset.TWO_PHOTON_VSYNC, units = 'samples')  # new sync may be able to do units = 'sec', so conversion can be skipped
        frames_2p = vs2p_f / sample_freq

        if 'lick_times' in meta_data['line_labels']:
             lick_times = sync_dataset.get_rising_edges('lick_1') / sample_freq  #why is this? compatibility with visual ccoding?
        else :
             lick_times = sync_dataset.get_edges('rising', sync_dataset.LICKS, units = 'samples') / sample_freq

        stim_photodiode = sync_dataset.get_edges('all', sync_dataset.PHOTODIODE_KEYS, units = 'samples') / sample_freq
        stimulus_times_no_monitor_delay = sync_dataset.get_edges('falling', sync_dataset.FRAME_KEYS, units = 'samples') / sample_freq
        trigger = sync_dataset.get_edges( 'rising', sync_dataset.ACQUISITION_TRIGGER, units = 'samples') / sample_freq
        eye_tracking = sync_dataset.get_edges('rising', sync_dataset.EYE_TRACKING_CAM_KEYS, units = 'samples') / sample_freq
        behavior_monitoring = sync_dataset.get_edges('rising', sync_dataset.BEHAVIOR_CAM_KEYS, units = 'samples') / sample_freq

        sync_data = {'ophys_frames': frames_2p,
                     'lick_times': lick_times,
                     'ophys_trigger': trigger,
                     'eye_tracking': eye_tracking,
                     'behavior_monitoring': behavior_monitoring,
                     'stim_photodiode': stim_photodiode,
                     'stimulus_times_no_delay': stimulus_times_no_monitor_delay,
                     }

        return sync_data

def get_stimulus_rebase_function(data, stimulus_timestamps_no_monitor_delay):
    
    # Time rebasing: times in stimulus_timestamps_pickle and lick log will agree with times in event log
    vsyncs = data["items"]["behavior"]['intervalsms']
    stimulus_timestamps_pickle_pre = np.hstack((0, vsyncs)).cumsum() / 1000.0

    assert len(stimulus_timestamps_pickle_pre) == len(stimulus_timestamps_no_monitor_delay)

    first_trial = data["items"]["behavior"]["trial_log"][0]
    first_trial_start_time, first_trial_start_frame = {(e[0], e[1]):(e[2], e[3]) for e in first_trial['events']}['trial_start','']
    offset_time = first_trial_start_time-stimulus_timestamps_pickle_pre[first_trial_start_frame]
    stimulus_timestamps_pickle = np.array([t+offset_time for t in stimulus_timestamps_pickle_pre])

    # Rebase used to transform trial log times to sync times:
    time_slope, time_intercept, _, _, _ = sps.linregress(stimulus_timestamps_pickle, stimulus_timestamps_no_monitor_delay)
    def rebase(t):
        return time_intercept+time_slope*t

    return rebase
