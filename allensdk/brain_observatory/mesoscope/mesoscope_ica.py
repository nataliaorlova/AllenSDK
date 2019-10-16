from allensdk.brain_observatory.mesoscope.mesoscope_plane import MesoscopeOphysPlane
from allensdk.brain_observatory.mesoscope.mesoscope_session import MesoscopeSession
from allensdk.internal.api.mesoscope_plane_lims_api import MesoscopePlaneLimsApi

class MesoICAPair(object):

	def __init__(self, session_id, pair_num):
		self.session = MesoscopeSession.from_lims(session_id)
		pairs = self.session.pairs
		pair = pairs[pair_num]
		self.plane1 = MesoscopeOphysPlane(api = MesoscopePlaneLimsApi(pair[0], self.session))
		self.plane2 = MesoscopeOphysPlane(api = MesoscopePlaneLimsApi(pair[1], self.session))

class MesoscopeICA(object):
	"""
	this class has methods and attributes to perfrom ICA demixing on a mesoscope pair
	"""
	def __init__(self, session_id_1, session_id_2):
		self.pair = MesoICAPair(session_id_1, session_id_2)

