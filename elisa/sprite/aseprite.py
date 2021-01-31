from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import List


@dataclass
class FrameDescriptor:
    sprite_fp: str
    # "frame": { "x": 32, "y": 0, "w": 32, "h": 32 },
    frame_ptr_x: int = 0
    frame_ptr_y: int = 0
    frame_ptr_w: int = 0
    frame_ptr_h: int = 0
    rotated: bool = False
    trimmed: bool = False
    #  { "x": 0, "y": 0, "w": 32, "h": 32 },
    spriteSourceSize_x: int = 0
    spriteSourceSize_y: int = 0
    spriteSourceSize_w: int = 0
    spriteSourceSize_h: int = 0
    #  { "w": 32, "h": 32 },
    sourceSize_w: int = 0
    sourceSize_h: int = 0
    duration_ms: int = 0

    @property
    def frame(self) -> tuple[int, int, int, int]:
        return self.frame_ptr_x, self.frame_ptr_y, self.frame_ptr_w, self.frame_ptr_h

    @property
    def spriteSourceSize(self) -> tuple[int, int, int, int]:
        return (
            self.spriteSourceSize_x,
            self.spriteSourceSize_y,
            self.spriteSourceSize_w,
            self.spriteSourceSize_h,
        )

    @property
    def sourceSize(self) -> tuple[int, int]:
        return self.sourceSize_w, self.sourceSize_h


@dataclass
class AnimationLayer:
    # { "name": "Layer", "opacity": 255, "blendMode": "normal" }
    name: str = ""
    opacity: int = 0
    blendmode: str = ""


@dataclass
class FrameTag:
    # { "name": "Tag1", "from": 0, "to": 1, "direction": "forward" }
    name: str
    direction: str
    frame_from: int = 0
    frame_to: int = 0


@dataclass
class AnimationDescriptor:
    # "app": "http://www.aseprite.org/",
    app_link: str
    # "version": "1.2.25-x64",
    version: str
    # "format": "I8"
    format: str
    #   "frameTags": [ ],
    frame_tags: list[FrameTag]
    #   "layers": [
    #    { "name": "Layer", "opacity": 255, "blendMode": "normal" }
    #  }
    layers: list[AnimationLayer]
    #   "slices": [ ]
    slices: list
    #   "size": { "w": 128, "h": 32 },
    size_w: int = 0
    size_h: int = 0
    #   "scale": "1",
    scale: float = 0.0

    @property
    def size(self) -> tuple[int, int]:
        return self.size_w, self.size_h


@dataclass
class SliceKey:
    frame: int
    bounds_x: int
    bounds_y: int
    bounds_w: int
    bounds_h: int
    center_x: int
    center_y: int
    center_w: int
    center_h: int

    @property
    def bounds(self) -> tuple[int, int, int, int]:
        return self.bounds_x, self.bounds_y, self.bounds_w, self.bounds_h

    @property
    def center(self) -> tuple[int, int, int, int]:
        return self.center_x, self.center_y, self.center_w, self.center_h


@dataclass
class Slice:
    # { "name": "Button-patch",
    #  "color": "#0000ffff",
    #  "keys": [{ "frame": 0,
    #             "bounds": {"x": 118, "y": 118, "w": 20, "h": 21 },
    #             "center": {"x": 5, "y": 5, "w": 10, "h": 9 } }] }
    name: str
    color: str
    keys: List[SliceKey]


@dataclass
class AsepriteAnimation:
    frames: dict[str, FrameDescriptor]
    descriptor: AnimationDescriptor

    @property
    def no_frames(self) -> int:
        """Number of frames in the Aseprite animation object

        Returns:
            int: the number of animation frames
        """
        return len(self.frames)

    @staticmethod
    def create(json_fp: str) -> AsepriteAnimation:
        """Generates an Aseprite Animation object from the json data source.

        Args:
            json_fp (str): path to json file describing the Aseprite animation sequence

        Raises:
            ValueError: raised if the file path is not provided, empty or the file does not exist.
            ValueError: raised if the json does not seem to be a plausible Aseprite animation JSON descriptor

        Returns:
            AsepriteAnimation: the constructed animation object
        """
        if not json_fp or json_fp.strip() == "":
            raise ValueError("path to aseprite export json not provided")
        if not os.path.exists(json_fp):
            raise ValueError("json_fp does not exist")

        with open(json_fp, "r+") as f:
            _json = json.load(f)
            if "meta" not in _json:
                raise ValueError(
                    "json does not appear to be a valid aseprite animation in json format"
                )

            _meta = _json["meta"]

            _frame_tags = []
            _animation_layers = []
            _slices = []

            for _frame_tag in _meta.get("frameTags", []):
                _frame_tags.append(
                    FrameTag(
                        name=_frame_tag["name"],
                        frame_from=_frame_tag["from"],
                        frame_to=_frame_tag["to"],
                        direction=_frame_tag["direction"],
                    )
                )

            for _anim_layer in _meta.get("layers", []):
                _animation_layers.append(
                    AnimationLayer(
                        name=_anim_layer["name"],
                        opacity=_anim_layer["opacity"],
                        blendmode=_anim_layer["blendMode"],
                    )
                )

            for _slice in _meta.get("slices", []):
                _sk = []
                for _slice_key in _slice.get("keys", []):
                    _sk.append(
                        SliceKey(
                            frame=_slice_key["frame"],
                            bounds_x=_slice_key["bounds"]["x"],
                            bounds_y=_slice_key["bounds"]["y"],
                            bounds_w=_slice_key["bounds"]["w"],
                            bounds_h=_slice_key["bounds"]["h"],
                            center_x=_slice_key["center"]["x"],
                            center_y=_slice_key["center"]["y"],
                            center_w=_slice_key["center"]["w"],
                            center_h=_slice_key["center"]["h"],
                        )
                    )
                _slices.append(
                    Slice(name=_slice["name"], color=_slice["color"], keys=_sk)
                )

            _desc = AnimationDescriptor(
                app_link=_meta["app"],
                version=_meta["version"],
                format=_meta["format"],
                frame_tags=_frame_tags,
                layers=_animation_layers,
                slices=_slices,
                size_w=_meta["size"]["w"],
                size_h=_meta["size"]["h"],
                scale=float(_meta["scale"]),
            )

            _frames = {}
            if "frames" in _json:
                _frames = _json["frames"]

            for frame_fp in _frames:
                _f = _frames[frame_fp]
                _frame = FrameDescriptor(
                    sprite_fp=frame_fp,
                    frame_ptr_x=_f["frame"]["x"],
                    frame_ptr_y=_f["frame"]["y"],
                    frame_ptr_w=_f["frame"]["w"],
                    frame_ptr_h=_f["frame"]["h"],
                    rotated=_f["rotated"],
                    trimmed=_f["trimmed"],
                    spriteSourceSize_x=_f["spriteSourceSize"]["x"],
                    spriteSourceSize_y=_f["spriteSourceSize"]["y"],
                    spriteSourceSize_w=_f["spriteSourceSize"]["w"],
                    spriteSourceSize_h=_f["spriteSourceSize"]["h"],
                    sourceSize_w=_f["sourceSize"]["w"],
                    sourceSize_h=_f["sourceSize"]["h"],
                    duration_ms=_f["duration"],
                )
                _frames[frame_fp] = _frame

            return AsepriteAnimation(frames=_frames, descriptor=_desc)
