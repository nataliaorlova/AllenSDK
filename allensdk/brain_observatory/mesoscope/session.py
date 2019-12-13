from allensdk.core.lazy_property import LazyProperty, LazyPropertyMixin
import pandas as pd
from allensdk.brain_observatory.behavior.sync import get_sync_data
from allensdk.internal.api.mesoscope_session_lims_api import MesoscopeSessionLimsApi
from allensdk.internal.api.mesoscope_plane_lims_api import MesoscopePlaneLimsApi
from allensdk.brain_observatory.mesoscope.plane import MesoscopePlane
import numpy as np

class MesoscopeSession(LazyPropertyMixin):

    def __init__(self, do_run=True, api=None):
        super().__init__()
        self.api = api
        self.planes = {}
        self.session_ophys_timestamps = None
        self.plane_ophys_framerate = None
        self.planes_timestamps = {}
        self.session_id = self.api.session_id
        self.session_df = LazyProperty(self.api.get_session_df)
        self.experiments_ids = LazyProperty(self.api.get_session_experiments)
        self.pairs = LazyProperty(self.api.get_paired_experiments)
        self.splitting_json =LazyProperty(self.api.get_splitting_json)
        self.folder = LazyProperty(self.api.get_session_folder)
        self.pair_num = len(self.pairs)
        if do_run:
            self.get_session_timestamps()
            self.split_session_timestamps()
            self.make_ophys_framerate()
            self.make_planes()

    @classmethod
    def from_lims(cls, session_id) :
        """
        instantiate a MesoscopeSession object
        :param session_id:
        :return: MesoscopeSession
        """
        return cls(api=MesoscopeSessionLimsApi(session_id))

    def make_planes(self) :
        """
        Create a Mesoscope palne object for each experiment in session identified by their experiment ids
        :return: dict[int: allensdk.brain_observatory.mesoscope.plane.MesoscopePlane]
        """
        for exp_id in self.experiments_ids['experiment_id']:
            pl = MesoscopePlane(api = MesoscopePlaneLimsApi(exp_id))
            pl.set_ophys_timestamps(self.planes_timestamps[exp_id])
            pl.session_id = self.session_id
            pl.set_ophys_framerate(self.plane_ophys_framerate)
            self.planes[exp_id]=pl
        return

    def get_session_timestamps(self):
        sync_file = self.api.get_sync_file()
        self.session_ophys_timestamps = get_sync_data(sync_file)['ophys_frames']
        return self.session_ophys_timestamps

    def split_session_timestamps(self) :
        """
        split sessions timestamps for individual experiments
        :return: dict[int : [float]]
        """
        #need to check for dropped frames: compare timestamps from sync file to SI's header timestamps

        planes_timestamps = {}
        for pair in range(self.pair_num):
            planes_timestamps[self.pairs[pair][0]] = planes_timestamps[self.pairs[pair][1]] = self.session_ophys_timestamps[pair::self.pair_num]
        self.planes_timestamps = planes_timestamps
        return

    def make_ophys_framerate(self)  -> np.float64:
        """
        calculates ophys framerate based on number of planes and sync data
        :return: numpy.float64
        """
        self.plane_ophys_framerate = 1/np.mean(np.diff(self.session_ophys_timestamps))/self.pair_num
        return self.plane_ophys_framerate

    def get_exp_by_structure(self, structure) -> int:
        """
        Retrieve experiment names for given targeted structure
        :param structure: str : the name of targeted structure, can be:
        VISp
        VISam
        VISl
        VISpm
        VISpl
        VISli
        VISpor
        VISm
        VISa
        VISal
        :return: experiment ID for given targeted structure
            list[int]
        """
        return self.session_df.loc[self.session_df.structure == structure]

if __name__ == "__main__":
    session_id = 839208243
    ses = MesoscopeSession.from_lims(session_id)
    pd.options.display.width = 0
    print(f"Session ID: {ses.session_id}")
    print(f'Experiment in session: {ses.experiments_ids}')
    print(f'Number of pairs: {ses.pair_num}')
    print(f'Sessions pairs: {ses.pairs}')
    print(f'Session timestamps, split: {ses.planes_timestamps}')
    print(f'Planes : {ses.planes}')
    # print('')







