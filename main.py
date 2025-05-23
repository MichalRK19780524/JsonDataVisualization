from os import times

import msgspec
from matplotlib import pyplot as plt
from enum import Flag, auto

class Mode(Flag):
    I = auto()
    U = auto()
    T = auto()


class Type(Flag):
    MASTER = auto()
    SLAVE = auto()

def read_file(file_path, mode=Mode.U, sipm_type=Type.MASTER | Type.SLAVE):
    decoder = msgspec.json.Decoder()
    with open(file_path, 'r') as file:
        # counter = 0
        timestamp_slave = []
        u_sipm_slave = []
        timestamp_master = []
        u_sipm_master = []
        for line in file:
            try:
                result = decoder.decode(line)
            except msgspec.DecodeError:
                pass
            if result is not None and isinstance(result['message'], dict):
                retval = result['message'].get('retval')
                if retval is not None and isinstance(retval, dict) and 'average_data' in retval:
                    average_data = retval['average_data']
                    # print(average_data)
                    # if( "timestamp_ms" in average_data):
                    #     print(average_data)
                    #     print(average_data.get("timestamp_ms"))
                    if(Type.SLAVE in sipm_type):
                        if('U_SIPM_MEAS1' in average_data):
                            # print(average_data)
                            timestamp_slave.append(average_data.get("timestamp_ms"))
                            u_sipm_slave.append(average_data.get("U_SIPM_MEAS1"))
                    if(Type.MASTER in sipm_type):
                        if('U_SIPM_MEAS0' in average_data):
                            # print(average_data)
                            timestamp_master.append(average_data.get("timestamp_ms"))
                            u_sipm_master.append(average_data.get("U_SIPM_MEAS0"))
    return timestamp_master, u_sipm_master, timestamp_slave, u_sipm_slave

if __name__ == "__main__":
    timestamp_master, u_sipm_master, timestamp_slave, u_sipm_slave = read_file("log_18.json")
    fig_master, ax_master = plt.subplots()
    ax_master.plot(timestamp_master, u_sipm_master)
    # ax_master.set_ylim(55.0, 55.25)
    # ax_master.set_xlim(left=500000)
    fig_slave, ax_slave = plt.subplots()
    ax_slave.plot(timestamp_slave, u_sipm_slave)
    ax_slave.set_ylim(55.0, 55.25)
    ax_slave.set_xlim(left=500000)
    # ax.set(xlabel='time (ms)', ylabel='U_SIPM_MEAS1 (V)',
    #        title='U_SIPM_MEAS1 vs time'
    # )
    plt.show()

