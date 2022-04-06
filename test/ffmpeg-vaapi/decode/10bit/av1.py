###
### Copyright (C) 2018-2020 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.ffmpeg.vaapi.util import *
from .....lib.ffmpeg.vaapi.decoder import DecoderTest

spec = load_test_spec("av1", "decode", "10bit")

@slash.requires(*platform.have_caps("decode", "av1_10"))
class default(DecoderTest):
  def before(self):
    # default metric
    self.metric = dict(type = "ssim", miny = 1.0, minu = 1.0, minv = 1.0)
    self.caps   = platform.get_caps("decode", "av1_10")
    super(default, self).before()
    hasSupport = have_vainfo_entrypoint("VAProfileAV1Profile0", "VAEntrypointVLD", self.renderDevice)
    if(not hasSupport[0]):
      slash.skip_test(hasSupport[1])

  @slash.parametrize(("case"), sorted(spec.keys()))
  def test(self, case):
    vars(self).update(spec[case].copy())
    self.case = case
    self.decode()

  @timefn("ffmpeg")
  def call_ffmpeg(self):
    # NOTE: If test has requested scale in/out range, then apply it only when
    # hw and sw formats differ (i.e. when csc is necessary).
    scale_range = ""
    if hasattr(self, "ffscale_range") and self.hwformat != self.mformat:
      scale_range = f"-vf 'scale=in_range={self.ffscale_range}:out_range={self.ffscale_range}'"

    return call(
      (
        f"{exe2os('ffmpeg')} -hwaccel {self.hwaccel}"
        f" -hwaccel_device {self.renderDevice}"
        f" -hwaccel_output_format {self.hwformat}"
        f" -hwaccel_flags allow_profile_mismatch -v verbose"
      ) + (
        " -c:v {ffdecoder}" if hasattr(self, "ffdecoder") else ""
      ).format(**vars(self)) + (
        f" -i {filepath2os(self.source)} {scale_range}"
        f" -pix_fmt {self.mformat} -f rawvideo -vsync passthrough"
        f" -vframes {self.frames} -y {filepath2os(self.decoded)}"
      )
    )
