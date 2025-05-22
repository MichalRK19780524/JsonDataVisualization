from os import times

import msgspec
from matplotlib import pyplot as plt
from enum import Enum

class Mode(Enum):


def read_file(file_path, mode=0):
    decoder = msgspec.json.Decoder()
    with open(file_path, 'r') as file:
        # counter = 0
        timestamp_slave = []
        u_sipm_slave = []
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
                    if('U_SIPM_MEAS1' in average_data):
                        # print(average_data)
                        timestamp_slave.append(average_data.get("timestamp_ms"))
                        u_sipm_slave.append(average_data.get("U_SIPM_MEAS1"))
    return timestamp_slave, u_sipm_slave

if __name__ == "__main__":
    timestamp_slave, u_sipm_slave = read_file("log_18.json")
    fig, ax = plt.subplots()
    ax.plot(timestamp_slave, u_sipm_slave)
    ax.set_ylim(55.0, 55.25)
    ax.set_xlim(left=500000)
    # ax.set(xlabel='time (ms)', ylabel='U_SIPM_MEAS1 (V)',
    #        title='U_SIPM_MEAS1 vs time'
    # )
    plt.show()

