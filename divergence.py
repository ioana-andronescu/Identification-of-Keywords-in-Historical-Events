import math

'''
    Kullback-Leibler divergence for initial distribution and approximate distribution (after applying peak detection algorithms)
'''

class KullbackLeibler():

    def __init__(self, expected, model):
        self.expected   = expected
        self.model      = model
        self.max_range  = 509
        self.relevance  = 11

    def compute_divergence(self):
        p_expected  = {k: 0 for k in range(self.relevance)}
        p_model     = {k: 0 for k in range(self.relevance)}
        for t in range(self.max_range):
            p_expected[self.expected[t]] += 1
            p_model[self.model[t]] += 1

        for x in range(self.relevance):
            p_expected[x] = float(p_expected[x]) / self.max_range
            p_model[x] = float(p_model[x]) / self.max_range

        sum_probability = 0.0
        for x in range(self.relevance):
            if p_model[x] == 0 or p_expected[x] == 0:
                sum_probability += 0
            else:
                p = p_expected[x] / p_model[x]
                sum_probability += p_expected[x] * math.log(p)
        if sum_probability > 1:
            sum_probability = 1.0
        return (1.0 - sum_probability) * 100.0