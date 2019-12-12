from allensdk.brain_observatory.behavior.behavior_ophys_session import BehaviorOphysSession
from allensdk.internal.api.mesoscope_plane_lims_api import MesoscopePlaneLimsApi
import pandas as pd

class MesoscopePlane(BehaviorOphysSession):

    @classmethod
    def from_lims(cls, experiment_id):
        return cls(api=MesoscopePlaneLimsApi(experiment_id))

    def __init__(self, api=None):
        super().__init__()
        self.api = api


    @property
    def experiment_df(self) -> int:
        """Information about this experiment.
        :rtype: pandas.DataFrame
        """
        return self.api.get_experiment_df()

    @property
    def metadata(self) -> pd.DataFrame:
        """
        Metadata about this experiment
        :return: pandas.DataFrame
        """
        return self.api.get_metadata()

    @property
    def imaging_depth(self) -> int:
        """
        call to the api method that queries imaging depth
        :return: int
        """
        return self.api.get_imaging_depth()

    @property
    def max_projection(self):
        """
        redefining to use MesoscopePLaneAPI
        returns max porjection image (np.array)
        :return: numpy.array
        """
        return self.api.get_max_projection()

    @property
    def average_projection(self):
        """
        redefining to use MesoScopePlaneAPI
        returns average projection image (2D numpy.array)
        :return: numpy.array
        """
        return self.api.get_average_projection()

    @property
    def segmentation_mask_image(self):
        """
        redefined to use MesoscopePlaneAPI
        returns segmentation mask image (2D numpy.array)
        :return: numpy.array
        """
        return self.api.get_segmentation_mask_image()

    @property
    def licks(self):
        """
        redefined to use MesoscopePlaneAPI
        get licks from sync, if not present - read from pickle
        :return: pandas.DataFrame
        """
        return self.api.get_licks()

    def ophys_timestamps(self):
        return None

    def set_ophys_timestamps(self, value):
        self.ophys_timestamps = value
        return

    def ophys_framerate(self):
        return None

    def set_ophys_framerate(self, value):
        self.ophys_framerate = value
        return

if __name__ == "__main__":
    test_experiment_id = 839716139
    mp = MesoscopePlane.from_lims(test_experiment_id)
    print(f'Experiment ID: {mp.ophys_experiment_id}')
    print(f'Metadata: {mp.metadata}')
    print(f'Experiment DF: {mp.experiment_df}')
    print(f'Imaging depth: {mp.imaging_depth}')
    print(f'Max projection image: {mp.max_projection}')
    print(f'Average projection image : {mp.average_projection}')
    print(f'Segmentation mask image: {mp.segmentation_mask_image}')
    print(f'Licks: {mp.licks}')




