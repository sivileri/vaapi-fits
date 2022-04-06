###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.decoder import DecoderTest

spec = load_test_spec("avc", "decode")

@slash.requires(*platform.have_caps("decode", "avc"))
@slash.requires(*have_gst_element("vaapih264dec"))
class default(DecoderTest):
  def before(self):
    super().before()
    vars(self).update(
      # default metric
      metric      = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0),
      caps        = platform.get_caps("decode", "avc"),
      gstdecoder  = "vaapih264dec",
      gstparser   = "h264parse",
    )
    hasSupport = have_vainfo_entrypoint("VAProfileH264Main", "VAEntrypointVLD", self.renderDevice)
    if(not hasSupport[0]):
      slash.skip_test(hasSupport[1])
    hasSupport = have_vainfo_entrypoint("VAProfileH264High", "VAEntrypointVLD", self.renderDevice)
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
