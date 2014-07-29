import matplotlib.pyplot as plt
import pylab

class Plotter():

    def __init__(self, x0, y0, period):
        self.x0         = x0
        self.y0         = y0
        self.x_limit    = [1500, 2008]
        self.y_limit    = [0, 11]
        self.period     = period
        self.colors     = ['#3399CC', '#FF6600', '#FF3333', '#339933', '#FFCC00', '#CC3366']

    def plot_single(self, word, y):
        plt.figure(figsize=(10, 6), dpi=80)
        plt.subplot(211)
        plt.plot(self.x0, y, color='#339933', linestyle='-', linewidth=1.8, label=word)
        pylab.xlim(self.x_limit)
        pylab.xticks([x for x in xrange(self.x_limit[0], self.x_limit[1], 50)])
        pylab.ylim(self.y_limit)
        pylab.yticks([y for y in xrange(0, 11, 2)])
        plt.legend(loc='upper right')
        plt.grid(True)

        plt.subplot(212)
        plt.plot(self.x0, self.y0, color='#003366', linestyle='-', linewidth=1.8, label=word)
        pylab.xlim(self.x_limit)
        pylab.xticks([x for x in xrange(self.x_limit[0], self.x_limit[1], 50)])
        pylab.ylim([0, max(self.y0) + 0.1 * max(self.y0)])
        plt.legend(loc='upper right')
        plt.grid(True)

        plt.show()

    def plot_peaks(self, word, y, y_label):
        plt.figure(figsize=(10, 6), dpi=80)
        plt.title('Peaks for ' + word)
        plt.subplot(211)
        plt.plot(self.x0, y, color=self.colors[1], linestyle='-', linewidth=1.8, label=y_label)
        #plt.plot(self.x0, self.y0, color=self.colors[0], linestyle='-', linewidth=1.2, label='Original Series')
        pylab.xlim(self.period)
        pylab.xticks([x for x in xrange(self.period[0], self.period[1], 50)])
        pylab.ylim(self.y_limit)
        pylab.yticks([y for y in xrange(0, 11, 2)])
        plt.legend(loc='upper right')
        plt.xlabel('Year')
        plt.ylabel('Relevance')
        plt.grid(True)

        plt.subplot(212)
        plt.plot(self.x0, self.y0, color=self.colors[0], linestyle='-', linewidth=1.8, label='original series')
        pylab.xlim(self.period)
        pylab.xticks([x for x in xrange(self.period[0], self.period[1], 50)])
        pylab.ylim([0, max(self.y0) + 0.1 * max(self.y0)])
        #pylab.yticks([y for y in xrange(0, 11, 2)])
        plt.legend(loc='upper right')
        plt.xlabel('Year')
        plt.ylabel('Frequency')
        plt.grid(True)

        plt.show()

    def plot_multiple_peaks(self, word, y, period):
        plt.figure(figsize=(10, 6), dpi=80)
        plt.title('Peak for ' + word)
        plt.subplot(211)
        plt.title('Peak for ' + word)
        plt.plot(self.x0, y[0], color=self.colors[0], linestyle='-', linewidth=1.8, label='level 1')
        plt.plot(self.x0, y[1], color=self.colors[1], linestyle='-', linewidth=1.8, label='level 2')
        plt.plot(self.x0, y[2], color=self.colors[2], linestyle='-', linewidth=1.8, label='sliding window 1')
        plt.plot(self.x0, y[3], color=self.colors[3], linestyle='-', linewidth=1.8, label='sliding window 2')
        plt.plot(self.x0, y[4], color=self.colors[4], linestyle='-', linewidth=1.8, label='sliding window 3')
        plt.plot(self.x0, y[5], color=self.colors[5], linestyle='-', linewidth=1.8, label='double change')
        pylab.xlim(self.period)
        pylab.xticks([x for x in xrange(self.period[0], self.period[1], 10)])
        pylab.ylim(self.y_limit)
        pylab.yticks([y for y in xrange(0, 11, 2)])
        plt.legend(loc='upper right')
        plt.xlabel('Year')
        plt.ylabel('Historical Relevance')
        plt.grid(True)

        plt.subplot(212)
        plt.plot(self.x0, self.y0, color=self.colors[0], linestyle='-', linewidth=1.8, label='original series')
        pylab.xlim(self.period)
        pylab.xticks([x for x in xrange(self.period[0], self.period[1], 20)])
        pylab.ylim([0, max(self.y0) + 0.1 * max(self.y0)])
        plt.legend(loc='upper right')
        plt.xlabel('Year')
        plt.ylabel('Frequency')
        plt.grid(True)

        plt.show()

    def plot_keywords(self, event, words, y):
        plt.figure(figsize=(10, 6), dpi=80)
        plt.title('Keywords for ' + event)
        plt.plot(self.x0, y[0], color=self.colors[0], linestyle='-', linewidth=1.8, label=words[0])
        plt.plot(self.x0, y[1], color=self.colors[1], linestyle='-', linewidth=1.8, label=words[1])
        plt.plot(self.x0, y[2], color=self.colors[2], linestyle='-', linewidth=1.8, label=words[2])
        plt.plot(self.x0, y[3], color=self.colors[3], linestyle='-', linewidth=1.8, label=words[3])
        plt.plot(self.x0, y[4], color=self.colors[4], linestyle='-', linewidth=1.8, label=words[4])
        pylab.xlim(self.period)
        pylab.xticks([x for x in xrange(self.period[0], self.period[1], 2)])
        plt.legend(loc='upper right')
        plt.xlabel('Year')
        plt.ylabel('Frequency')
        plt.grid(True)
        plt.show()

    def plot_multiple_level(self, word, y):
        plt.figure(figsize=(10, 6), dpi=80)
        plt.plot(self.x0, y[0], color=self.colors[0], linestyle='-', linewidth=1.8, label='Level Function 1')
        plt.plot(self.x0, y[1], color=self.colors[1], linestyle='-', linewidth=1.8, label='Level Function 2')
        plt.plot(self.x0, self.y0, color=self.colors[-1], linestyle='-', linewidth=1.8, label='Original Peaks')
        pylab.xlim([1750, 2000])
        pylab.xticks([x for x in xrange(1750, 2000, 50)])
        pylab.ylim(self.y_limit)
        pylab.yticks([y for y in xrange(0, 11, 2)])
        plt.legend(loc='upper right')
        plt.grid(True)
        plt.show()

    def plot_multiple_window(self, word, y):
        plt.figure(figsize=(10, 6), dpi=80)
        plt.plot(self.x0, y[0], color=self.colors[0], linestyle='-', linewidth=1.8, label='Window Function 1')
        plt.plot(self.x0, y[1], color=self.colors[1], linestyle='-', linewidth=1.8, label='Window Function 2')
        plt.plot(self.x0, y[2], color=self.colors[2], linestyle='-', linewidth=1.8, label='Window Function 2')
        plt.plot(self.x0, self.y0, color=self.colors[-1], linestyle='-', linewidth=1.8, label='Original Peaks')
        pylab.xlim(self.x_limit)
        pylab.xticks([x for x in xrange(self.x_limit[0], self.x_limit[1], 50)])
        pylab.ylim(self.y_limit)
        pylab.yticks([y for y in xrange(0, 11, 2)])
        plt.legend(loc='upper right')
        plt.grid(True)
        plt.show()

    def plot_multiple_double(self, word, y):
        plt.figure(figsize=(10, 6), dpi=80)
        plt.plot(self.x0, y, color=self.colors[0], linestyle='-', linewidth=1.8, label='Double Change')
        plt.plot(self.x0, self.y0, color=self.colors[-1], linestyle='-', linewidth=1.8, label='Original Peaks')
        pylab.xlim(self.x_limit)
        pylab.xticks([x for x in xrange(self.x_limit[0], self.x_limit[1], 50)])
        pylab.ylim(self.y_limit)
        pylab.yticks([y for y in xrange(0, 11, 2)])
        plt.legend(loc='upper right')
        plt.grid(True)
        plt.show()