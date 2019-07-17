import numpy as np
import pandas as pd
import scipy.stats

class Metrics:

    def __init__(self, timestamps, aggregation_duration, window_overlap):

        # if aggregation_duration == 'day':
        #     duration = 86400
        # elif aggregation_duration == 'hour':
        #     duration = 3600
        # elif aggregation_duration == 'minute':
        #     duration = 60
        # elif aggregation_duration == 'second':
        #     duration = 1

        sampling_frequency = self.establish_sampling_frequency(timestamps)

        indexing = aggregation_duration/np.floor(sampling_frequency)

        if (indexing % 2) != 0:
            indexing = np.ceil(indexing)

        self.window_length = int(indexing)
        self.current_position = 0
        self.window_overlap = window_overlap

    @staticmethod
    def average_labels_per_window(labels, timestamps):
        """Return the average label proportion per window."""
        unique_lab, counts_lab = np.unique(labels, return_counts=True)

        number_of_instances = len(labels)
        number_of_labels = len(unique_lab)

        label_occurrence_array = np.zeros((number_of_labels, 2))

        for idx, (lab, count) in enumerate(zip(unique_lab, counts_lab)):
            prop = count / number_of_instances
            label_occurrence_array[idx, 0] = int(lab)
            label_occurrence_array[idx, 1] = prop

        return label_occurrence_array

    @staticmethod
    def duration_of_labels_per_window(labels, timestamps):
        """Return the average duration of a label per window."""
        unique_lab, counts_lab = np.unique(labels, return_counts=True)

        number_of_instances = len(labels)
        number_of_labels = len(unique_lab)
        timestamps = np.array(timestamps)
        total_time_in_window = timestamps[-1] - timestamps[0]

        label_time_array = np.zeros((number_of_labels, 2))

        for idx, (lab, count) in enumerate(zip(unique_lab, counts_lab)):

            prop = count / number_of_instances
            time_prop = prop * total_time_in_window
            label_time_array[idx, 0] = int(lab)
            label_time_array[idx, 1] = time_prop

        return label_time_array

    @staticmethod
    def number_of_label_changes_per_window(labels, timestamps):
        """Return a confusion matrix of the number of label changes in a window."""
        unique_lab, counts_lab = np.unique(labels, return_counts=True)
        labels_ = np.array(labels)

        label_change_array = np.zeros((len(unique_lab), len(unique_lab)))

        for idx in range(1, len(labels_)):
            label_change_array[int(np.where(unique_lab == labels_[idx-1])[0][0]), int(np.where(unique_lab == labels_[idx])[0][0])] += 1

        return label_change_array

    @staticmethod
    def speed(labels, timestamps, adjacency):
        """Return approximate speed of a person given the timestamps and the rate of change of labels, given their distance."""
        unique_lab, counts_lab = np.unique(labels, return_counts=True)
        labels_ = np.array(labels)
        adjacency = np.array(adjacency)
        timestamps = np.array(timestamps)

        label_change_array = np.zeros(len(labels))
        label_time_array = np.zeros(len(labels))

        for idx in range(1, len(labels_)):
            label_change_array[idx] += adjacency[int(np.where(unique_lab == labels_[idx-1])[0][0]), int(np.where(unique_lab == labels_[idx])[0][0])]
            label_time_array[idx] += timestamps[idx - 1] - timestamps[idx]

        distances = np.divide(label_change_array, label_time_array)
        speed = np.abs(np.nanmean(distances))

        return speed

    @staticmethod
    def average_time_between_labels(labels, timestamps, normalise=True):
        """Return the average time, in seconds, between labels in a window."""
        # normalise parameter attempts to remove sequential labels
        # assuming a finite set of ordinal labels
        unique_lab, counts_lab = np.unique(labels, return_counts=True)

        timestamps_ = np.array(timestamps)
        sampling_frequency = 0
        for idx in range(1, len(timestamps_)):
            if (timestamps_[idx] - timestamps_[idx - 1]) < 100:
                sampling_frequency = sampling_frequency + (timestamps_[idx] - timestamps_[idx - 1])

        sampling_frequency = sampling_frequency / len(timestamps_)

        sampling_frequency = 1 / sampling_frequency

        number_of_instances = len(labels)
        labels_ = np.array(labels)
        number_of_labels = len(unique_lab)

        inter_label_times = []

        average_per_label = np.zeros((number_of_labels, 1))

        for idx_outer in range(number_of_labels):
            lab_instance_outer = labels_[idx_outer]
            for idx in range(number_of_instances):
                if (labels_[idx] == lab_instance_outer).any():
                    inter_label_times.append(np.squeeze(timestamps_[idx]))

            inter_label_times = np.diff(inter_label_times)

            if normalise:
                deletion_array = []
                for idx, time in enumerate(inter_label_times):
                    if np.isclose(time, (1/sampling_frequency)):
                        deletion_array.append(idx)
                inter_label_times = np.delete(inter_label_times, deletion_array)

            if inter_label_times.size == 0:
                average_per_label[idx_outer] = 0
            else:
                average_per_label[idx_outer] = np.mean(inter_label_times)
            inter_label_times = []

        return average_per_label

    def establish_sampling_frequency(self, timestamps):
        """Return the most likely sampling frequency from the timestamps in a time window."""
        timestamps_ = np.array(timestamps)
        sampling_frequency = 0
        for idx in range(1, len(timestamps_)):
            if (timestamps_[idx] - timestamps_[idx - 1]) < 100:
                sampling_frequency = sampling_frequency + (timestamps_[idx] - timestamps_[idx - 1])

        sampling_frequency = sampling_frequency / len(timestamps_)

        sampling_frequency = 1 / sampling_frequency

        return sampling_frequency

    def slide(self, index, update=True):
        """Slide and return the window of data."""
        window = index[self.current_position - self.window_length:self.current_position]
        if len(window) > 0:
            if len(window.shape) > 1:
                window = window[~np.isnan(window).any(axis=1)]
            else:
                window = window[~np.isnan(window)]
        if update:
            self.current_position += self.window_overlap
        return window

    def localisation_metrics(self, labels, timestamps):
        """Outputs typical localisation metrics."""
        # Room Transfers - Daily average
            # Find all timestamps within a time window
        df_time = pd.DataFrame(timestamps)
        #

        # TODO Number of times bathroom visited during the night
        # TODO Number of times kitchen visited during the night

    def activity_metrics(self, labels, timestamps):
        """Outputs typical activity metrics."""
        # Number of times activities undertaken (e.g. cooking / cleaning) - Daily average
        # Walking - Hourly average
        # Sitting - Hourly average
        # Lying - Hourly average
        # walking - Daily average
        # Main Sleep Length - Daily average
        # Total Sleep Length - Daily average