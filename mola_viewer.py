import os
import numpy as np
import pyqtgraph as pg
from scipy.interpolate import LinearNDInterpolator


def file_data(path):
    if os.path.isfile(path):
        f = open(path)
        return f.read()


def run(lat_top=-37.5, lat_bottom=-38.25, long_west=87.5, long_east=88.25, filename='PEDR_test_2.csv', rnd=4):
    data_coord = []
    data_value = []

    data = file_data(filename)
    lines = data.split('\n')
    lines.pop(0)

    for line in lines:
        if ',' in line:
            p = Pixel(line)

            data_coord.append([p.long_w, p.lat])
            data_value.append(p.topo)
        else:
            continue

    x_bounds = min(long_west, long_east), max(long_west, long_east)
    y_bounds = lat_bottom, lat_top

    x_range = int(abs((long_east+360) - (long_west+360)) % 360)
    #x_range = int(max(long_east, long_west) - min(long_east, long_west)) * (10**rnd) + 1)
    y_range = int((lat_top - lat_bottom) * (10**rnd) + 1)

    img_coords = np.zeros((y_range, x_range, 2))
    img_coords[:, :, 0] = np.linspace(x_bounds[0], x_bounds[1], x_range)[None, :]
    img_coords[:, :, 1] = np.linspace(y_bounds[0], y_bounds[1], y_range)[:, None]


    interp = LinearNDInterpolator(data_coord, data_value)
    image = interp(img_coords)    

    if __name__ == '__main__':
        pg.image(image)


class Pixel:
    def __init__(self, data):
        print('---   ', data)
        self.data = data
        self.vars = data.split(',')

        self.long_w = float(self.vars[0])
        self.lat = float(self.vars[1])
        self.topo = float(self.vars[2])



