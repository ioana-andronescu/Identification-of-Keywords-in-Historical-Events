'''
    Peak Detection based on the level difference in the time series.
'''

class LevelPeakDetector():

    def __init__(self, series):
        self.series     = series
        self.max_range  = 509

    def function_1(self, max_peak, min_initial, min_final):
        return 2 * max_peak - min_final - min_initial

    def function_2(self, max_peak, min_initial, min_final):
        level_diff = 2 * max_peak - min_final - min_initial
        return level_diff / 2 * (max_peak - min(min_final, min_initial))

    # not used, doesn't work as expected
    def function_3(self, max_peak, min_initial, min_final, factor):
        level_diff = 2 * max_peak - min_final - min_initial
        return level_diff / factor

    # get peak values
    def get_levels(self, function_type):
        levels = {}

        min_global = min(self.series)
        max_global = max(self.series)
        factor = 2 * (max_global - min_global)

        t = 1
        while t < self.max_range:
            # initial minimum (before peak)
            min_initial = self.series[t - 1]
            # final minimum (after peak)
            min_final   = 0.0
            # local maximum (peak)
            max_peak    = self.series[t - 1]

            levels[t] = 0.0

            ascending   = False
            descending  = False

            i = t
            while self.series[i] > self.series[i - 1]:
                i += 1
                if i >= self.max_range:
                    break
                ascending = True
            if ascending:
                max_peak = self.series[i - 1]

            if i == self.max_range:
                for k in xrange(t, i):
                    levels[k] = 0.0
                break

            while self.series[i] < self.series[i - 1]:
                i += 1
                if i >= self.max_range:
                    break
                descending = True
            if descending:
                min_final = self.series[i - 1]

            if function_type == 1:
                level = self.function_1(max_peak, min_initial, min_final)
            elif function_type == 2:
                level = self.function_2(max_peak, min_initial, min_final)

            for k in xrange(t, i - 1):
                levels[k] = level

            # peak => last index after decrease
            t = i
            # not a peak => increment
            if ascending is False and descending is False:
                t += 1

            # last value in the time series
            if t == self.max_range:
                levels[t] = 0.0

        return levels