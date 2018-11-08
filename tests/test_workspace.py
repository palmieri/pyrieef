#!/usr/bin/env python

# Copyright (c) 2018, University of Stuttgart
# All rights reserved.
#
# Permission to use, copy, modify, and distribute this software for any purpose
# with or without   fee is hereby granted, provided   that the above  copyright
# notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
# REGARD TO THIS  SOFTWARE INCLUDING ALL  IMPLIED WARRANTIES OF MERCHANTABILITY
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR  BE LIABLE FOR ANY SPECIAL, DIRECT,
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR  ANY DAMAGES WHATSOEVER RESULTING  FROM
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
# OTHER TORTIOUS ACTION,   ARISING OUT OF OR IN    CONNECTION WITH THE USE   OR
# PERFORMANCE OF THIS SOFTWARE.
#
#                                        Jim Mainprice on Sunday June 13 2018


from __init__ import *
# from __future__ import absolute_import
# from .__init__ import *
from geometry.workspace import *
from itertools import product
from numpy.testing import assert_allclose


def test_circle():
    circle = Circle()
    sdf = SignedDistance2DMap(circle)

    print("Check Circle SDF (J implementation) : ")
    assert check_jacobian_against_finite_difference(sdf)

    print("Check Circle SDF (H implementation) : ")
    assert check_hessian_against_finite_difference(sdf)

    x = np.random.random(2)

    # Test gradient outside circle
    circle = Circle(radius=.2)
    p1 = super(Circle, circle).dist_gradient(x)
    p2 = circle.dist_gradient(x)
    assert_allclose(p1, p2)

    # Test gradient inside circle
    circle = Circle(radius=2.)
    p1 = super(Circle, circle).dist_gradient(x)
    p2 = circle.dist_gradient(x)
    assert_allclose(p1, p2)


def test_segment():
    p1 = np.random.random(2)
    p2 = np.random.random(2)
    l = segment_from_end_points(p1, p2)
    p1_l, p2_l = l.end_points()
    assert_allclose(p1, p1_l)
    assert_allclose(p2, p2_l)

    segment = Segment(orientation=.0)
    sdf = SignedDistance2DMap(segment)

    print("Check Segment SDF (J implementation) : ")
    assert check_jacobian_against_finite_difference(sdf)

    # print("Check Segment SDF (H implementation) : ")
    # assert check_hessian_against_finite_difference(sdf)


def test_box():

    box = Box()

    verticies = box.verticies()
    for k, vertex in enumerate(verticies):
        print("vertex {} : {}".format(k, vertex))

    dist = box.dist_from_border(np.array([0.0, 1.0]))
    print("dist = ", dist)
    assert np.fabs(dist - 0.5) < 1.e-06

    dist = box.dist_from_border(np.array([1.0, 0.0]))
    print("dist = ", dist)
    assert np.fabs(dist - 0.5) < 1.e-06

    box = Box(
        origin=np.array([.5, .5]),
        dim=np.array([1., 1.])
    )
    sdf = SignedDistance2DMap(box)

    print("Check Box SDF (J implementation) : ")
    assert check_jacobian_against_finite_difference(sdf)

    # print("Check Box SDF (H implementation) : ")
    # assert check_hessian_against_finite_difference(sdf)

    box = Box(
        origin=np.array([-.5, .5]),
        dim=np.array([.5, .5])
    )
    sdf = SignedDistance2DMap(box)

    print("Check Box SDF (J implementation) : ")
    assert check_jacobian_against_finite_difference(sdf)


def test_inside_box():
    for n in [2, 3]:  # TODO make it work for 3D
        box = EnvBox(
            origin=np.random.rand(n),
            dim=np.random.rand(n) + .5 * np.ones(n))
        for i in range(50):
            p = box.sample_uniform()
            assert box.is_inside(p)
            p = np.random.random(box.origin.size)
            assert not box.is_inside(p + box.upper_corner())
            assert not box.is_inside(-1. * p + box.lower_corner())


def test_ellipse():

    ellipse = Ellipse()
    ellipse.a = 0.1
    ellipse.b = 0.2

    dist = ellipse.dist_from_border(np.array([0.3, 0.0]))
    print("dist = ", dist)
    assert np.fabs(dist - 0.2) < 1.e-06

    dist = ellipse.dist_from_border(np.array([0.0, 0.3]))
    print("dist = ", dist)
    assert np.fabs(dist - 0.1) < 1.e-06


def test_sdf_derivatives():
    verbose = False
    circles = []
    for center, radius in sample_circles(nb_circles=10):
        circles.append(Circle(center, radius))
    for c in circles:
        signed_distance_field = SignedDistance2DMap(c)
        assert check_jacobian_against_finite_difference(
            signed_distance_field, verbose)
        assert check_hessian_against_finite_difference(
            signed_distance_field)


def test_sdf_workspace():
    workspace = sample_workspace(nb_circles=10)
    signed_distance_field = SignedDistanceWorkspaceMap(workspace)
    assert check_jacobian_against_finite_difference(signed_distance_field)
    assert check_hessian_against_finite_difference(signed_distance_field)


def test_meshgrid():
    nb_points = 10
    workspace = Workspace()
    pixel_map = workspace.pixel_map(nb_points)
    X, Y = workspace.box.meshgrid(nb_points)
    print("pm -- resolution : {}".format(pixel_map.resolution))
    print("pm -- origin : {}".format(pixel_map.origin))
    for i, j in product(list(range(nb_points)), list(range(nb_points))):
        p_meshgrid = np.array([X[i, j], Y[i, j]])
        p_grid = pixel_map.world_to_grid(p_meshgrid)
        p_world = pixel_map.grid_to_world(p_grid)
        assert_allclose(p_meshgrid, p_world)


def test_sdf_grid():
    nb_points = 24
    workspace = sample_workspace(nb_circles=10)
    sdf = SignedDistanceWorkspaceMap(workspace)
    pixel_map = workspace.pixel_map(nb_points)
    # WARNING !!!
    # Here we need to transpose the costmap
    # otherwise the grid representation do not match
    grid = workspace.box.stacked_meshgrid(nb_points)
    sdfmap = sdf(grid).T
    for i, j in product(list(range(nb_points)), list(range(nb_points))):
        p = pixel_map.grid_to_world(np.array([i, j]))
        assert_allclose(sdf(p), sdfmap[i, j])


def test_workspace_to_occupancy_map():
    np.random.seed(0)
    np.set_printoptions(suppress=True, linewidth=200, precision=2)
    nb_points = 10
    workspace = sample_workspace(nb_circles=5)
    occ = occupancy_map(nb_points, workspace)
    pixel_map = pixelmap_from_box(nb_points, workspace.box)
    for i, j in product(list(range(nb_points)), list(range(nb_points))):
        p = pixel_map.grid_to_world(np.array([i, j]))
        v = float(workspace.min_dist(p)[0] < 0)
        assert_allclose(occ[i, j], v)


if __name__ == "__main__":

    test_circle()
    test_segment()
    test_box()
    test_inside_box()
    test_ellipse()
    test_sdf_derivatives()
    test_sdf_workspace()
    test_meshgrid()
    test_sdf_grid()
    test_workspace_to_occupancy_map()
