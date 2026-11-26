"""Perspective transform from image pixels to field meters (HU-7.x)."""

from __future__ import annotations


class ViewTransformer:
    def __init__(self, image_points=None, field_points=None) -> None:
        self.image_points = image_points
        self.field_points = field_points

    def add_transformed_position_to_tracks(self, tracks) -> None:
        raise NotImplementedError("HU-7.2")
