import numpy as np
import pandas

from borneo.analysis import Analysis


def some_measurement(analysis, data):
    result = data / 2
    analysis.results['x'] = result
    return result


def another_measurement(analysis, data):
    result = analysis.some_tag**2
    analysis.results['y'] = result
    return result


class TestAnalysis(object):

    def test_init(self):
        """Test constructor"""
        model = lambda x: x
        analysis = Analysis(model, x=1, y=2)
        assert type(analysis.results) == pandas.Series
        assert analysis.measurements == []
        assert analysis.x == 1
        assert analysis.y == 2
        assert analysis.model == model

    def test_add_measurement(self):
        """Test add_measurement"""
        analysis = Analysis("blah")
        measurement = lambda x: x
        analysis.add_measurement("some_tag", measurement)
        assert analysis.measurements == [("some_tag", measurement)]

    def test_run(self):
        """Test run"""
        analysis = Analysis("blah")
        analysis.add_measurement('some_tag', some_measurement)
        analysis.add_measurement("another_tag", another_measurement)
        result = analysis.run(1.0, {})
        assert result == 0.25
        assert analysis.some_tag == 0.5
        assert analysis.another_tag == 0.25
        assert analysis.results['x'] == 0.5
        assert analysis.results['y'] == 0.25

    def test_run_resample(self):
        """Test run_resample"""
        analysis = Analysis("blah")
        analysis.add_measurement('some_tag', some_measurement)
        analysis.add_measurement('another_tag', another_measurement)
        samples = np.arange(10, dtype=float)
        centre, results, error = analysis.run_resample(1.0, samples, np.std, {})
        assert centre.x == 0.5
        assert centre.y == 0.25
        xs = np.array([result.x for result in results])
        ys = np.array([result.y for result in results])
        assert np.allclose(xs, samples / 2)
        assert np.allclose(ys, samples**2 / 4)