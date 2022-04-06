###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.decoder import DecoderTest

spec = load_test_spec("hevc", "decode", "8bit")

@slash.requires(*platform.have_caps("decode", "hevc_8"))
@slash.requires(*have_gst_element("vaapih265dec"))
class default(DecoderTest):
  def before(self):
    super().before()
    vars(self).update(
      # default metric
      metric      = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0),
      caps        = platform.get_caps("decode", "hevc_8"),
      gstdecoder  = "vaapih265dec",
      gstparser   = "h265parse",
    )
    hasSupport = have_vainfo_entrypoint("VAProfileHEVCMain", "VAEntrypointVLD", self.renderDevice)
    if(not hasSupport[0]):
      slash.skip_test(hasSupport[1])

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    vars(self).update(case = case)

    dxmap = {".mp4" : "qtdemux"}
    ext = os.path.splitext(self.source)[1]
    if ext in dxmap.keys():
      vars(self).update(
        case        = case,
        gstdemuxer  = dxmap[ext],
      )

    self.decode()
