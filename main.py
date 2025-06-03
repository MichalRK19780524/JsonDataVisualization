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

class AFEParameters:
    def __init__(self, v_opt: float=0, t_opt: float=0,
                 u_measured_b: float=0, dv_dt: float=0,
                 u_set_b: float=0, t_measured_a: float=0, dt: float=0,
                 u_set_a: float=0, t_measured_b: float=0, u_measured_a: float=0,
                 i_measured_b: float=0, i_measured_a: float=0, offset: int=0,
                 t_br: float=0, avg_number: int=0, v_br: float=0):
        self.v_opt = v_opt
        self.t_opt = t_opt
        self.u_measured_b = u_measured_b
        self.dv_dt = dv_dt
        self.u_set_b = u_set_b
        self.t_measured_a = t_measured_a
        self.dt = dt
        self.u_set_a = u_set_a
        self.t_measured_b = t_measured_b
        self.u_measured_a = u_measured_a
        self.i_measured_b = i_measured_b
        self.i_measured_a = i_measured_a
        self.offset = offset
        self.t_br = t_br
        self.avg_number = avg_number
        self.v_br = v_br

class MeasurementParameters:
    def __init__(self, id: int=0, afeMaster: AFEParameters=AFEParameters, afeSlave: AFEParameters=AFEParameters):
        self.id = id
        self.afeMaster = afeMaster
        self.afeSlave = afeSlave

    def __repr__(self):
        return (f"MeasurementParameters("
                f"id={self.id}, "
                f"afeMaster={self.afeMaster}, "
                f"afeSlave={self.afeSlave}")

class PlotData:
    def __init__(self, timestamp_master, u_sipm_master, i_sipm_master,
                 t_sipm_master, timestamp_slave, u_sipm_slave, i_sipm_slave, t_sipm_slave, measurment_parameters: MeasurementParameters):
        self.timestamp_master = timestamp_master
        self.u_sipm_master = u_sipm_master
        self.i_sipm_master = i_sipm_master
        self.t_sipm_master = t_sipm_master
        self.timestamp_slave = timestamp_slave
        self.u_sipm_slave = u_sipm_slave
        self.i_sipm_slave = i_sipm_slave
        self.t_sipm_slave = t_sipm_slave
        self.measurment_parameters = measurment_parameters


    def __repr__(self):
        return (f"Result("
            f"timestamp_master_u={self.timestamp_master}, "
            f"u_sipm_master={self.u_sipm_master}, "
            f"i_sipm_master={self.i_sipm_master}, "
            f"t_sipm_master={self.t_sipm_master}, "
            f"timestamp_slave_u={self.timestamp_slave}, "
            f"u_sipm_slave={self.u_sipm_slave}, "
            f"i_sipm_slave={self.i_sipm_slave}, "
            f"t_sipm_slave={self.t_sipm_slave})"
            f"measurment_parameters={self.measurment_parameters}")


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
        measurment_parameters = MeasurementParameters

        for line in file:
            try:
                result = decoder.decode(line)
            except msgspec.DecodeError:
                pass
            if result is not None :
                message = result.get('message')
                if message is not None and isinstance(message, dict):
                    info = message.get('info')
                    if info == 'default_procedure':
                        msg = result.get('msg')
                        if msg is not None:
                            measurment_parameters.id = msg.get("ID")
                            afe_master = msg.get("M")
                            if afe_master is not None and isinstance(afe_master, dict):
                                v_opt = afe_master.get("V_opt")
                                t_opt = afe_master.get("T_opt")
                                u_measured_b = afe_master.get("U_measured_b ")
                                dv_dt = afe_master.get("dV/dT [V/T]")
                                u_set_b = afe_master.get("U_set_b")
                                t_measured_a = afe_master.get("T_measured_a")
                                dt = afe_master.get("dT [C]")
                                u_set_a = afe_master.get("U_set_a")
                                t_measured_b = afe_master.get("T_measured_b")
                                u_measured_a = afe_master.get("U_measured_a")
                                i_measured_b = afe_master.get("I_measured_b")
                                i_measured_a = afe_master.get("I_measured_a")
                                offset = afe_master.get("offset [bit]")
                                t_br = afe_master.get("T_br [T]")
                                avg_number = afe_master.get("Avg_number")
                                v_br = afe_master.get("V_br [V]")
                            measurment_parameters.afeMaster = AFEParameters(v_opt, t_opt, u_measured_b, dv_dt, u_set_b, t_measured_a, dt, u_set_a, t_measured_b, u_measured_a, i_measured_b, i_measured_a, offset, t_br, avg_number, v_br)

                            afe_slave = msg.get("S")
                            if afe_slave is not None and isinstance(afe_slave, dict):
                                v_opt = afe_slave.get("V_opt")
                                t_opt = afe_slave.get("T_opt")
                                u_measured_b = afe_slave.get("U_measured_b ")
                                dv_dt = afe_slave.get("dV/dT [V/T]")
                                u_set_b = afe_slave.get("U_set_b")
                                t_measured_a = afe_slave.get("T_measured_a")
                                dt = afe_slave.get("dT [C]")
                                u_set_a = afe_slave.get("U_set_a")
                                t_measured_b = afe_slave.get("T_measured_b")
                                u_measured_a = afe_slave.get("U_measured_a")
                                i_measured_b = afe_slave.get("I_measured_b")
                                i_measured_a = afe_slave.get("I_measured_a")
                                offset = afe_slave.get("offset [bit]")
                                t_br = afe_slave.get("T_br [T]")
                                avg_number = afe_slave.get("Avg_number")
                                v_br = afe_slave.get("V_br [V]")
                            measurment_parameters.afeSlave = AFEParameters(v_opt, t_opt, u_measured_b, dv_dt,
                                                                                u_set_b, t_measured_a, dt, u_set_a,
                                                                                t_measured_b, u_measured_a,
                                                                                i_measured_b, i_measured_a, offset,
                                                                                t_br, avg_number, v_br)
                    retval = message.get('retval')
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
                    t_sipm_slave=t_sipm_slave,
                    measurment_parameters=measurment_parameters)

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