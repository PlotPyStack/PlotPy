import numpy as np
import pytest
import qtpy.QtCore as QC

from plotpy.widgets.items.curve.base import seg_dist, seg_dist_v

param_list = [
    ((200, 100), (150, 196), (250, 180), 86),
    ((200, 100), (190, 196), (210, 180), 80),
    ((201, 105), (201, 196), (201, 180), 75),
]


# @pytest.mark.skip(reason="Explose le framework en runtime")
@pytest.mark.parametrize("point_1,point_2,point_3,output", param_list)
def test_seg_dist(point_1, point_2, point_3, output):
    """ """
    ret = seg_dist(QC.QPointF(*point_1), QC.QPointF(*point_2), QC.QPointF(*point_3))
    assert int(ret) == output


# @pytest.mark.skip(reason="Explose le framework en runtime")
def test_seg_dist_v():
    """Test de seg_dist_v"""
    a = (np.arange(10.0) ** 2).reshape(5, 2)
    ix, dist = seg_dist_v((2.1, 3.3), a[:-1, 0], a[:-1, 1], a[1:, 0], a[1:, 1])
    assert ix == 0
    assert round(dist, 2) == 0.85


if __name__ == "__main__":
    pytest.main()
