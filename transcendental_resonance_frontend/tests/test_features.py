import inspect
from utils.features import (
    quick_post_button,
    high_contrast_switch,
    skeleton_loader,
)


def test_quick_post_button_callable():
    assert callable(quick_post_button)


def test_high_contrast_switch_callable():
    assert callable(high_contrast_switch)


def test_skeleton_loader_callable():
    assert callable(skeleton_loader)
