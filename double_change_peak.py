'''
    Peak Detection based on a double change (double increase or double decrease of the time series)
'''

class DoubleChangePeakDetector():

    def __init__(self, series):
        self.series     = series
        self.max_range  = 509

    def compute_relevance(self, ratio):
        counts = [0 for _ in range(len(self.series))]
        for t in xrange(1, self.max_range - 1):
            a = self.series[t - 1]
            b = self.series[t]
            c = self.series[t + 1]

            if a >= 0 and b >= 0.000001 and c >= 0:
                # count the relevance from 0 to 10
                count = 0
                while count <= 9:
                    sup_ratio = 1.0 + ratio * (count + 1)
                    inf_ratio = 1.0 - ratio * (count + 1)
                    if ((b > sup_ratio * a and c > sup_ratio * b) or
                        (b < inf_ratio * a and c < inf_ratio * b)):
                        count += 1
                    else:
                        break
                counts[t] = count
        return counts