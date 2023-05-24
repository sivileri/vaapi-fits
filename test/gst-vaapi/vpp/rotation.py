###
### Copyright (C) 2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.vpp import VppTest

spec = load_test_spec("vpp", "rotation")

@slash.requires(*platform.have_caps("vpp", "rotation"))
class default(VppTest):
  def before(self):
    vars(self).update(
      caps    = platform.get_caps("vpp", "rotation"),
      vpp_op  = "transpose",
    )
    super(default, self).before()

  @slash.parametrize(*gen_vpp_rotation_parameters(spec))
  def test(self, case, degrees):
    vars(self).update(spec[case].copy())
    vars(self).update(
      case      = case,
      degrees   = degrees,
      direction = map_transpose_direction(degrees, None),
      method    = None,
    )

    if self.direction is None:
      slash.skip_test(
        "{degrees} rotation unsupported".format(**vars(self)))

    self.vpp()

  def check_metrics(self):
    check_metric(
      metric = dict(type = "ssim", miny = 0.90, minu = 0.90, minv = 0.90),
      reference = self.reference[0].replace("filenameplaceholder", "{}_transpose_{}_None_{}x{}_{}.yuv".format(self.case, self.degrees, self.width, self.height, self.format)),
      decoded = self.decoded,
      format = self.format,
      format2 = self.format,
      width = self.width,
      height = self.height,
      frames = self.frames,
    )