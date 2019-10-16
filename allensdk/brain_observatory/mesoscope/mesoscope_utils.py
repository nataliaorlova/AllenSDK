from . import PostgresQueryMixin
import pandas as pd
import logging
from allensdk.brain_observatory import roi_masks
import numpy as np
import json
import os
import h5py

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

from pymongo import MongoClient
mongo = MongoClient('10.128.105.108', 27017)


def get_all_created_sessions():

    db = PostgresQueryMixin()
    query = ("select os.id as session_id, "
             "os.storage_directory as session_folder, "
             "sp.name as specimen, "
             "os.date_of_acquisition as date, "
             "os.workflow_state as session_wfl_state, " 
             "users.login as operator, "
             "p.code as project "
             "from ophys_sessions os "
             "join specimens sp on sp.id = os.specimen_id "
             "join projects p on p.id = os.project_id "
             "join users on users.id = os.operator_id "
#             "join equipment rigs on rigs.id = os.equipment_id "
             "where p.code in ('MesoscopeDevelopment', 'VisualBehaviorMultiscope', 'VisualBehaviorMultiscope4areasx2d', 'VisualBehaviorMultiscopeTask1G')"
             "order by date")

    #let's for now read stim type from mouse_director
    #in the future this should be in lims

    #return pd.read_sql(query, db.get_connection())
    meso_data_df = pd.read_sql(query, db.get_connection())
    session_ids = meso_data_df['session_id']
    meso_data_df['stimulus_type'] = None

    for session_id in session_ids:
        x = mongo.qc.metrics.find_one({'lims_id': int(session_id)})
        if x :
            if 'change_detection' in x.keys():
                 stim_type = x['change_detection']['stage']
                 meso_data_df.loc[meso_data_df['session_id'] == session_id,'stimulus_type'] = stim_type
            else:
                if 'stimulus_pickle' in x.keys():
                    stim_type = x['stimulus_pickle']['stage']
                    meso_data_df.loc[meso_data_df['session_id'] == session_id,'stimulus_type'] = stim_type
                else:
                    logger.warning(f'session {session_id} has no behavior data in mouse seeks')
    return meso_data_df

def create_roi_masks(rois, w, h, motion_border):
    roi_list = []
    for roi in rois:
        mask = np.array(roi["mask"], dtype=bool)
        px = np.argwhere(mask)
        px[:, 0] += roi["y"]
        px[:, 1] += roi["x"]

        mask = roi_masks.create_roi_mask(w, h, motion_border,
                                         pix_list=px[:, [1, 0]],
                                         label=str(roi["id"]),
                                         mask_group=roi.get("mask_page", -1))

        roi_list.append(mask)
    # sort by roi id
    roi_list.sort(key=lambda x: x.label)
    return roi_list

def get_traces(movie_exp_dir, movie_exp_id, mask_exp_dir, mask_exp_id):
    jin_movie_path = os.path.join(movie_exp_dir, f"processed/{movie_exp_id}_input_extract_traces.json")

    jin_mask_path = os.path.join(mask_exp_dir, f"processed/{mask_exp_id}_input_extract_traces.json")

    with open(jin_movie_path, "r") as f:
        jin_movie = json.load(f)

    motion_border = jin_movie.get("motion_border", [])
    motion_border = [motion_border["x0"], motion_border["x1"], motion_border["y0"], motion_border["y1"], ]

    movie_h5 = jin_movie["motion_corrected_stack"]

    with h5py.File(movie_h5, "r") as f:
        d = f["data"]
        h = d.shape[1]
        w = d.shape[2]

    # reading traces extracting json for masks
    with open(jin_mask_path, "r") as f:
        jin_mask = json.load(f)

    rois = jin_mask["rois"]

    roi_mask_list = create_roi_masks(rois, w, h, motion_border)
    roi_names = [ roi.label for roi in roi_mask_list ]

    traces, neuropil_traces = roi_masks.calculate_roi_and_neuropil_traces(movie_h5, roi_mask_list, motion_border)
    return traces, neuropil_traces, roi_names
