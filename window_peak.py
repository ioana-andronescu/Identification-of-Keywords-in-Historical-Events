import math

'''
    Peak Detection based on sliding window.
'''

class WindowPeakDetector:

    def __init__(self, series):
        self.series         = series
        self.max_range      = 509
        self.window_size    = 31
        self.threshold      = 0.1
        self.w              = 5

    def kernel_gauss(self, value):
        return (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * (value ** 2))

    def compute_pdf(self, t, k, contains_value):
        size = 2 * self.window_size
        n = t
        if contains_value:
            size += 1
        else:
            n = n - 1
        parzen_window = math.sqrt((self.series[n + k] - self.series[n + k + self.w]) ** 2 + self.w ** 2)
        factor = 1 / (size * parzen_window)

        sum_kernel = 0.0
        for i in xrange(1, self.window_size + 1):
            value_left  = (self.series[t + k] - self.series[t - i]) / parzen_window
            value_right = (self.series[t + k] - self.series[t + i]) / parzen_window
            sum_kernel += self.kernel_gauss(value_left) + self.kernel_gauss(value_right)
        if contains_value:
            sum_kernel += self.kernel_gauss(0.0)
        return factor * sum_kernel

    def peak_function_1(self, t):
        sum_left    = sum(self.series[t] - x for x in self.series[(t - self.window_size):t]) / self.window_size
        sum_right   = sum(self.series[t] - x for x in self.series[(t + 1):(t + self.window_size + 1)]) / self.window_size
        return (sum_left + sum_right) / 2

    def peak_function_2(self, t):
        sum_left    = self.series[t] - sum(self.series[(t - self.window_size):t]) / self.window_size
        sum_right   = self.series[t] - sum(self.series[(t + 1):(t + self.window_size + 1)]) / self.window_size
        return (sum_left + sum_right) / 2

    def peak_function_3(self, t):
        left    = max(self.series[t] - x for x in self.series[(t - self.window_size):t])
        right   = max(self.series[t] - x for x in self.series[(t + 1):(t + self.window_size + 1)])
        return (left + right) / 2

    def peak_function_4(self, t, contains_value):
        entropy = 0.0
        for k in xrange(1, self.window_size + 1):
            pdf_left = self.compute_pdf(t, -k, contains_value)
            pdf_right = self.compute_pdf(t, k, contains_value)
            entropy -= (pdf_left * math.log(pdf_left, 2) + pdf_right * math.log(pdf_right, 2))
        if contains_value:
            pdf = self.compute_pdf(t, 0, contains_value)
            entropy -= pdf * math.log(pdf, 2)
        return entropy

    # get the peaks for the time series
    def compute_peaks(self, function_type):
        peaks = {}
        results = {}
        for t in xrange(self.window_size + self.w, self.max_range - self.window_size - self.w):
            if function_type < 4:
                if function_type == 1:
                    diff = self.peak_function_1(t)
                elif function_type == 2:
                    diff = self.peak_function_2(t)
                else:
                    diff = self.peak_function_3(t)
                # peaks have positive values
                if diff >= 0:
                    results[t] = diff
            # not used - doesn't work as expected
            elif function_type == 4:
                diff = self.peak_function_4(t, False) - self.peak_function_4(t, True)
                if diff < 0:
                    results[t] = diff

        if len(results) == 0:
            return {}

        # filter the peaks
        mean = sum(results.values()) / len(results)
        variance = sum([(r - mean) ** 2 for r in results.values()]) / len(results)
        std = math.sqrt(variance)

        for t in results:
            if results[t] - mean > self.threshold * std:
                peaks[t] = results[t]

        # remove one peak very close (inside the same window) to another peak
        results = peaks
        peaks = {}
        for t1 in results:
            for t2 in results:
                if t1 != t2:
                    if math.fabs(t1 - t2) > self.window_size:
                        peaks[t1] = results[t1]
                        peaks[t2] = results[t2]
                    else:
                        if results[t1] > results[t2]:
                            peaks[t1] = results[t1]
                            if t2 in peaks:
                                peaks.pop(t2)
                        else:
                            peaks[t2] = results[t2]
                            if t1 in peaks:
                                peaks.pop(t1)
        return peaks