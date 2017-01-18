import matplotlib
matplotlib.use('agg')

import pytest
import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from allensdk.core.brain_observatory_nwb_data_set import BrainObservatoryNwbDataSet
import allensdk.brain_observatory.observatory_plots as oplots
from allensdk.brain_observatory.static_gratings import StaticGratings
from allensdk.brain_observatory.drifting_gratings import DriftingGratings
from allensdk.brain_observatory.natural_scenes import NaturalScenes
from allensdk.brain_observatory.natural_movie import NaturalMovie
from allensdk.brain_observatory.locally_sparse_noise import LocallySparseNoise
import allensdk.brain_observatory.stimulus_info as stiminfo
import allensdk.core.json_utilities as ju
from pkg_resources import resource_filename  # @UnresolvedImport

if 'TEST_OBSERVATORY_EXPERIMENT_PLOTS_DATA' in os.environ:
    data_file = os.environ['TEST_OBSERVATORY_EXPERIMENT_PLOTS_DATA']
else:
    data_file = resource_filename(__name__, 'test_observatory_plots_data.json')

EXPERIMENT_CONTAINER = ju.read(data_file)
TEST_DATA_DIR = EXPERIMENT_CONTAINER['image_directory']

class AnalysisSingleton(object):
    def __init__(self, klass, session, *args):
        self.klass = klass
        self.session = session
        self.args = args

        self.obj = None

    @staticmethod
    def experiment_for_session(session):
        return next(exp for exp in EXPERIMENT_CONTAINER['experiments'] if exp['session'] == session)

    def __call__(self):
        if self.obj is None:
            exp = self.experiment_for_session(self.session)
            data_set = BrainObservatoryNwbDataSet(exp['nwb_file'])
            self.obj = self.klass.from_analysis_file(data_set, exp['analysis_file'], *self.args)

        return self.obj

STATIC_GRATINGS = AnalysisSingleton(StaticGratings, stiminfo.THREE_SESSION_B)
DRIFTING_GRATINGS = AnalysisSingleton(DriftingGratings, stiminfo.THREE_SESSION_A)
NATURAL_SCENES = AnalysisSingleton(NaturalScenes, stiminfo.THREE_SESSION_B)
NATURAL_MOVIE_ONE_A = AnalysisSingleton(NaturalMovie, stiminfo.THREE_SESSION_A, stiminfo.NATURAL_MOVIE_ONE)
NATURAL_MOVIE_ONE_B = AnalysisSingleton(NaturalMovie, stiminfo.THREE_SESSION_B, stiminfo.NATURAL_MOVIE_ONE)
NATURAL_MOVIE_ONE_C = AnalysisSingleton(NaturalMovie, stiminfo.THREE_SESSION_C, stiminfo.NATURAL_MOVIE_ONE)
NATURAL_MOVIE_TWO = AnalysisSingleton(NaturalMovie, stiminfo.THREE_SESSION_C, stiminfo.NATURAL_MOVIE_TWO)
NATURAL_MOVIE_THREE = AnalysisSingleton(NaturalMovie, stiminfo.THREE_SESSION_A, stiminfo.NATURAL_MOVIE_THREE)
LOCALLY_SPARSE_NOISE = AnalysisSingleton(LocallySparseNoise, stiminfo.THREE_SESSION_C, stiminfo.LOCALLY_SPARSE_NOISE)
CELL_SPECIMEN_ID = EXPERIMENT_CONTAINER['cells'][0]

def assert_images_match(new_file, test_file, shape):
    assert os.path.exists(new_file)
    new_img = mpimg.imread(new_file)
    assert np.allclose(new_img.shape[:2], shape)
    
    assert os.path.exists(test_file)
    test_img = mpimg.imread(test_file)
    assert np.allclose(new_img.shape, test_img.shape)
    assert np.allclose(test_img.shape[:2], shape)

    assert (new_img - test_img).mean() < 0.1
    
    os.remove(new_file)

@pytest.mark.parametrize("new_file,static_gratings", 
                         [ [ 'static_gratings_ttp.png', STATIC_GRATINGS ] ])
def test_ttp_static_gratings(new_file, static_gratings, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        static_gratings().plot_time_to_peak()
        oplots.finalize_with_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,static_gratings", 
                         [ [ 'static_gratings_pref_ori.png', STATIC_GRATINGS ] ])
