from allensdk.internal.api.behavior_ophys_api import BehaviorOphysLimsApi
from allensdk.brain_observatory.behavior.image_api import ImageApi
from allensdk.brain_observatory.behavior.sync import get_sync_data
import uuid
import matplotlib.image as mpimg
from allensdk.api.cache import memoize
import pandas as pd
import numpy as np
import logging
from allensdk.internal.api import PostgresQueryMixin
logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

class MesoscopePlaneLimsApi(BehaviorOphysLimsApi):

    def __init__(self, experiment_id, do_run=True):
        """
        Notes
        -----
        -experiment_id is the same as experiment id in lims
        -session is the session object created with MesoscopeSession class
        """
        self.experiment_id = experiment_id
        self.experiments = None #set on session's level
        self.session_id = None #this is set on session's level
        self.experiment_df = None
        self.ophys_timestamps = None #set on sessin's level
        super().__init__(experiment_id)
        if do_run:
            self.get_experiment_df()

    # def get_ophys_timestamps(self):
    #     """returns ophys timestamps for given plane"""
    #     if not self.session_id :
    #         self.get_ophys_session_id()
    #     plane_timestamps = self.session.get_plane_timestamps(self.ophys_experiment_id)
    #     self.ophys_timestamps = plane_timestamps
    #     return self.ophys_timestamps

    def get_experiment_df(self) -> pd.DataFrame:
        """experiment dataframe -
            overwrites  BehaviorOphysLimsApi.get_ophys_experiment_df"""
        api = PostgresQueryMixin()
        query = ''' 
                SELECT 
                oe.id as experiment_id, 
                os.id as session_id, 
                oe.storage_directory as experiment_folder,
                sp.name as specimen,
                os.date_of_acquisition as date,
                imaging_depths.depth as depth,
                st.acronym as structure,
                os.parent_session_id as parent_id,
                oe.workflow_state as workflow_state,
                os.stimulus_name as stimulus
                FROM ophys_experiments oe
                JOIN ophys_sessions os ON os.id = oe.ophys_session_id 
                JOIN specimens sp ON sp.id = os.specimen_id  
                JOIN imaging_depths ON imaging_depths.id = oe.imaging_depth_id 
                JOIN structures st ON st.id = oe.targeted_structure_id 
                AND oe.id='{}'
                '''
        query = query.format(self.get_ophys_experiment_id())
        self.experiment_df = pd.read_sql(query, api.get_connection())
        return self.experiment_df

    # def get_ophys_session_id(self):
    #     """ophys mesoscope experiment session ID"""
    #     return self.session.session_id

    @memoize
    def get_metadata(self) -> pd.DataFrame:
        """ophys experiment session metadata """ # this needs better definition
        metadata = super().get_metadata()
        metadata['ophys_experiment_id'] = self.get_ophys_experiment_id()
        metadata['experiment_container_id'] = self.get_experiment_container_id()
        metadata['ophys_frame_rate'] = self.get_ophys_frame_rate()
        metadata['stimulus_frame_rate'] = self.get_stimulus_frame_rate()
        metadata['targeted_structure'] = self.get_targeted_structure()
        metadata['imaging_depth'] = self.get_imaging_depth() #redefined below
        metadata['session_type'] = self.get_stimulus_name()
        metadata['experiment_datetime'] = self.get_experiment_date()
        metadata['reporter_line'] = self.get_reporter_line()
        metadata['driver_line'] = self.get_driver_line()
        metadata['LabTracks_ID'] = self.get_external_specimen_name()
        metadata['full_genotype'] = self.get_full_genotype()
        metadata['behavior_session_uuid'] = uuid.UUID(self.get_behavior_session_uuid())
        return metadata

    @memoize
    def get_imaging_depth(self) -> int:
        """lims query to retrieve imaging depth"""
        query = '''
                SELECT id.depth
                FROM ophys_experiments oe
                JOIN imaging_depths id ON id.id = oe.imaging_depth_id 
                WHERE oe.id= {};
                '''.format(self.get_ophys_experiment_id())
        return self.fetchone(query, strict=True)

    @memoize
    def get_max_projection(self, image_api=None) :
        """overwrites BehaviorOphysLimsApi.get_ophys_experiment_df as no pixel resolution is
            stored for many mesoscope experiments"""
        if image_api is None:
            image_api = ImageApi
        max_int_a13_file = self.get_max_projection_file()
        if self.get_surface_2p_pixel_size_um() == 0 :
            pixel_size = 400/512 # this should not be release. fix wiritn pixel size to paltform.json and lims, then query from lims.
        else : pixel_size = self.get_surface_2p_pixel_size_um()
        max_projection = mpimg.imread(max_int_a13_file)
        return image_api.serialize(max_projection, [pixel_size / 1000., pixel_size / 1000.], 'mm')


    @memoize
    def get_average_projection(self, image_api=None): #what are we returning here?

        if image_api is None:
            image_api = ImageApi
        avg_int_a1x_file = self.get_average_intensity_projection_image_file()
        if self.get_surface_2p_pixel_size_um() == 0 :
            pixel_size = 400/512
        else : pixel_size = self.get_surface_2p_pixel_size_um()
        average_image = mpimg.imread(avg_int_a1x_file)
        return image_api.serialize(average_image, [pixel_size / 1000., pixel_size / 1000.], 'mm')

    @memoize
    def get_segmentation_mask_image(self, image_api=None): #return type?
        if image_api is None:
            image_api = ImageApi
        segmentation_mask_image_file = self.get_segmentation_mask_image_file()
        if self.get_surface_2p_pixel_size_um() == 0 :
            pixel_size = 400/512
        else : pixel_size = self.get_surface_2p_pixel_size_um()
        segmentation_mask_image = mpimg.imread(segmentation_mask_image_file)
        return image_api.serialize(segmentation_mask_image, [pixel_size / 1000., pixel_size / 1000.], 'mm')

    def get_licks(self) -> pd.DataFrame: # here we read licks from sync, if they are absent, we read from pickle.
        sync_file = self.get_sync_file()
        lick_times = get_sync_data(sync_file)['lick_times']
        licks_df = pd.DataFrame({'time': lick_times})
        if licks_df.empty :
            behavior_stimulus_file = self.get_behavior_stimulus_file()
            data = pd.read_pickle(behavior_stimulus_file)
            lick_frames = data['items']['behavior']['lick_sensors'][0]['lick_events']
            stimulus_timestamps_no_monitor_delay = get_sync_data(sync_file)['stimulus_times_no_delay']
            lick_times  = stimulus_timestamps_no_monitor_delay[lick_frames]
            licks_df = pd.DataFrame({'time': lick_times})
        return licks_df

    @memoize
    def get_ophys_frame_rate(self):
        ophys_timestamps = self.get_ophys_timestamps()
        return np.round(1 / np.mean(np.diff(ophys_timestamps)), 0)

