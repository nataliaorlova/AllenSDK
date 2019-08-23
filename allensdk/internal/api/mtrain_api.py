import pandas as pd
import requests
import os
import sys
import itertools
import json
import uuid

from . import PostgresQueryMixin
from .behavior_lims_api import BehaviorLimsApi
from allensdk.brain_observatory.behavior.trials_processing import EDF_COLUMNS

class MtrainApi(PostgresQueryMixin):

    def __init__(self, api_base='http://mtrain:5000'):
        self.api_base = api_base

    def get_page(self, table_name, get_obj=None, filters=[], **kwargs):
      
        if get_obj is None:
            get_obj = requests

        data = {'total_pages':'--'}
        for ii in itertools.count(1):
            sys.stdout.flush()

            uri = '/'.join([self.api_base, "api/v1/%s?page=%i&q={\"filters\":%s}" % (table_name, ii, json.dumps(filters))])
            tmp = get_obj.get(uri, **kwargs)
            try:
                data = tmp.json()
            except TypeError:
                data = tmp.json
            if 'message' not in data:
                df = pd.DataFrame(data["objects"])
                sys.stdout.flush()
                yield df

            if 'total_pages' not in data or data['total_pages'] == ii:
                return

    def get_df(self, table_name, get_obj=None, **kwargs):
        return pd.concat([df for df in self.get_page(table_name, get_obj=get_obj, **kwargs)], axis=0)

    def get_subjects(self):
        return self.get_df('subjects').LabTracks_ID.values

    def get_session(self, behavior_session_uuid=None, behavior_session_id=None):
        assert not all(v is None for v in [
                       behavior_session_uuid, behavior_session_id]), 'must enter either a behavior_session_uuid or a behavior_session_id'

        if behavior_session_uuid is None and behavior_session_id is not None:
            # get a behavior session uuid if a lims ID was entered
            behavior_session_uuid = BehaviorLimsApi.behavior_session_id_to_foraging_id(
                behavior_session_id)

        if behavior_session_uuid is not None and behavior_session_id is not None:
            # if both a behavior session uuid and a lims id are entered, ensure that they match
            assert behavior_session_uuid == BehaviorLimsApi.behavior_session_id_to_foraging_id(
                behavior_session_id), 'behavior_session {} does not match behavior_session_id {}'.format(behavior_session_uuid, behavior_session_id)
        filters = [{"name": "id", "op": "eq", "val": behavior_session_uuid}]
        behavior_df = self.get_df('behavior_sessions', filters=filters).rename(columns={'id': 'behavior_session_uuid'})
        state_df = self.get_df('states').rename(columns={'id': 'state_id'})
        regimen_df = self.get_df('regimens').rename(columns={'id': 'regimen_id', 'name': 'regimen_name'}).drop(['states', 'active'], axis=1)
        stage_df = self.get_df('stages').rename(columns={'id': 'stage_id'}).drop(['states'], axis=1)

        behavior_df = pd.merge(behavior_df, state_df, how='left', on='state_id')
        behavior_df = pd.merge(behavior_df, stage_df, how='left', on='stage_id')
        behavior_df = pd.merge(behavior_df, regimen_df, how='left', on='regimen_id')
        behavior_df.drop(['state_id', 'stage_id', 'regimen_id'], inplace=True, axis=1)
        if len(behavior_df) == 0:
            raise RuntimeError("Session not found %s:" % behavior_session_uuid)
        assert len(behavior_df) == 1
        session_dict = behavior_df.iloc[0].to_dict()

        filters = [{"name": "behavior_session_uuid", "op": "eq", "val": behavior_session_uuid}]
        trials_df = self.get_df('trials', filters=filters).sort_values('index').drop(['id', 'behavior_session'], axis=1).set_index('index', drop=False)
        trials_df['behavior_session_uuid'] = trials_df['behavior_session_uuid'].map(uuid.UUID)
        del trials_df.index.name
        session_dict['trials'] = trials_df[EDF_COLUMNS]

        return session_dict

    def get_behavior_training_df(self, LabTracks_ID=None):
        if LabTracks_ID is not None:
            filters = [{"name":"LabTracks_ID","op":"eq","val":LabTracks_ID}]
        else:
            filters = []
        behavior_df = self.get_df('behavior_sessions', filters=filters).rename(columns={'id':'behavior_session_uuid'})
        
        state_df = self.get_df('states').rename(columns={'id':'state_id'})
        regimen_df = self.get_df('regimens').rename(columns={'id':'regimen_id', 'name':'regimen_name'}).drop(['states', 'active'], axis=1)
        stage_df = self.get_df('stages').rename(columns={'id':'stage_id', 'name':'stage_name'}).drop(['states'], axis=1)

        behavior_df = pd.merge(behavior_df, state_df, how='left', on='state_id')
        behavior_df = pd.merge(behavior_df, stage_df, how='left', on='stage_id')
        behavior_df = pd.merge(behavior_df, regimen_df, how='left', on='regimen_id')
        return behavior_df


    def get_current_stage(self, LabTracks_ID):
        sess = requests.Session()

        state_response = sess.get(os.path.join(self.api_base, 'get_script/'), data=json.dumps({'LabTracks_ID':LabTracks_ID}))#.json()#['objects']).keys()
        return state_response.json()['data']['parameters']['stage']


class MtrainSqlApi(PostgresQueryMixin):
    
    def __init__(self, dbname="mtrain", user="mtrainreader", host="prodmtrain1", password="mtrainro", port=5432):
        super(MtrainSqlApi, self).__init__(dbname=dbname, user=user, host=host, password=password, port=port)


    def get_subjects(self):
        query = 'SELECT "LabTracks_ID" FROM subjects'
        return self.fetchall(query)


    def get_behavior_training_df(self, LabTracks_ID):
        connection = self.get_connection()
        dataframe = pd.read_sql(
            '''SELECT stages.name as stage_name, regimens.name as regimen_name, bs.date, bs.id as behavior_session_id
               FROM behavior_sessions bs
               LEFT JOIN states ON states.id = bs.state_id
               LEFT JOIN regimens ON regimens.id = states.regimen_id
               LEFT JOIN stages ON stages.id = states.stage_id
               WHERE "LabTracks_ID"={}
            '''.format(LabTracks_ID), connection)
        return dataframe.sort_values(by='date')
