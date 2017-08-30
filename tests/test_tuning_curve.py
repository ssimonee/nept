import numpy as np
import pytest
from shapely.geometry import Point, LineString
import nept


def test_simple_tc():
    linear = nept.Position(np.linspace(0, 10, 4), np.linspace(0, 3, 4))

    spikes = [nept.SpikeTrain(np.array([0.5]), 'test'),
              nept.SpikeTrain(np.array([1.5]), 'test'),
              nept.SpikeTrain(np.array([2.5]), 'test')]

    tuning = nept.tuning_curve_1d(linear, spikes, binsize=3, gaussian_std=None)

    assert np.allclose(tuning, ([1., 0., 0., 0.], [0., 1., 0., 0.], [0., 0., 1., 0.]))


def test_simple_tc1():
    """Time spent in each bin not the same."""
    linear = nept.Position(np.linspace(0, 9, 4), np.linspace(0, 3, 4))

    spikes = [nept.SpikeTrain(np.array([0.0]), 'test'),
              nept.SpikeTrain(np.array([1.0]), 'test'),
              nept.SpikeTrain(np.array([2.0]), 'test'),
              nept.SpikeTrain(np.array([2.5]), 'test')]

    tuning = nept.tuning_curve_1d(linear, spikes, binsize=3, gaussian_std=None)

    assert np.allclose(tuning, ([1., 0., 0.], [0., 1., 0.], [0., 0., 0.5], [0., 0., 0.5]))


def test_tuning_curve_1d_gaussian():
    linear = nept.Position(np.linspace(0, 9, 4), np.linspace(0, 3, 4))

    spikes = [nept.SpikeTrain(np.array([0.0]), 'test'),
              nept.SpikeTrain(np.array([1.0]), 'test'),
              nept.SpikeTrain(np.array([2.0]), 'test'),
              nept.SpikeTrain(np.array([2.5]), 'test')]

    tuning = nept.tuning_curve_1d(linear, spikes, binsize=3, gaussian_std=1.5)

    assert np.allclose(tuning, ([0.89349302, 0.10650698, 0.],
                                [0.10650698, 0.78698604, 0.10650698],
                                [0., 0.05325349, 0.44674651],
                                [0., 0.05325349, 0.44674651]))


def test_tuning_curve_1d_with_2d_position():
    position = nept.Position(np.hstack([np.array([2, 4, 6, 8])[..., np.newaxis],
                                        np.array([7, 5, 3, 1])[..., np.newaxis]]),
                             np.array([0., 1., 2., 3.]))

    binsize = 2

    spikes = [nept.SpikeTrain(np.array([0., 3., 3., 3.]), 'test')]

    with pytest.raises(ValueError) as excinfo:
        nept.tuning_curve_1d(position, spikes, binsize=binsize)

    assert str(excinfo.value) == 'position must be linear'


def test_binned_position_2d_position():
    position = nept.Position(np.hstack([np.array([2, 4, 6, 8])[..., np.newaxis],
                                        np.array([7, 5, 3, 1])[..., np.newaxis]]),
                             np.array([0., 1., 2., 3.]))
    binsize = 2

    with pytest.raises(ValueError) as excinfo:
        nept.binned_position(position, binsize=binsize)

    assert str(excinfo.value) == 'position must be linear'


def test_linearize():
    t_start = 1
    t_stop = 6

    xy = np.array(([1., 1.], [2., 2.], [3., 3.], [4., 4.], [5., 5.]))
    time = np.array([0., 1., 2., 3., 4.])
    pos = nept.Position(xy, time)

    trajectory = [[0., 0.], [5., 5.], [10., 10.]]
    line = LineString(trajectory)

    zone_start = Point([1., 1.])
    zone_stop = Point([9., 9.])
    expand_by = 1
    zone = nept.expand_line(zone_start, zone_stop, line, expand_by)

    sliced_pos = pos[t_start:t_stop]

    linear = sliced_pos.linearize(line, zone)

    assert np.allclose(linear.x, np.array([2.82842712, 4.24264069, 5.65685425, 7.07106781]))
    assert np.allclose(linear.time, [1, 2, 3, 4])


def test_tuning_curve_2d():
    pos = nept.Position(np.hstack([np.array([2, 4, 6, 8])[..., np.newaxis],
                                  np.array([7, 5, 3, 1])[..., np.newaxis]]),
                        np.array([0., 1., 2., 3.]))

    binsize = 2
    xedges = np.arange(pos.x.min(), pos.x.max()+binsize, binsize)
    yedges = np.arange(pos.y.min(), pos.y.max()+binsize, binsize)

    spikes = [nept.SpikeTrain(np.array([0., 3., 3., 3.]), 'test')]

    tuning_curves = nept.tuning_curve_2d(pos, spikes, xedges, yedges)

    assert np.allclose(tuning_curves, [np.array([[0., 0., 3.], [0., 0., 0.], [1., 0., 0.]])])


def test_tuning_curve_2d_gaussian():
    position = nept.Position(np.hstack([np.array([2, 4, 6, 8])[..., np.newaxis],
                                       np.array([7, 5, 3, 1])[..., np.newaxis]]),
                             np.array([0., 1., 2., 3.]))

    binsize = 2
    xedges = np.arange(position.x.min(), position.x.max()+binsize, binsize)
    yedges = np.arange(position.y.min(), position.y.max()+binsize, binsize)

    spikes = [nept.SpikeTrain(np.array([0., 3., 3., 3.]), 'test')]

    tuning_curves = nept.tuning_curve_2d(position, spikes, xedges, yedges, gaussian_std=1.4)

    assert np.allclose(tuning_curves, [np.array([[[0.02983511, 0.50226235, 1.80353116],
                                                  [0.1729374, 0.18497526, 0.50226235],
                                                  [0.60142384, 0.1729374, 0.02983511]]])])
