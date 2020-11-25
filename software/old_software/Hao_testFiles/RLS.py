import numpy as np
import matplotlib.pylab as plt
import padasip as pa


# these two function supplement your online measurment
def measure_x():
    # it produces input vector of size 3
    x = np.random.random(3)
    return x


def measure_d(x):
    # meausure system output
    d = 2 * x[0] + 1 * x[1] - 1.5 * x[2]
    return d


N = 100
log_d = np.zeros(N)
log_y = np.zeros(N)
filt = pa.filters.FilterRLS(3, mu=0.5)
for k in range(N):
    # measure input
    x = measure_x()
    # predict new value
    y = filt.predict(x)
    # do the important stuff with prediction output
    pass
    # measure output
    d = measure_d(x)
    # update filter
    filt.adapt(d, x)
    # log values
    log_d[k] = d
    log_y[k] = y

### show results
plt.figure(figsize=(15, 9))
plt.subplot(211);
plt.title("Adaptation");
plt.xlabel("samples - k")
plt.plot(log_d, "b", label="d - target")
plt.plot(log_y, "g", label="y - output");
plt.legend()
plt.subplot(212);
plt.title("Filter error");
plt.xlabel("samples - k")
plt.plot(10 * np.log10((log_d - log_y) ** 2), "r", label="e - error [dB]")
plt.legend();
plt.tight_layout();
plt.show()

# class padasip.filters.rls.FilterRLS(n, mu=0.99, eps=0.1, w='random')
# Bases: padasip.filters.base_filter.AdaptiveFilter
#
# Adaptive RLS filter.
#
# Args:
#
# n : length of filter (integer) - how many input is input array (row of input matrix)
# Kwargs:
#
# mu : forgetting factor (float). It is introduced to give exponentially less weight to older error samples. It is usually chosen between 0.98 and 1.
#
# eps : initialisation value (float). It is usually chosen between 0.1 and 1.
#
# w : initial weights of filter. Possible values are:
#
# array with initial weights (1 dimensional array) of filter size
# “random” : create random weights
# “zeros” : create zero value weights
# adapt(d, x)[source]
# Adapt weights according one desired value and its input.
#
# Args:
#
# d : desired value (float)
# x : input array (1-dimensional array)
# run(d, x)[source]
# This function filters multiple samples in a row.
#
# Args:
#
# d : desired value (1 dimensional array)
#
# x
# : input matrix (2-dimensional array). Rows are samples,
# columns are input arrays.
#
# Returns:
#
# y : output value (1 dimensional array). The size corresponds with the desired value.
# e : filter error for every sample (1 dimensional array). The size corresponds with the desired value.
# w : history of all weights (2 dimensional array). Every row is set of the weights for given sample.