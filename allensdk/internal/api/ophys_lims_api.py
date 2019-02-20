from . import PostgresQueryMixin

from allensdk.api.cache import memoize

class OphysLimsApi(PostgresQueryMixin):

    @memoize
    def get_ophys_experiment_dir(self, ophys_experiment_id=None):
        query = '''
                SELECT oe.storage_directory
                FROM ophys_experiments oe
                WHERE oe.id = {ophys_experiment_id};
                '''.format(ophys_experiment_id=ophys_experiment_id)
        return self.fetchone(query, strict=True)


    @memoize
    def get_nwb_filepath(self, ophys_experiment_id=None):

        query = '''
                SELECT wkf.storage_directory || wkf.filename AS nwb_file
                FROM ophys_experiments oe
                LEFT JOIN well_known_files wkf ON wkf.attachable_id=oe.id AND wkf.well_known_file_type_id IN (SELECT id FROM well_known_file_types WHERE name = 'NWBOphys')
                WHERE oe.id = {ophys_experiment_id};
                '''.format(ophys_experiment_id=ophys_experiment_id)
        return self.fetchone(query, strict=True)


    @memoize
    def get_sync_file(self, ophys_experiment_id=None):
        query = '''
                SELECT sync.storage_directory || sync.filename AS sync_file
                FROM ophys_experiments oe
                JOIN ophys_sessions os ON oe.ophys_session_id = os.id
                LEFT JOIN well_known_files sync ON sync.attachable_id=os.id AND sync.attachable_type = 'OphysSession' AND sync.well_known_file_type_id IN (SELECT id FROM well_known_file_types WHERE name = 'OphysRigSync')
                WHERE oe.id= {};
                '''.format(ophys_experiment_id)        
        return self.fetchone(query, strict=True)