def test_pref_ori_static_gratings(new_file, static_gratings, shape=[250,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        static_gratings().plot_preferred_orientation()
        oplots.finalize_no_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,static_gratings", 
                         [ [ 'static_gratings_ori.png', STATIC_GRATINGS ] ])
def test_osi_static_gratings(new_file, static_gratings, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        static_gratings().plot_orientation_selectivity()
        oplots.finalize_with_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,static_gratings", 
                         [ [ 'static_gratings_pref_sf.png', STATIC_GRATINGS ] ])
def test_pref_sf(new_file, static_gratings, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        static_gratings().plot_preferred_spatial_frequency()
        oplots.finalize_with_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,drifting_gratings", 
                         [ [ 'drifting_gratings_pref_dir.png', DRIFTING_GRATINGS ] ])
def test_pref_dir_drifting_gratings(new_file, drifting_gratings, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        drifting_gratings().plot_preferred_direction()
        oplots.finalize_no_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,drifting_gratings", 
                         [ [ 'drifting_gratings_pref_tf.png', DRIFTING_GRATINGS ] ])
def test_pref_tf_drifting_gratings(new_file, drifting_gratings, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        drifting_gratings().plot_preferred_temporal_frequency()
        oplots.finalize_with_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,drifting_gratings", 
                         [ [ 'drifting_gratings_dsi.png', DRIFTING_GRATINGS ] ])
def test_dsi_drifting_gratings(new_file, drifting_gratings, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        drifting_gratings().plot_direction_selectivity()
        oplots.finalize_with_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,drifting_gratings", 
                         [ [ 'drifting_gratings_osi.png', DRIFTING_GRATINGS ] ])
def test_osi_drifting_gratings(new_file, drifting_gratings, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        drifting_gratings().plot_orientation_selectivity()
        oplots.finalize_with_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,natural_scenes", 
                         [ [ 'natural_scenes_ttp.png', NATURAL_SCENES ] ])
def test_ttp_natural_scenes(new_file, natural_scenes, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        natural_scenes().plot_time_to_peak()
        oplots.finalize_with_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,static_gratings,cell_specimen_id",
                         [ [ 'static_gratings_fan_plot.png', STATIC_GRATINGS, CELL_SPECIMEN_ID ] ])
def test_fan_plot(new_file, static_gratings, cell_specimen_id, shape=[250,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        static_gratings().open_fan_plot(cell_specimen_id)
        oplots.finalize_no_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,natural_scenes,cell_specimen_id", 
                         [ [ 'natural_scenes_fan_plot.png', NATURAL_SCENES, CELL_SPECIMEN_ID ] ])
def test_corona_plot(new_file, natural_scenes, cell_specimen_id, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        natural_scenes().open_corona_plot(cell_specimen_id)
        oplots.finalize_no_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,natural_movie,cell_specimen_id", 
                         [ ("natural_movie_one_a_track_plot.png", NATURAL_MOVIE_ONE_A, CELL_SPECIMEN_ID),
                           ("natural_movie_one_b_track_plot.png", NATURAL_MOVIE_ONE_B, CELL_SPECIMEN_ID),
                           ("natural_movie_one_c_track_plot.png", NATURAL_MOVIE_ONE_C, CELL_SPECIMEN_ID),
                           ("natural_movie_two_track_plot.png", NATURAL_MOVIE_TWO, CELL_SPECIMEN_ID),
                           ("natural_movie_three_track_plot.png", NATURAL_MOVIE_THREE, CELL_SPECIMEN_ID) ])
def test_track_plot(new_file, natural_movie, cell_specimen_id, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        natural_movie().open_track_plot(cell_specimen_id)
        oplots.finalize_no_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,drifting_gratings,cell_specimen_id", 
                         [ [ 'drifting_gratings_star_plot.png', DRIFTING_GRATINGS, CELL_SPECIMEN_ID ] ])
def test_star_plot(new_file, drifting_gratings, cell_specimen_id, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        drifting_gratings().open_star_plot(cell_specimen_id)
        oplots.finalize_no_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,analysis,cell_specimen_id", 
                         [ ("3sa_speed_tuning_plot.png", DRIFTING_GRATINGS, CELL_SPECIMEN_ID),
                           ("3sb_speed_tuning_plot.png", STATIC_GRATINGS, CELL_SPECIMEN_ID),
                           ("3sc_speed_tuning_plot.png", NATURAL_MOVIE_TWO, CELL_SPECIMEN_ID) ])
def test_speed_tuning_plot(new_file, analysis, cell_specimen_id, shape=[500,500]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        analysis().plot_speed_tuning(cell_specimen_id)
        oplots.finalize_with_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)

@pytest.mark.parametrize("new_file,locally_sparse_noise,on,cell_specimen_id", 
                         [ ('locally_sparse_noise_on.png', LOCALLY_SPARSE_NOISE, True, CELL_SPECIMEN_ID),
                           ('locally_sparse_noise_off.png', LOCALLY_SPARSE_NOISE, False, CELL_SPECIMEN_ID) ])
def test_pincushion_plot(new_file, locally_sparse_noise, on, cell_specimen_id, shape=[500,877]):
    with oplots.figure_in_px(shape[1], shape[0], new_file) as fig:
        locally_sparse_noise().open_pincushion_plot(cell_specimen_id, on=on)
        oplots.finalize_no_axes()
    assert_images_match(new_file, os.path.join(TEST_DATA_DIR, new_file), shape)



    


                           