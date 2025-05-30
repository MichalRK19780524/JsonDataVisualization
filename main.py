# from os import times

import msgspec
from matplotlib import pyplot as plt
from enum import Flag, auto

# from matplotlib.pyplot import plot_date


class Mode(Flag):   # which physical quantity to read
    I = auto()      #   current
    U = auto()      #   voltage
    T = auto()      #   temperature

class Type(Flag):   # which board(s) to read
    MASTER = auto()
    SLAVE  = auto()

class MeasurementParameters:
    def __init__(self, id: int, type: Type):
        self.id = id
        self.type = type

class PlotData:
    def __init__(self, timestamp_master, u_sipm_master, i_sipm_master,
                 t_sipm_master, timestamp_slave, u_sipm_slave, i_sipm_slave, t_sipm_slave):
        self.timestamp_master = timestamp_master
        self.u_sipm_master = u_sipm_master
        self.i_sipm_master = i_sipm_master
        self.t_sipm_master = t_sipm_master
        self.timestamp_slave = timestamp_slave
        self.u_sipm_slave = u_sipm_slave
        self.i_sipm_slave = i_sipm_slave
        self.t_sipm_slave = t_sipm_slave


    def __repr__(self):
        return (f"Result("
            f"timestamp_master_u={self.timestamp_master}, "
            f"u_sipm_master={self.u_sipm_master}, "
            f"i_sipm_master={self.i_sipm_master}, "
            f"t_sipm_master={self.t_sipm_master}, "
            f"timestamp_slave_u={self.timestamp_slave}, "
            f"u_sipm_slave={self.u_sipm_slave}, "
            f"i_sipm_slave={self.i_sipm_slave}, "
            f"t_sipm_slave={self.t_sipm_slave})")


both =  Type.SLAVE | Type.MASTER
all_modes = Mode.U | Mode.I | Mode.T
def read_file(file_path: str, mode: Mode = all_modes, sipm_type: Type = both) -> PlotData:
    decoder = msgspec.json.Decoder()
    with open(file_path, 'r') as file:
        # counter = 0
        timestamp_slave_u = []
        u_sipm_slave = []
        timestamp_master_u = []
        u_sipm_master = []
        timestamp_slave_i = []
        i_sipm_slave = []
        timestamp_master_i = []
        i_sipm_master = []
        timestamp_slave_t = []
        t_sipm_slave = []
        timestamp_master_t = []
        t_sipm_master = []
        for line in file:
            try:
                result = decoder.decode(line)
            except msgspec.DecodeError:
                pass
            if result is not None and isinstance(result['message'], dict):
                retval = result['message'].get('retval')
                if retval is not None and isinstance(retval, dict) and 'average_data' in retval:
                    average_data = retval['average_data']
                    if Type.SLAVE in sipm_type:
                        if Mode.U in mode:
                            if 'U_SIPM_MEAS1' in average_data:
                                timestamp_slave_u.append(result.get("timestamp"))
                                u_sipm_slave.append(average_data.get("U_SIPM_MEAS1"))
                        if Mode.I in mode:
                            if 'I_SIPM_MEAS1' in average_data:
                                timestamp_slave_i.append(result.get("timestamp"))
                                i_sipm_slave.append(average_data.get("I_SIPM_MEAS1"))
                        if Mode.T in mode:
                            if 'TEMP_EXT' in average_data:
                                timestamp_slave_t.append(result.get("timestamp"))
                                t_sipm_slave.append(average_data.get("TEMP_EXT"))
                    if Type.MASTER in sipm_type:
                        if Mode.U in mode:
                            if 'U_SIPM_MEAS0' in average_data:
                                timestamp_master_u.append(result.get("timestamp"))
                                u_sipm_master.append(average_data.get("U_SIPM_MEAS0"))
                        if Mode.I in mode:
                            if 'I_SIPM_MEAS0' in average_data:
                                timestamp_master_i.append(result.get("timestamp"))
                                i_sipm_master.append(average_data.get("I_SIPM_MEAS0"))
                        if Mode.T in mode:
                            if 'TEMP_LOCAL' in average_data:
                                timestamp_master_t.append(result.get("timestamp"))
                                t_sipm_master.append(average_data.get("TEMP_LOCAL"))
    return PlotData(timestamp_master=timestamp_master_u,
                    u_sipm_master=u_sipm_master,
                    i_sipm_master=i_sipm_master,
                    t_sipm_master=t_sipm_master,
                    timestamp_slave=timestamp_slave_u,
                    u_sipm_slave=u_sipm_slave,
                    i_sipm_slave=i_sipm_slave,
                    t_sipm_slave=t_sipm_slave)

if __name__ == "__main__":
    plot_date = read_file("log_18.json")
    print(plot_date)
    fig_master_u, ax_master_u = plt.subplots()
    ax_master_u.plot(plot_date.timestamp_master, plot_date.u_sipm_master)
    ax_master_u.set_ylim(55.0, 55.25)
    ax_master_u.set_xlim(left=500000)
    fig_slave, ax_slave = plt.subplots()
    ax_slave.plot(plot_date.timestamp_slave, plot_date.u_sipm_slave)
    ax_slave.set_ylim(55.0, 55.25)
    ax_slave.set_xlim(left=500000)
    fig_master_t, ax_master_t = plt.subplots()
    ax_master_t.plot(plot_date.timestamp_master, plot_date.t_sipm_master)
    ax_slave.set(xlabel='time (ms)', ylabel='U_SIPM_MEAS1 (V)',
           title='U_SIPM_MEAS1 vs time'
    )
    plt.show()