#!/usr/bin/env python

# Copyright (c) 2015 Max Planck Institute
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
# Jim Mainprice on Sunday June 17 2018

import demos_common_imports
from scipy import optimize
from pyrieef.motion.objective import *
import time
from numpy.testing import assert_allclose


class TrajectoryOptimizationViewer:

    def __init__(self, objective, draw):
        self.objective = objective
        self.viewer = None
        if draw:
            self.init_viewer()

    def init_viewer(self):
        from pyrieef.rendering import workspace_renderer
        from pyrieef.rendering import opengl
        self.viewer = workspace_renderer.WorkspaceRender(
            self.objective.workspace)
        self.viewer.draw_ws_background(self.objective.obstacle_cost_map())

    def evaluate(self, x):
        v = self.objective.objective(x)
        # print "value shape : ", v.shape
        return v

    def gradient(self, x, draw=True):
        if draw and self.viewer is not None:
            trajectory = Trajectory(q_init=self.objective.q_init, x=x)
            g_traj = Trajectory(
                q_init=self.objective.q_init,
                x=-0.001 * self.objective.objective.gradient(x) + x)
            for k in range(self.objective.T + 1):
                q = trajectory.configuration(k)
                self.viewer.draw_ws_circle(
                    .01, q, color=(0, 0, 1) if k == 0 else (0, 1, 0))
                self.viewer.draw_ws_line(q, g_traj.configuration(k))
            self.viewer.render()
            time.sleep(0.1)
        # print "gradient shape : ", self.objective.objective.jacobian(x).shape
        # return self.objective.objective.jacobian(x)
        g = self.objective.objective.gradient(x)
        # print "jacobian shape : ", g.shape
        return g

    def hessian(self, x):
        # print "hessian shape : ", self.objective.objective.hessian(x).shape
        return np.array(self.objective.objective.hessian(x))
        # return np.eye(self.objective.metric.shape[0])


def motion_optimimization():
    print "Checkint Motion Optimization"
    trajectory = linear_interpolation_trajectory(
        q_init=-.22 * np.ones(2),
        q_goal=.3 * np.ones(2),
        T=22
    )
    objective = MotionOptimization2DCostMap(
        T=trajectory.T(),
        q_init=trajectory.initial_configuration(),
        q_goal=trajectory.final_configuration()
    )
    gtol = 1e-05
    assert check_jacobian_against_finite_difference(
        objective.objective, verbose=False)
    f = TrajectoryOptimizationViewer(objective, draw=True)
    t_start = time.time()
    x = trajectory.active_segment()
    # print "x.shape : ", x.shape
    res = optimize.minimize(
        f.evaluate,
        x0=x,
        method='trust-ncg',
        jac=f.gradient,
        hess=f.hessian,
        # hessp=f.hessian_product
        options={'maxiter': 100, 'gtol': gtol, 'disp': True}
    )
    print "optimization done in {} sec.".format(time.time() - t_start)
    # objective.optimize(q_init=np.zeros(2), trajectory=trajectory)
    # print trajectory.x().shape
    # print res.x.shape
    # print res
    # print trajectory.x()
    # print "- res.jac : {}".format(res.jac.shape)
    print "gradient norm : ", np.linalg.norm(res.jac)
    # print "jac : ", res.jac
    # assert_allclose(res.jac, np.zeros(res.jac.size), atol=1e-1)

if __name__ == "__main__":
    motion_optimimization()
    raw_input("Press Enter to continue...")
    # import cProfile
    # cProfile.run('motion_optimimization()')