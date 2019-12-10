from allensdk.core.lazy_property import LazyProperty, LazyPropertyMixin
import pandas as pd
from allensdk.internal.api.mesoscope_session_lims_api import MesoscopeSessionLimsApi
from allensdk.internal.api.mesoscope_plane_lims_api import MesoscopePlaneLimsApi
from allensdk.brain_observatory.mesoscope.plane import MesoscopePlane

class MesoscopeSession(LazyPropertyMixin):

    def __init__(self, do_run=False, api=None):
        self.api = api
        self.planes = {} #pd.DataFrame(columns=['plane_id', 'plane', 'ophys_timestamp'], index=range(len(self.experiments_ids['experiment_id'])))
        super().__init__()
        self.session_id = LazyProperty(self.api.session_id)
        self.session_df = LazyProperty(self.api.get_session_df)
        self.experiments_ids = self.api.get_session_experiments()
        self.pairs = self.api.get_paired_experiments()
        self.splitting_json =LazyProperty(self.api.get_splitting_json)
        self.folder = LazyProperty(self.api.get_session_folder)
        self.planes_timestamps = {}
        self.pair_num = len(self.pairs)
        if do_run:
            self.split_session_timestamps()
            self.make_planes()


    @classmethod
    def from_lims(cls, session_id) :
        return cls(api=MesoscopeSessionLimsApi(session_id))

    def make_planes(self) -> list:
        for exp_id in self.experiments_ids['experiment_id']:
            pl = MesoscopePlane(api = MesoscopePlaneLimsApi(exp_id))
            pl.ophys_timestamps = self.planes_timestamps[self.planes_timestamps.plane_id == exp_id].reset_index().loc[0, 'ophys_timestamps']
            self.planes[exp_id]=pl
        return self.planes

    def split_session_timestamps(self) -> dict:
        '''split ophys timestamps'''
        #need to check for dropped frames: compare timestamps from sync file to SI's header timestamps
        sync_file = self.api.get_sync_file()
        timestamps = self.api.get_sync_data(sync_file)['ophys_frames']
        planes_timestamps = {} #pd.DataFrame(columns= ['plane_id', 'ophys_timestamps'], index = range(len(self.get_session_experiments())))
        pairs = self.pairs
        for pair in range(self.pair_num):
            planes_timestamps[pairs[pair][0]] = planes_timestamps[pairs[pair][1]] = timestamps[pair::len(pairs)]
        self.planes_timestamps = planes_timestamps
        return self.planes_timestamps

    def get_exp_by_structure(self, structure) -> int:
        return self.session_df.loc[self.session_df.structure == structure]

if __name__ == "__main__":
    session_id = 992393325
    ses = MesoscopeSession.from_lims(session_id)
    pd.options.display.width = 0
    print(f"planes : {ses.planes}")
    print(f'Session ID: {ses.session_id}')
    print(f'Session DataFrame: {ses.session_df}')
    print(f'Session .session_df)
    #plane = planes[planes.plane_id == 807310592].plane.values[0]
    #print(plane.licks)






