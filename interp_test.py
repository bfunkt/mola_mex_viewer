import pyqtgraph as pg
import numpy as np
from scipy.interpolate import LinearNDInterpolator
import scipy.ndimage


w, h = (100, 100)
measure_coords_2d = np.mgrid[0:w, 0:h].transpose(1, 2, 0)

origin = np.array([30, 275])
transform = np.array([[0.5, 1.3], [-1.7, 0.2]])
measure_coords_2d = (measure_coords_2d[..., None] * transform[None, None, ...]).sum(axis=2) + origin

measure_vals_2d = np.random.normal(size=(w, h)) + 10
measure_vals_2d = scipy.ndimage.gaussian_filter(measure_vals_2d, (2, 2))

measure_coords = measure_coords_2d.reshape(w*h, 2)
measure_vals = measure_vals_2d.reshape(w*h)


plt = pg.plot()
plt.resize(1000, 1000)
colors = [pg.mkBrush(np.clip([(x-10)*250 + 50, (x-10)*250, (x-10)*250 - 50], 0, 255)) for x in measure_vals]
scatter = plt.plot(measure_coords[:,0], measure_coords[:,1], symbolBrush=colors, symbolPen=None, pen=None, symbol='o', symbolSize=3)


x_bounds = -100, 0
y_bounds = 300, 380

img_coords = np.zeros((50, 50, 2))
img_coords[:, :, 0] = np.linspace(x_bounds[0], x_bounds[1], 50)[None, :]
img_coords[:, :, 1] = np.linspace(y_bounds[0], y_bounds[1], 50)[:, None]

interp = LinearNDInterpolator(measure_coords, measure_vals)
img_vals = interp(img_coords)

img = pg.ImageItem(img_vals.T, levels=[8, 15])
plt.addItem(img)
brect = pg.QtCore.QRectF(x_bounds[0], y_bounds[0], x_bounds[1]-x_bounds[0], y_bounds[1]-y_bounds[0])
img.setRect(brect)
img.setZValue(-10)