import pandas

from borneo.parameters import filter_for_func


class AnalysisError(Exception):
    """Custom model error to handle errors in the analysis"""
    pass


class Analysis(object):
    """Generic wrapper class for a chain of analysis computations"""

    def __init__(self, model, **kwargs):
        """Class constructor"""
        self.model = model
        self.measurements = []
        self.results = pandas.Series()

        for key, value in kwargs.items():
            setattr(self, key, value)

    def add_measurement(self, tag, function):
        """Add a measurement function to the analysis"""
        self.measurements.append((tag, function))

    def run(self, data, param_set):
        """Run the analysis"""
        self.results = pandas.Series()
        last_result = data

        for tag, measurement in self.measurements:
            meas_params = filter_for_func(measurement, param_set)
            last_result = measurement(self, last_result, **meas_params)
            setattr(self, tag, last_result)
        return last_result

    def run_resample(self, centre, samples, error_func, centre_params,
                     sample_params=None):
        """Run the analysis for a set of resampled data, computing the error
        using the supplied error function and passing it to subsequent
        measurements"""

        last_centre_result = pandas.Series()
        last_sample_results = [pandas.Series() for sample in samples]
        sample_params = sample_params or [centre_params] * len(samples)
        last_tag = None
        centre_results = dict([(tag, pandas.Series())
                               for tag, meas in self.measurements])
        sample_results = dict([(tag, []) for tag, meas in self.measurements])

        for tag, measurement in self.measurements:
            error = error_func(last_sample_results)
            self.results = last_centre_result
            centre_params['error'] = error
            meas_params = filter_for_func(measurement, centre_params)
            if last_tag:
                setattr(self, last_tag, centre_results[last_tag])
            centre_results[tag] = measurement(self, centre, **meas_params)
            last_centre_result = self.results.copy()

            it = enumerate(zip(sample_params, samples, last_sample_results))
            for i, (params, sample, last_result) in it:
                self.results = last_result
                params['error'] = error
                meas_params = filter_for_func(measurement, params)
                if last_tag:
                    setattr(self, last_tag, sample_results[last_tag][i])
                result = measurement(self, sample, **meas_params)
                sample_results[tag].append(result)
                last_sample_results[i] = self.results.copy()

            last_tag = tag

        return (last_centre_result, last_sample_results,
                error_func(last_sample_results))