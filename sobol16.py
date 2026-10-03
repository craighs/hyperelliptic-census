import scipy.stats.qmc as qmc
import numpy as np
import math
sobol_gen = qmc.Sobol(d = 8)
n_points = 2**17
points = sobol_gen.random(n_points)*16
points = points // 1
points = points.astype(int)
with open ('16.txt','w') as f:
	for row in points:
		line = ' '.join(map(str,row))
		f.write(line+'\n')

