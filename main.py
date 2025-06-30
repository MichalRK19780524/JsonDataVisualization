# from os import times
from os import times_result

import msgspec
from matplotlib import pyplot as plt
from enum import Flag, auto
import pandas as pd
import numpy as np
from IPython.display import display

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

    def __repr__(self):
        return (f"AFEParameters("
                f"v_opt={self.v_opt}, "
                f"t_opt={self.t_opt}, "
                f"u_measured_b={self.u_measured_b}, "
                f"dv_dt={self.dv_dt}, "
                f"u_set_b={self.u_set_b}, "
                f"t_measured_a={self.t_measured_a}, "
                f"dt={self.dt}, "
                f"u_set_a={self.u_set_a}, "
                f"t_measured_b={self.t_measured_b}, "
                f"u_measured_a={self.u_measured_a}, "
                f"i_measured_b={self.i_measured_b}, "
                f"i_measured_a={self.i_measured_a}, "
                f"offset={self.offset}, "
                f"t_br={self.t_br}, "
                f"avg_number={self.avg_number}, "
                f"v_br={self.v_br})")

class MeasurementParameters:
    def __init__(self, id: int=0, afeMaster: AFEParameters=AFEParameters, afeSlave: AFEParameters=AFEParameters):
        self.id = id
        self.afeMaster = afeMaster
        self.afeSlave = afeSlave

    def __str__(self):
        return (f"MeasurementParameters:\n"
                f"  ID: {self.id}\n"
                f"  AFE Master: {self.afeMaster}\n"
                f"  AFE Slave: {self.afeSlave}")

    def __repr__(self):
        return (f"MeasurementParameters("
                f"id={self.id}, "
                f"afeMaster={self.afeMaster}, "
                f"afeSlave={self.afeSlave}")

class PlotData:
    def __init__(self, u_timestamp_master, u_sipm_master, i_timestamp_master, i_sipm_master, t_timestamp_master,
                 t_sipm_master, u_timestamp_slave, u_sipm_slave, i_timestamp_slave, i_sipm_slave, t_timestamp_slave, t_sipm_slave,
                 measurement_parameters: MeasurementParameters):
        self.u_timestamp_master = u_timestamp_master
        self.u_sipm_master = u_sipm_master
        self.i_timestamp_master = i_timestamp_master
        self.i_sipm_master = i_sipm_master
        self.t_timestamp_master = t_timestamp_master
        self.t_sipm_master = t_sipm_master
        self.u_timestamp_slave = u_timestamp_slave
        self.u_sipm_slave = u_sipm_slave
        self.i_timestamp_slave = i_timestamp_slave
        self.i_sipm_slave = i_sipm_slave
        self.t_timestamp_slave = t_timestamp_slave
        self.t_sipm_slave = t_sipm_slave
        self.measurement_parameters = measurement_parameters


    def __repr__(self):
        return (f"PlotData("
            f"u_timestamp_master={self.u_timestamp_master}, "
            f"u_sipm_master={self.u_sipm_master}, "
            f"i_timestamp_master={self.i_timestamp_master}, "
            f"i_sipm_master={self.i_sipm_master}, "
            f"t_timestamp_master={self.t_timestamp_master}, "
            f"t_sipm_master={self.t_sipm_master}, "
            f"u_timestamp_slave={self.u_timestamp_slave}, "
            f"u_sipm_slave={self.u_sipm_slave}, "
            f"i_timestamp_slave={self.i_timestamp_slave}, "
            f"i_sipm_slave={self.i_sipm_slave}, "
            f"t_timestamp_slave={self.t_timestamp_slave}, "
            f"t_sipm_slave={self.t_sipm_slave}, "
            f"measurement_parameters={self.measurement_parameters})")

    def __str__(self):
        return (f"PlotData:\n"
                f"  Master SiPM:\n"
                f"    Timestamps U: {self.u_timestamp_master}\n"
                f"    Timestamps I: {self.i_timestamp_master}\n"
                f"    Timestamps T: {self.t_timestamp_master}\n"
                f"    Voltage: {self.u_sipm_master}\n"
                f"    Current: {self.i_sipm_master}\n"
                f"    Temperature: {self.t_sipm_master}\n"
                f"  Slave SiPM:\n"
                f"    Timestamps U: {self.u_timestamp_slave}\n"
                f"    Timestamps I: {self.i_timestamp_slave}\n"
                f"    Timestamps T: {self.t_timestamp_slave}\n"
                f"    Voltage: {self.u_sipm_slave}\n"
                f"    Current: {self.i_sipm_slave}\n"
                f"    Temperature: {self.t_sipm_slave}\n"
                f"  Measurement Parameters: {self.measurement_parameters}")


