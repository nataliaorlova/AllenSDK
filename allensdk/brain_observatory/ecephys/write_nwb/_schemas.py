import os

from marshmallow import RAISE, ValidationError

from argschema import ArgSchema, ArgSchemaParser
from argschema.schemas import DefaultSchema
from argschema.fields import LogLevel, String, Int, DateTime, Nested, Boolean, Float


def check_write_access(path):
    try:
        fd = os.open(path, os.O_CREAT | os.O_EXCL)
        os.close(fd)
        os.remove(path)
        return True
    except FileNotFoundError:
        check_write_access(os.path.dirname(path))
    except PermissionError:
        raise ValidationError(f'don\'t have permissions to write {path}')
    except FileExistsError:
        if not os.path.isdir(path):
            raise ValidationError(f'file at {path} already exists')
        return True


def check_read_access(path):
    try:
        f = open(path, mode='r')
        f.close()
        return True
    except Exception as err:
        raise ValidationError(f'file at #{path} not readable (#{type(err)}: {err.message}')


class RaisingSchema(DefaultSchema):
    class Meta:
        unknown=RAISE


class Channel(RaisingSchema):
    id = Int(required=True)
    probe_id = Int(required=True)
    valid_data = Boolean(required=True)
    local_index = Int(required=True)
    probe_vertical_position = Int(required=True)
    probe_horizontal_position = Int(required=True)


class Unit(RaisingSchema):
    id = Int(required=True)
    peak_channel_id = Int(required=True)
    local_index = Int(required=True, description='within-probe index of this unit. Used for indexing into the spike times file.')
    # probe_id = Int(required=True, description='')
    quality = String(required=True)
    firing_rate = Float(required=True)
    snr = Float(required=True)
    isi_violations = Float(required=True)


class Probe(RaisingSchema):
    id = Int(required=True)
    name = String(required=True)
    spike_times_path = String(required=True)
    spike_clusters_file = String(required=True)
    channels = Nested(Channel, many=True, required=True)
    units = Nested(Unit, many=True, required=True)

class RunningSpeed(RaisingSchema):
    running_speed_path = String(required=True)
    running_speed_timestamps_path = String(required=True)


class InputSchema(ArgSchema):
    class Meta:
        unknown=RAISE
    log_level = LogLevel(default='INFO', description='set the logging level of the module')
    output_path = String(required=True, validate=check_write_access, description='write outputs to here')
    session_id = Int(required=True, description='unique identifier for this ecephys session')
    session_start_time = DateTime(required=True, description='the date and time (iso8601) at which the session started')
    stimulus_table_path = String(required=True, validate=check_read_access, description='path to stimulus table file')
    probes = Nested(Probe, many=True, required=True, description='records of the individual probes used for this experiment')
    running_speed = Nested(RunningSpeed, required=True, description='data collected about the running behavior of the experiment\'s subject')


class OutputSchema(RaisingSchema):
    nwb_path = String(required=True, description='path to output file')