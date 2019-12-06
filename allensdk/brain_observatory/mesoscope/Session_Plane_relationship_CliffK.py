import sciris as sc
import pylab as pl

class Experiment:
    def __init__(self):
        self.api = 'i am an api'

class ExperimentMeso(Experiment):

    def __init__(self, uid):
        super(self).__init__()
        self.uid = uid
        self.timestamp = None
        self.session = None

    def get_timestamp(self):
        return self.session.timestamps[self.uid]

class Session:

    def __init__(self, do_run=True, n=5):
        self.n = n
        self.ids = []
        self.timestamps = {}
        self.experiments = {}
        if do_run:
            self.get_ids(n=n)
            self.make_experiments()
            self.get_timestamps()

    def get_ids(self, n):
        for i in range(n):
            self.ids.append(sc.uuid())
        return self.ids

    def make_experiments(self):
        for uid in self.ids:
            self.experiments[uid] = ExperimentMeso(uid=uid)
            self.experiments[uid].session = self # Support session.experiment.session.timesteps[uid]
        return self.experiments

    def get_timestamps(self):
        for uid in self.ids:
            self.timestamps[uid] = pl.rand()
        for uid, experiment in self.experiments.items():
            experiment.timestamp = self.timestamps[uid] # Supports session.experiment.timestamp, does not support update
