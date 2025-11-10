import numpy as np

from src.backend.services.video_composer import VideoComposer


def test_compose_places_inset_in_top_left_corner():
    composer = VideoComposer(border_thickness=0)
    base = np.zeros((100, 100, 3), dtype=np.uint8)
    inset = np.ones((50, 50, 3), dtype=np.uint8) * 255

    result = composer.compose(base, inset, position=(0, 0), size=(20, 20))

    assert result[0, 0, 0] == 255
    assert result[19, 19, 0] == 255
    assert result[21, 21, 0] == 0