both =  Type.SLAVE | Type.MASTER
all_modes = Mode.U | Mode.I | Mode.T
def read_file(file_path: str, mode: Mode = all_modes, sipm_type: Type = both) -> PlotData:
    decoder = msgspec.json.Decoder()
    with open(file_path, 'r') as file:
        # counter = 0
        timestamp_slave_u = np.array([])
        u_sipm_slave = np.array([])
        timestamp_master_u = np.array([])
        u_sipm_master = np.array([])
        timestamp_slave_i = np.array([])
        i_sipm_slave = np.array([])
        timestamp_master_i = np.array([])
        i_sipm_master = np.array([])
        timestamp_slave_t = np.array([])
        t_sipm_slave = np.array([])
        timestamp_master_t = np.array([])
        t_sipm_master = np.array([])

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
                        msg = message.get('msg')
                        if msg is not None:
                            # measurement_parameters.id = msg.get("ID")
                            id = msg.get("ID")
                            # print("msg is not None ", measurment_parameters.id)
                            afe_master = msg.get("M")
                            if afe_master is not None and isinstance(afe_master, dict):
                                v_opt = afe_master.get("V_opt [V]")
                                t_opt = afe_master.get("T_opt [T]")
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
                            afeMasterParameters = AFEParameters(v_opt, t_opt, u_measured_b, dv_dt, u_set_b, t_measured_a, dt, u_set_a, t_measured_b, u_measured_a, i_measured_b, i_measured_a, offset, t_br, avg_number, v_br)

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
                            afeSlaveParameters = AFEParameters(v_opt, t_opt, u_measured_b, dv_dt,
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
                                    timestamp_slave_u = np.append(timestamp_slave_u, result.get("timestamp"))
                                    u_sipm_slave = np.append(u_sipm_slave, average_data.get("U_SIPM_MEAS1"))
                            if Mode.I in mode:
                                if 'I_SIPM_MEAS1' in average_data:
                                    timestamp_slave_i = np.append(timestamp_slave_i, result.get("timestamp"))
                                    i_sipm_slave = np.append(i_sipm_slave, average_data.get("I_SIPM_MEAS1"))
                            if Mode.T in mode:
                                if 'TEMP_EXT' in average_data:
                                    timestamp_slave_t = np.append(timestamp_slave_t, result.get("timestamp"))
                                    t_sipm_slave = np.append(t_sipm_slave, average_data.get("TEMP_EXT"))
                        if Type.MASTER in sipm_type:
                            if Mode.U in mode:
                                if 'U_SIPM_MEAS0' in average_data:
                                    timestamp_master_u = np.append(timestamp_master_u, result.get("timestamp"))
                                    u_sipm_master = np.append(u_sipm_master, average_data.get("U_SIPM_MEAS0"))
                            if Mode.I in mode:
                                if 'I_SIPM_MEAS0' in average_data:
                                    timestamp_master_i = np.append(timestamp_master_i, result.get("timestamp"))
                                    i_sipm_master = np.append(i_sipm_master, average_data.get("I_SIPM_MEAS0"))
                            if Mode.T in mode:
                                if 'TEMP_LOCAL' in average_data:
                                    timestamp_master_t = np.append(timestamp_master_t, result.get("timestamp"))
                                    t_sipm_master = np.append(t_sipm_master, average_data.get("TEMP_LOCAL"))
    # print(measurement_parameters)
    return PlotData(u_timestamp_master=timestamp_master_u,
                    u_sipm_master=u_sipm_master,
                    i_timestamp_master=timestamp_master_i,
                    i_sipm_master=i_sipm_master,
                    t_timestamp_master=timestamp_master_t,
                    t_sipm_master=t_sipm_master,
                    u_timestamp_slave=timestamp_slave_u,
                    u_sipm_slave=u_sipm_slave,
                    i_timestamp_slave=timestamp_slave_i,
                    i_sipm_slave=i_sipm_slave,
                    t_timestamp_slave=timestamp_slave_t,
                    t_sipm_slave=t_sipm_slave,
                    measurement_parameters=MeasurementParameters(id, afeMasterParameters, afeSlaveParameters))

if __name__ == "__main__":
    plot_data = read_file("log_6.json")
    binder_data_df = pd.read_csv("prog12 2025-05-30.prg", encoding="ISO-8859-1", sep="\t", decimal=",", parse_dates=['Length'], date_format="%H:%M",
                                header=0, skiprows=[0, 1, 2, 4], usecols=['Value', 'Length'])
    # print(binder_data_df)
    # print(binder_data_df.info(memory_usage='deep'))
    start_time = pd.Timestamp("1900-01-01 00:00:00")
    zero_time = pd.Timestamp("00:00:00")
    # display(start_time)
    # display(zero_time)
    # time_stamp = binder_data_df['Length'][1]
    # display(time_stamp)
    # delta0 = binder_data_df['Length'][0] - start_time
    # delta1 = binder_data_df['Length'][1] - start_time
    # display(delta0)
    # display(type(delta0))
    # display(delta1)
    # suma = delta0 + delta1
    # display(suma)
    # display(type(suma))
    # display(binder_data_df['Length'])
    counter = 0
    time_series = [0]
    result = 0
    length = len(binder_data_df) - 1
    while counter < length:
        if counter == 0:
            result = binder_data_df['Length'][counter] - start_time
        else:
            result += (binder_data_df['Length'][counter] - start_time)
        time_series.append(result.total_seconds()/3600)
        counter += 1
    np_t_timestamp_master_h = plot_data.t_timestamp_master / 1000 / 3600
    fig, ax_temperature = plt.subplots()
    ax_temperature.plot(time_series, binder_data_df['Value'], np_t_timestamp_master_h, plot_data.t_sipm_master)
    ax_temperature.set_xlabel('time [h]')
    ax_temperature.set_ylabel('Temperature [°C]')
    ax_temperature.set_title("Binder Temperature and SiPM Temperature")
    ax_temperature.set_xlim(left=-2, right=24)
    ax_temperature.grid(True)
    ax_voltage = ax_temperature.twinx()
    np_u_timestamp_master_h = plot_data.u_timestamp_master / 1000 / 3600
    mask = plot_data.u_sipm_master > 48
    np_u_timestamp_master_h = np_u_timestamp_master_h[mask]
    plot_data.u_sipm_master = plot_data.u_sipm_master[mask]
    ax_voltage.set_ylabel('Voltage [V]')
    ax_voltage.plot(np_u_timestamp_master_h, plot_data.u_sipm_master)
    plt.show()
    # fig_master_u, ax_master_u = plt.subplots()
    # ax_master_u.plot(plot_data.u_timestamp_master, plot_data.u_sipm_master)
    # ax_master_u.set_ylim(55.0, 55.25)
    # ax_master_u.set_xlim(left=500000)
    # fig_slave, ax_slave = plt.subplots()
    # ax_slave.plot(plot_data.u_timestamp_slave, plot_data.u_sipm_slave)
    # ax_slave.set_ylim(55.0, 55.25)
    # ax_slave.set_xlim(left=500000)
    # fig_master_t, ax_master_t = plt.subplots()
    # ax_master_t.plot(plot_data.t_timestamp_master, plot_data.t_sipm_master)
    # ax_slave.set(xlabel='time (ms)', ylabel='U_SIPM_MEAS1 (V)',
    #        title='U_SIPM_MEAS1 vs time'
    # )
    # plt.show()
