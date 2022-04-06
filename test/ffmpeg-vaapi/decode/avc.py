###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.decoder import DecoderTest

spec = load_test_spec("avc", "decode")

@slash.requires(*platform.have_caps("decode", "avc"))
class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)
    self.caps   = platform.get_caps("decode", "avc")
    super(default, self).before()
    hasSupport = have_vainfo_entrypoint("VAProfileH264Main", "VAEntrypointVLD", self.renderDevice)
    if(not hasSupport[0]):
      slash.skip_test(hasSupport[1])
    hasSupport = have_vainfo_entrypoint("VAProfileH264High", "VAEntrypointVLD", self.renderDevice)
    if(not hasSupport[0]):
      slash.skip_test(hasSupport[1])

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()
