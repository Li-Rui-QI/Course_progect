from scipy import signal
import numpy as np
import os
import matplotlib.pyplot as plt
import ripper
import sys



stage = 0
current_dir = os.path.dirname(os.path.abspath(__file__))
output_dir = os.path.join(current_dir, "output", "sawtooth_frequency")

pyglobus_dir = os.path.join(current_dir, "pyglobus", "python")

sys.path.append(pyglobus_dir)
try:
    import pyglobus
except ImportError as e:
    print("Cannot import pyglobus from %s, exiting" % pyglobus_dir)
    sys.exit(1)



DATA_FILE = 0
SENSOR_NUMBER = 0
HIGH_PASS_CUTOFF = 250
LOW_PASS_CUTOFF = 2000
MOVING_AVERAGE_WINDOW_SIZE = 5

#
# NEEDED FUCTIONS 
#

# Plotting sample_data and saving it to PNG file
def plot(x, y, label_x, label_y, color="k", new_fig=True, flush=True):
    global stage

    if new_fig:
        plt.figure(figsize=(15, 10))

    plt.plot(x, y, color)
    plt.xlabel(label_x, fontsize=25)
    plt.ylabel(label_y, fontsize=25)

    if flush:
        out = os.path.join(output_dir, "#%i.png" % stage)
        plt.savefig(out)

        print("Stage %i result:" % stage, out)

        stage += 1


# Applies Butterworth filter
def butter_filter(input_, cutoff, fs, btype, order=5):
    b, a = signal.butter(order, cutoff / (0.5 * fs), btype=btype, analog=False)
    return signal.filtfilt(b, a, input_)


# Applies moving average window
def moving_average(x, w):
    return np.convolve(x, np.ones(w), "valid") / w

# Enter the needed values to start algoritm
def init_data_():
    SHT_NUMBER_ARRAY = [38933, 38934, 38935, 38936, 38937 ,38938]
    name_detectors = [15,27,50,80]
    SigROI  = [18, 19,20, 26, 55 ]

    print("Enter the number of experiment: \n")

    for i in range(len(SHT_NUMBER_ARRAY)):
        print(SHT_NUMBER_ARRAY[i])

    print("\n")
    
    global DATA_FILE
    DATA_FILE = int(input())

    c = False
    for i in range(len(SHT_NUMBER_ARRAY)):
        if DATA_FILE == SHT_NUMBER_ARRAY[i]:
            c = True
            break;

    if c != True:
        print("Bad input!")
        exit(1)

    os.system('cls')

    print("Enter the number of SXR Detector: ")

    # for i in range(len(SHT_NUMBER_ARRAY)):
    #     print("SXR ", SHT_NUMBER_ARRAY[i])
    for i in range(len(name_detectors)):
        print("SXR ", name_detectors[i], " mkm")
    
    print("\n")

    global SENSOR_NUMBER
    SENSOR_NUMBER = int(input())

    os.system('cls')

    d = False
    # for i in range(len(SHT_NUMBER_ARRAY)):
    #     if SENSOR_NUMBER == SHT_NUMBER_ARRAY[i]:
    #         d = True
    #         SENSOR_NUMBER = SigROI[i];
    #         break;
    for i in range(len(name_detectors)):
        if SENSOR_NUMBER == name_detectors[i]:
            d = True
            SENSOR_NUMBER = SigROI[i];
            break;

    if d != True:
        print("Bad input!")
        exit(1)



if __name__ == "__main__":
    font = {"size": 22}

    plt.rc("font", **font)

    os.makedirs(output_dir, exist_ok=True)

    print("Stage %i" % stage)

    init_data_()

    data_all = ripper.extract('sample_data', DATA_FILE, [SENSOR_NUMBER])

    c,d = ripper.x_y(data_all[0][SENSOR_NUMBER])

    data = np.array([np.array(c),np.array(d)])

    print("Loaded %s" % DATA_FILE)

    roi = (60000, 90000)
    x = data[0, roi[0]:roi[1]]
    y = data[1, roi[0]:roi[1]]

    plot(data[0], data[1], "Время, с", "U, В")

    print("Stage %i: High pass filtering" % stage)


    sample_rate = 1.0 / (x[1] - x[0])

    y = butter_filter(y, HIGH_PASS_CUTOFF, sample_rate, btype="high")
    plot(x, y, "Время, с", "U, В")

    print("Stage %i: Low pass filtering" % stage)


    y = butter_filter(y, LOW_PASS_CUTOFF, sample_rate, btype="low")

    plot(x, y, "Время, с", "U, В")

    print("Stage %i: Finding zero crossings" % stage)

    zero_crossings = np.where(np.diff(np.sign(y)))[0]

    plot(x, y, "Время, с", "U, В", flush=False)
    plot(x[zero_crossings], y[zero_crossings], "Время, с", "U, В", color="rx", new_fig=False)

    print("Stage %i: Computing frequencies" % stage)

    freqs = []

    for i in range(len(zero_crossings) - 2):
        freqs.append(1 / (x[zero_crossings[i + 2]] - x[zero_crossings[i]]))

    x = x[zero_crossings][:-(MOVING_AVERAGE_WINDOW_SIZE + 1)]
    y = moving_average(freqs, MOVING_AVERAGE_WINDOW_SIZE)

    plot(x, y, "Время, с", "Частота, Гц", color="ko-")
