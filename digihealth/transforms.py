"""
transforms.py
====================================
The main transforms are contained within this class.
"""

import numpy as np
import scipy.stats

from sklearn.feature_selection import SelectFromModel
from sklearn.svm import LinearSVC
from sklearn.ensemble import ExtraTreesClassifier
from scipy.signal import butter, filtfilt

class Transforms:
    """
    Transforms class is instantiated in order perform feature extraction/transformations upon given dataset.
    It contains basic extraction functions.

    If you want to add your own extraction function, do it here.
    """

    def __init__(self, window_length, window_overlap):
        self.window_length = window_length
        self.current_position = 0
        self.window_overlap = window_overlap

    @staticmethod
    def zero_crossings(x):
        """
        Return the number of zero crossings.

        Parameters
        ----------
        x
            A window of data.
        """
        sign = [1,0]
        direction = 0
        count_zc = 0
        if x[0] >= 0:
            direction = 1

        for i in range(len(x)):
            if (x[i] >= 0 and direction == 0) or (x[i] < 0 and direction == 1):
                direction = sign[direction]
                count_zc += 1
        return count_zc

    @staticmethod
    def mean_crossings(x):
        """
        Return the number of mean crossings.

        Parameters
        ----------
        x
            A window of data.
        """
        x = x - np.mean(x)
        return Transforms.zero_crossings(x)

    @staticmethod
    def interq(x):
        """
        Return the interquartile range.

        Parameters
        ----------
        x
            A window of data.
        """
        interquartile = scipy.stats.iqr(x)
        return interquartile

    @staticmethod
    def skewn(x):
        """
        Return the skewness.

        Parameters
        ----------
        x
            A window of data.
        """
        skewness = scipy.stats.mstats.skew(x)
        skewness = skewness.data.flatten()[0]
        return skewness

    @staticmethod
    def spec_energy(x):
        """
        Return the spectral energy.

        Parameters
        ----------
        x
            A window of data.
        """
        f = np.fft.fft(x)
        F = abs(f)
        return sum(np.square(F))

    @staticmethod
    def spec_entropy(x):
        """
        Return the spectral entropy.

        Parameters
        ----------
        x
            A window of data.
        """
        f = np.fft.fft(x)
        F = abs(f)
        sumf = sum(F)
        if sumf == 0:
            sumf = 1
        nf = F/sumf
        min_nf = 1
        if (min(nf) != max(nf)) and (min(nf) != 0):
            min_nf = min(m for m in nf if m > 0)

        logf = np.log((nf+min_nf))
        spectral_entropy = -1*sum(nf*logf)
        return spectral_entropy

    @staticmethod
    def p25(x):
        """
        Return the 25th percentile.

        Parameters
        ----------
        x
            A window of data.
        """
        return np.percentile(x, 25)

    @staticmethod
    def p75(x):
        """
        Return the 75th percentile.

        Parameters
        ----------
        x
            A window of data.
        """
        return np.percentile(x, 75)

    @staticmethod
    def kurtosis(x):
        """
        Return the kurtosis.

        Parameters
        ----------
        x
            A window of data.
        """
        return scipy.stats.kurtosis(x, fisher=False, bias=True)
    
    def _butter_lowpass(cutoff, fs, order=5):
        """
        Butterworth low pass filter. Internal function.

        Parameters
        ----------
        cutoff
            Cutoff frequency of the filter.
        fs
            Sampling frequency.
        order
            Order of the filter. Default = 5
        """
        nyq = 0.5 * fs
        normal_cutoff = cutoff / nyq 
        b, a = butter(order, normal_cutoff, btype='low', analog=False)
        return b, a
    
    @staticmethod
    def butter_lowpass_filter(x, cutoff, fs, order=5):
        """
        Wrapper for above Butterworth low pass filter.

        Parameters
        ----------
        x
            Window of data.
        cutoff
            Cutoff frequency of the filter.
        fs
            Sampling frequency.
        order
            Order of the filter. Default = 5
        """
        b, a = _butter_lowpass(cutoff, fs, order=order)
        y = filtfilt(b, a, x)
        return y

    def slide(self, x, update=True):
        """
        Function to keep track of the sliding window, when windowing the data. Internal function.

        Parameters
        ----------
        x
            Window of data.
        update
            Update the current position of the window index.
        """
        window = x[self.current_position-self.window_length:self.current_position]
        if len(window) > 0:
            if len(window.shape) > 1:
                window = window[~np.isnan(window).any(axis=1)]
            else:
                window = window[~np.isnan(window)]
        if update:
            self.current_position += self.window_overlap
        return window

    def feature_selection(self, X, y, method):
        """
        Feature selection

        Parameters
        ----------
        X
            Training data. Used to fit models and establish dominant features.
        y
            Test data. Used to fit models and establish dominant features.
        method
            Method of feature selection. Method 'tree' uses random forest selection. Method 'l1' uses a linear feature selection based on L1-norm.
        """
        if method == 'tree':
            clf = ExtraTreesClassifier(n_estimators=50)
            clf = clf.fit(X, y)
            model = SelectFromModel(clf, prefit=True)
            X_new = model.transform(X)
        elif method == 'l1':
            lsvc = LinearSVC(C=0.01, penalty="l1", dual=False).fit(X, y)
            model = SelectFromModel(lsvc, prefit=True)
            X_new = model.transform(X)

        return X_new