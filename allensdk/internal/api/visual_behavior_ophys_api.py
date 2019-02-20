import matplotlib.image as mpimg  # NOQA: E402
import numpy as np
import pandas as pd

from allensdk.api.cache import memoize
from allensdk.internal.api.ophys_lims_api import OphysLimsApi
from allensdk.brain_observatory.visual_behavior.sync import get_sync_data

class VisualBehaviorOphysLimsApi(OphysLimsApi):

    @memoize
    def get_sync_data(self, ophys_experiment_id=None, use_acq_trigger=False):
        sync_path = self.get_sync_file(ophys_experiment_id=ophys_experiment_id)
        return get_sync_data(sync_path, use_acq_trigger=use_acq_trigger)


    @memoize
    def get_stimulus_timestamps(self, ophys_experiment_id=None, use_acq_trigger=False):
        return self.get_sync_data(ophys_experiment_id=ophys_experiment_id, use_acq_trigger=use_acq_trigger)['stimulus_frames']


    @memoize
    def get_ophys_timestamps(self, ophys_experiment_id=None, use_acq_trigger=False):
        return self.get_sync_data(ophys_experiment_id=ophys_experiment_id, use_acq_trigger=use_acq_trigger)['ophys_frames']


    @memoize
    def get_experiment_container_id(self, ophys_experiment_id=None):
        query = '''
                SELECT visual_behavior_experiment_container_id 
                FROM ophys_experiments_visual_behavior_experiment_containers 
                WHERE ophys_experiment_id= {};
                '''.format(ophys_experiment_id)        
        return self.fetchone(query, strict=False)


    @memoize
    def get_behavior_stimulus_file(self, ophys_experiment_id=None):
        query = '''
                SELECT stim.storage_directory || stim.filename AS stim_file
                FROM ophys_experiments oe
                JOIN ophys_sessions os ON oe.ophys_session_id = os.id
                JOIN behavior_sessions bs ON bs.ophys_session_id=os.id
                LEFT JOIN well_known_files stim ON stim.attachable_id=bs.id AND stim.attachable_type = 'BehaviorSession' AND stim.well_known_file_type_id IN (SELECT id FROM well_known_file_types WHERE name = 'StimulusPickle')
                WHERE oe.id= {};
                '''.format(ophys_experiment_id)
        return self.fetchone(query, strict=True)


    def get_behavior_session_uuid(self, ophys_experiment_id=None):
        behavior_stimulus_file = self.get_behavior_stimulus_file(ophys_experiment_id=ophys_experiment_id)
        data = pd.read_pickle(behavior_stimulus_file)
        return data['session_uuid']


    @memoize
    def get_metadata(self, ophys_experiment_id=None, use_acq_trigger=False):
        
        ophys_timestamps = self.get_ophys_timestamps(ophys_experiment_id=ophys_experiment_id, use_acq_trigger=use_acq_trigger)
        stimulus_timestamps = self.get_stimulus_timestamps(ophys_experiment_id=ophys_experiment_id, use_acq_trigger=use_acq_trigger)

        metadata = {}
        metadata['ophys_experiment_id'] = ophys_experiment_id
        metadata['experiment_container_id'] = self.get_experiment_container_id(ophys_experiment_id=ophys_experiment_id)
        metadata['ophys_frame_rate'] = np.round(1 / np.mean(np.diff(ophys_timestamps)), 0)
        metadata['stimulus_frame_rate'] = np.round(1 / np.mean(np.diff(stimulus_timestamps)), 0)
        metadata['targeted_structure'] = self.get_targeted_structure(ophys_experiment_id)
        metadata['imaging_depth'] = self.get_imaging_depth(ophys_experiment_id)
        metadata['session_type'] = self.get_stimulus_name(ophys_experiment_id)
        metadata['experiment_date'] = self.get_experiment_date(ophys_experiment_id)
        metadata['reporter_line'] = self.get_reporter_line(ophys_experiment_id)
        metadata['driver_line'] = self.get_driver_line(ophys_experiment_id)
        metadata['LabTracks_ID'] = self.get_LabTracks_ID(ophys_experiment_id)
        metadata['full_genotype'] = self.get_full_genotype(ophys_experiment_id)
        metadata['behavior_session_uuid'] = self.get_behavior_session_uuid(ophys_experiment_id)

        return metadata