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

    data_coord = np.array(data_coord)
    data_value = np.array(data_value)

    plt = pg.plot()
    plt.resize(1000, 1000)
    dmin, dmax = data_value.min(), data_value.max()
    cmap = pg.ColorMap(
        pos=np.linspace(dmin, dmax, 4),
        color=np.array([[0, 0, 0], [255, 0, 0], [255, 255, 0], [255, 255, 255]])
    )

    colors = [pg.mkBrush(cmap.map(x)) for x in data_value]
    scatter = plt.plot(data_coord[:,0], data_coord[:,1], symbolBrush=colors, symbolPen=0.3, pen=None, symbol='o', symbolSize=3)


    x_bounds = min(long_west, long_east), max(long_west, long_east)
    y_bounds = lat_bottom, lat_top

    x_range = int(min(abs(long_east-long_west), abs(long_west-long_east)) * (10**rnd) +1)
    y_range = int((lat_top - lat_bottom) * (10**rnd) + 1)

    print('x_range = ', x_range, ' : y_range = ', y_range)

    img_coords = np.zeros((y_range, x_range, 2))
    img_coords[:, :, 0] = np.linspace(x_bounds[0], x_bounds[1], x_range)[None, :]
    img_coords[:, :, 1] = np.linspace(y_bounds[0], y_bounds[1], y_range)[:, None]


    interp = LinearNDInterpolator(data_coord, data_value)
    image = interp(img_coords)    

    img = pg.ImageItem(image.T)
    plt.addItem(img)
    brect = pg.QtCore.QRectF(x_bounds[0], y_bounds[0], x_bounds[1]-x_bounds[0], y_bounds[1]-y_bounds[0])
    img.setRect(brect)
    img.setZValue(-10)

    label = pg.TextItem()
    label.setParentItem(plt.plotItem.vb)

    def mouseHover(pos):
        pos = plt.plotItem.vb.mapSceneToView(pos)
        label.setText('%0.2f %0.2f %0.2f' % (pos.x(), pos.y(), interp([pos.x(), pos.y()])))

    plt.scene().sigMouseMoved.connect(mouseHover)

    # if __name__ == '__main__':
    #     pg.image(image)


class Pixel:
    def __init__(self, data):
        print('---   ', data)
        self.data = data
        self.vars = data.split(',')

        self.long_w = float(self.vars[0])
        self.lat = float(self.vars[1])
        self.topo = float(self.vars[2])



