###
### Copyright (C) 2019-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.encoder import EncoderTest

spec = load_test_spec("av1", "encode", "8bit")

# @slash.requires(*have_ffmpeg_encoder("av1_vaapi"))
class AV1EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec = "av1-8",
      ffenc = "av1_vaapi",
    )

  def get_file_ext(self):
    return "ivf"

  def get_vaapi_profile(self):
    return "VAProfileAV1Profile0"

@slash.requires(*platform.have_caps("vdenc", "av1_8"))
class AV1EncoderLPTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "av1_8"),
      lowpower  = 1,
    )

class cqp_lp(AV1EncoderLPTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows,qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = gop,
      bframes   = bframes,
      qp        = qp,
      rcmode    = "cqp",
      quality   = quality,
      profile   = profile,
      tilerows  = tilerows,
      tilecols  = tilecols,
    )

  @slash.parametrize(*gen_av1_cqp_lp_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    self.encode()

class cbr_lp(AV1EncoderLPTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      tilerows  = tilerows,
      tilecols  = tilecols,
      quality   = quality,
    )

  @slash.parametrize(*gen_av1_cbr_lp_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, bitrate, quality, fps, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()

@slash.requires(*platform.have_caps("encode", "av1_8"))
class AV1EncoderTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "av1_8"),
      lowpower  = 0,
    )
    hasSupport = have_vainfo_entrypoint(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)
    if(not hasSupport[0]):
      slash.skip_test(hasSupport[1])

class cqp(AV1EncoderTest):
  def init(self, tspec, case, gop, tilerows, tilecols, bframes, qp, quality, profile):
    vars(self).update(tspec[case].copy())
    maxSupportedTiles=int(get_vainfo_max_slices(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported slices: " + str(maxSupportedTiles))
    if (maxSupportedTiles < (tilerows * tilecols)):
      slash.skip_test("Number of tiles requested is not supported by underlying device.")
    maxSupportedBFrames = int(get_vainfo_num_lX_references(self.get_vaapi_profile(), "VAEntrypointEncSlice", "1", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported B frames: " + str(maxSupportedBFrames))
    if ((bframes > 0) and (maxSupportedBFrames == 0)):
      slash.skip_test("B frames are not supported by underlying device.")    
    vars(self).update(
      bframes   = bframes,
      case      = case,
      gop       = gop,
      profile   = profile,
      qp        = qp,
      quality   = quality,
      rcmode    = "cqp",
      tilerows    = tilerows,
      tilecols    = tilecols,
    )

  @slash.parametrize(*gen_av1_cqp_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, qp, quality, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, qp, quality, profile)
    self.encode()

class cbr(AV1EncoderTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      tilerows  = tilerows,
      tilecols  = tilecols,
      quality   = quality,
    )

  @slash.parametrize(*gen_av1_cbr_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, bitrate, quality, fps, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()


class vbr(AV1EncoderTest):
  def init(self, tspec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "vbr",
      tilerows  = tilerows,
      tilecols  = tilecols,
      quality   = quality,
    )

  @slash.parametrize(*gen_av1_vbr_parameters(spec))
  def test(self, case, gop, bframes, tilecols, tilerows, bitrate, quality, fps, profile):
    self.init(spec, case, gop, bframes, tilecols, tilerows, bitrate, fps, quality, profile)
    self.encode()
