from allensdk.brain_observatory.mesoscope.plane import MesoscopePlane
from allensdk.brain_observatory.mesoscope.session import MesoscopeSession
from allensdk.internal.api.mesoscope_plane_lims_api import MesoscopePlaneLimsApi

import os

class MesoICAPair(object):

	def __init__(self, session_id, pair_num, cache = '/media/rd-storage/X/decrosstalk/'):
		self.session = MesoscopeSession.from_lims(session_id)
		pairs = self.session.pairs
		pair = pairs[pair_num]
		self.plane1 = MesoscopePlane(api = MesoscopePlaneLimsApi(pair[0], self.session))
		self.plane2 = MesoscopePlane(api = MesoscopePlaneLimsApi(pair[1], self.session))
		self.session_id = session_id
		self.cache = cache
		self.session_dir = os.path.join(self.cache, f'session_{self.session_id}')
		self.ica_traces_dir = None
		self.ica_neuropil_dir = None

		#input to demixing, cells:
		self.plane1.ica_traces_in = None
		self.plane2.ica_traces_in = None
		self.plane1.ica_traces_in_path = None
		self.plane2.ica_traces_in_path = None
		#output of demixing, cells:
		self.plane1.ica_traces_out = None
		self.plane2.ica_traces_out = None
		self.plane1.ica_traces_out_path = None
		self.plane2.ica_traces_out_path = None
		self.mixing_matrix_traces_path = None
		#input to demixing, neuropil:
		self.plane1.ica_neuropil_in = None
		self.plane2.ica_neuropil_in = None
		self.plane1.ica_neuropil_in_path = None
		self.plane2.ica_neuropil_in_path = None
		#output of demixing, neuropil:
		self.plane1.ica_neuropil_out = None
		self.plane2.ica_neuropil_out = None
		self.plane1.ica_neuropil_out_path = None
		self.plane2.ica_neuropil_out_path = None
		self.mixing_matrix_neuropil_path = None


	def set_ica_traces_dir(self):
		self.ica_traces_dir = os.path.join(self.session_dir, f'ica_traces_{self.plane1.ophys_experiment_id}_{self.plane2.ophys_experiment_id}/')
		self.plane1.ica_traces_in_path = os.path.join(self.ica_traces_dir, f'traces_ica_input_{self.plane1.ophys_experiment_id}.h5')
		self.plane2.ica_traces_in_path = os.path.join(self.ica_traces_dir, f'traces_ica_input_{self.plane2.ophys_experiment_id}.h5')
		self.plane1.ica_traces_out_path = os.path.join(self.ica_traces_dir, f'traces_ica_output_{self.plane1.ophys_experiment_id}.h5')
		self.plane2.ica_traces_out_path = os.path.join(self.ica_traces_dir, f'traces_ica_output_{self.plane2.ophys_experiment_id}.h5')
		self.mixing_matrix_traces_path = os.path.join(self.ica_traces_dir, f'traces_ica_mixing.h5')
		return

	def set_ica_neuropil_dir(self):
		self.ica_neuropil_dir = os.path.join(self.session_dir, f'ica_neuropil_{self.plane1.ophys_experiment_id}_{self.plane2.ophys_experiment_id}/')
		self.plane1.ica_neuropil_in_path = os.path.join(self.ica_neuropil_dir, f'neuropil_ica_input_{self.plane1.ophys_experiment_id}.h5')
		self.plane2_ica_neuropil_in_path = os.path.join(self.ica_neuropil_dir, f'neuropil_ica_input_{self.plane2.ophys_experiment_id}.h5')
		self.plane1_ica_neuropil_out_path = os.path.join(self.ica_neuropil_dir, f'neuropil_ica_output_{self.plane1.ophys_experiment_id}.h5')
		self.plane2_ica_neuropil_out_path = os.path.join(self.ica_neuropil_dir, f'neuropil_ica_output_{self.plane2.ophys_experiment_id}.h5')
		self.ica_mixing_matrix_neuropil_path = os.path.join(self.ica_neuropil_dir, f'neuropil_ica_mixing.h5')
		return


class MesoscopeICA(object):
	"""
	this class has methods and attributes to perfrom ICA demixing on a mesoscope pair
	"""
	def __init__(self, session_id, pair_num):
		self.pair = MesoICAPair(session_id, pair_num)




if __name__ == '__main__':
	ms_ica_pair = MesoICAPair(882386411, 3)
	print(f'Plane 1 experiment id = {ms_ica_pair.plane1.ophys_experiment_id}')
	print(f'Plane 2 experiment id = {ms_ica_pair.plane2.ophys_experiment_id}')
	print(f'Session ID: {ms_ica_pair.session_id}')
	ms_ica_pair.set_ica_traces_dir()
	ms_ica_pair.set_ica_neuropil_dir()
	print(f'ICA traces dir: {ms_ica_pair.ica_traces_dir}')
	print(f'Neuropil traces dir: {ms_ica_pair.ica_neuropil_dir}')

		# self.ica_traces_dir = None
		# #input to demixing:
		# self.plane1.ica_traces_in = None
		# self.plane2.ica_traces_in = None
		# self.plane1.ica_traces_in_path = None
		# self.plane2.ica_traces_in_path = None
		# #output of demixing:
		# self.plane1.ica_traces_out = None
		# self.plane2.ica_traces_out = None
		# self.plane1.ica_traces_out_path = None
		# self.plane2.ica_traces_out_path = None
		# self.mixing_matrix_path = None


	# ms_ica = MesoscopeICA(882386411, 1)
	# print(f'session cache: {ms_ica.pair.plane1}')
	# print(f'session analysis dir: {ms_ica.session_cache_dir}')
	# print(f'traces dir : {ms_ica.ica_traces_dir}')