if __name__ == "__main__":
    test_experiment_id = 839716139
    mp = MesoscopePlaneLimsApi(test_experiment_id)
    # print(f'Experiment ID : {mp.experiment_id}')
    # print(f'Session ID: {mp.session_id}')
    # print(f'Experiment data frame:: {mp.experiment_df}')
    # print(f'Ophys Timestamps: {mp.ophys_timestamps}')
    # print(f'Imaging depth: : {mp.get_imaging_depth()}')
    # print(f'Max projection image: {mp.get_max_projection()}')
    # print(f'Segm mask image: {mp.get_segmentation_mask_image()}')
    # print(f'Licks: {mp.get_licks()}')
    # print(f'Stim presentations: {mp.get_stimulus_presentations() }')
    # print(f'Sync data: {mp.get_sync_data()}')
    # print(f'Task parameters: {mp.get_task_parameters()}')
    # print(f'DB connection: {mp.get_connection()}')
    # print(f'Targeted structure: {mp.get_targeted_structure()}')
    # print(f'stimulus_timestamps: {mp.get_stimulus_timestamps()}')
    # print(f'experiment container: {mp.get_experiment_container_id()}')
    # print(f'beh stim file: {mp.get_behavior_stimulus_file()}')
    # print(f'beh session uuid: {mp.get_behavior_session_uuid()}')
    # print(f'stim framerate: {mp.get_stimulus_frame_rate()}')
    print(f'ophys framerate: {mp.get_ophys_frame_rate()}') # to test!
    # print(f'metadata: {mp.get_metadata()}')
    #print(f'dff traces: {mp.get_dff_traces()}')
    #print(f'running data df: {mp.get_running_data_df()}') #doesn't work foe meso experiment
    #print(f'running speed: {mp.get_running_speed()}') #doesn't work for meso
    # print(f'stim templates: {mp.get_stimulus_templates()}')
    # print(f'rewards: {mp.get_rewards()}')
    # print(f'corrected fl traces: {mp.get_corrected_fluorescence_traces()}')
    # print(f'motion correction: {mp.get_motion_correction()}')
    #print(f'NWB filepath: {mp.get_nwb_filepath()}') #doesn't wokr for meso
