"""Where two parts touch is where their material meets, not where their boxes do.

A profile's box is the whole it fits in (a-profile-is-one-part-with-its-section), so a channel laid
on an angle's flange sits inside the angle's box: read by boxes, the two run into each other and a
joint between them "joins parts that do not touch". Read by sections, they touch on the flange.
"""

from __future__ import annotations

from types import SimpleNamespace

from quern.tree import Quern

from furniture_design import natives
from furniture_design.standards_piece import piece_world

# An angle 20 x 20 x 1 along x, its flange lying flat (z 0 to 1) and its leg standing at y 0 to 1;
# a channel 12 x 12 x 1 open upwards laid on the flange, from y 10 to 22.
ANGLE = SimpleNamespace(lo=[0, 0, 0], hi=[1000, 20, 20],
                        section=[[0, 0], [20, 0], [20, 1], [1, 1], [1, 20], [0, 20]])
CHANNEL = SimpleNamespace(lo=[0, 10, 1], hi=[1000, 22, 13],
                          section=[[0, 0], [12, 0], [12, 12], [11, 12], [11, 1], [1, 1], [1, 12], [0, 12]])


def test_a_channel_on_an_angles_flange_touches_it_where_they_meet():
    lo, hi, normal = natives.contact(CHANNEL, ANGLE)
    assert normal == 2
    assert (lo[1], hi[1], lo[2]) == (10, 20, 1)
    assert (lo[0], hi[0]) == (0, 1000)


def test_a_channel_that_runs_into_the_angles_leg_does_not_touch_it():
    into = SimpleNamespace(lo=[0, 0, 1], hi=[1000, 12, 13], section=CHANNEL.section)
    assert natives.contact(into, ANGLE) is None


def test_two_boxes_touch_as_before():
    a = SimpleNamespace(lo=[0, 0, 0], hi=[18, 400, 450])
    b = SimpleNamespace(lo=[18, 0, 100], hi=[600, 400, 118])
    assert natives.contact(a, b) == ((18, 0, 100), (18, 400, 118), 0)


def test_the_standards_door_rail_places_its_screws():
    """The standards' own example glues the channel under the angle's flange, inside its box."""
    tree = Quern()
    tree.root.children = piece_world()
    boxes = {b.path: b for b in natives.bodies(tree, "pieces/doors")}
    joint = natives.get_node(tree, "pieces/doors/channel-to-angle")
    lay = natives.joint_layout(tree, "pieces/doors/channel-to-angle", joint, boxes)
    assert lay.normal == 2 and lay.lo[2] == 1199
    assert all(p[2] == 1199 for p in lay.positions) and len(lay.positions) == 4
