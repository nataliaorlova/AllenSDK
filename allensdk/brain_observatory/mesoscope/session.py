from allensdk.core.lazy_property import LazyProperty, LazyPropertyMixin
import pandas as pd
from allensdk.brain_observatory.behavior.sync import get_sync_data
from allensdk.internal.api.mesoscope_session_lims_api import MesoscopeSessionLimsApi
from allensdk.internal.api.mesoscope_plane_lims_api import MesoscopePlaneLimsApi
from allensdk.brain_observatory.mesoscope.plane import MesoscopePlane

class MesoscopeSession(LazyPropertyMixin):

    def __init__(self, do_run=True, api=None):
        self.api = api
        self.planes = {} #pd.DataFrame(columns=['plane_id', 'plane', 'ophys_timestamp'], index=range(len(self.experiments_ids['experiment_id'])))
        super().__init__()
        self.session_id = self.api.session_id
        self.session_df = LazyProperty(self.api.get_session_df)
        self.experiments_ids = LazyProperty(self.api.get_session_experiments)
        self.pairs = LazyProperty(self.api.get_paired_experiments)
        self.splitting_json =LazyProperty(self.api.get_splitting_json)
        self.folder = LazyProperty(self.api.get_session_folder)
        self.pair_num = len(self.pairs)
        self.planes_timestamps = self.split_session_timestamps()
        if do_run:
            self.make_planes()

    @classmethod
    def from_lims(cls, session_id) :
        return cls(api=MesoscopeSessionLimsApi(session_id))

    def make_planes(self) -> dict:
        for exp_id in self.experiments_ids['experiment_id']:
            pl = MesoscopePlane(api = MesoscopePlaneLimsApi(exp_id))
            pl.set_ophys_timestamps(self.planes_timestamps[exp_id])
            self.planes[exp_id]=pl
        return self.planes

    def split_session_timestamps(self) -> dict:
        '''split ophys timestamps'''
        #need to check for dropped frames: compare timestamps from sync file to SI's header timestamps
        sync_file = self.api.get_sync_file()
        timestamps = get_sync_data(sync_file)['ophys_frames']
        planes_timestamps = {} #pd.DataFrame(columns= ['plane_id', 'ophys_timestamps'], index = range(len(self.get_session_experiments())))
        pairs = self.pairs
        for pair in range(self.pair_num):
            planes_timestamps[pairs[pair][0]] = planes_timestamps[pairs[pair][1]] = timestamps[pair::len(pairs)]
        self.planes_timestamps = planes_timestamps
        return self.planes_timestamps

    def get_exp_by_structure(self, structure) -> int:
        return self.session_df.loc[self.session_df.structure == structure]

if __name__ == "__main__":
    session_id = 839208243
    ses = MesoscopeSession.from_lims(session_id)
    pd.options.display.width = 0
    print(f"Session ID: {ses.session_id}")
    print(f'Experiment in session: {ses.experiments_ids}')
    print(f'Sessions pairs: {ses.pairs}')
    print(f'Session timestamps, split: {ses.planes_timestamps}')

    # print(f"Planes : {ses.planes}") #not yer working
    # print(f'Session DataFrame: {ses.session_df}')
    # print(f'Splitting json: {ses.splitting_json}')


    #print(plane.licks)






