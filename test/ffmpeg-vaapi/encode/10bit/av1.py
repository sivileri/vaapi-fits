###
### Copyright (C) 2019-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .....lib import *
from .....lib.ffmpeg.vaapi.util import *
from .....lib.ffmpeg.vaapi.encoder import EncoderTest

spec = load_test_spec("av1", "encode", "10bit")

@slash.requires(*have_ffmpeg_encoder("av1_vaapi"))
class AV1EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec = "av1-10",
      ffenc = "av1_vaapi",
    )

  def get_file_ext(self):
    return "ivf"

  def get_vaapi_profile(self):
    return "VAProfileAV1Profile0"

@slash.requires(*platform.have_caps("encode", "av1_10"))
class AV1EncoderTest(AV1EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "av1_10"),
      lowpower  = 0,
    )
    hasSupport = have_vainfo_entrypoint(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)
    if(not hasSupport[0]):
      slash.skip_test(hasSupport[1])
    has10BitFormat = have_vainfo_rt_format(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice, "VA_RT_FORMAT_YUV420_10")
    if(not has10BitFormat[0]):
      slash.skip_test(has10BitFormat[1])

class cqp(AV1EncoderTest):
  def init(self, tspec, case, gop, tile_rows, tile_cols, bframes, qp, quality, profile, tile_mode):
    vars(self).update(tspec[case].copy())
    maxSupportedTiles=int(get_vainfo_max_slices(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported slices: " + str(maxSupportedTiles))
    if (maxSupportedTiles < (tile_rows * tile_cols)):
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
      tile_rows    = tile_rows,
      tile_cols    = tile_cols,
      tile_mode = tile_mode,
    )

  @slash.parametrize(*gen_av1_cqp_parameters(spec))
  def test(self, case, gop, bframes, tile_cols, tile_rows, qp, quality, profile, tile_mode):
    self.init(spec, case, gop, bframes, tile_cols, tile_rows, qp, quality, profile, tile_mode)
    self.encode()

class cbr(AV1EncoderTest):
  def init(self, tspec, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode):
    vars(self).update(tspec[case].copy())
    maxSupportedTiles=int(get_vainfo_max_slices(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported slices: " + str(maxSupportedTiles))
    if (maxSupportedTiles < (tile_rows * tile_cols)):
      slash.skip_test("Number of tiles requested is not supported by underlying device.")
    maxSupportedBFrames = int(get_vainfo_num_lX_references(self.get_vaapi_profile(), "VAEntrypointEncSlice", "1", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported B frames: " + str(maxSupportedBFrames))
    if ((bframes > 0) and (maxSupportedBFrames == 0)):
      slash.skip_test("B frames are not supported by underlying device.")    
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "cbr",
      tile_rows  = tile_rows,
      tile_cols  = tile_cols,
      quality   = quality,
      tile_mode = tile_mode,
    )

  @slash.parametrize(*gen_av1_cbr_parameters(spec))
  def test(self, case, gop, bframes, tile_cols, tile_rows, bitrate, quality, fps, profile, tile_mode):
    self.init(spec, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode)
    self.encode()


class vbr(AV1EncoderTest):
  def init(self, tspec, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode):
    vars(self).update(tspec[case].copy())
    maxSupportedTiles=int(get_vainfo_max_slices(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported slices: " + str(maxSupportedTiles))
    if (maxSupportedTiles < (tile_rows * tile_cols)):
      slash.skip_test("Number of tiles requested is not supported by underlying device.")
    maxSupportedBFrames = int(get_vainfo_num_lX_references(self.get_vaapi_profile(), "VAEntrypointEncSlice", "1", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported B frames: " + str(maxSupportedBFrames))
    if ((bframes > 0) and (maxSupportedBFrames == 0)):
      slash.skip_test("B frames are not supported by underlying device.")    
    vars(self).update(
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      maxrate = bitrate,
      minrate = bitrate,
      profile = profile,
      rcmode  = "vbr",
      tile_rows  = tile_rows,
      tile_cols  = tile_cols,
      quality   = quality,
      tile_mode = tile_mode,
    )

  @slash.parametrize(*gen_av1_vbr_parameters(spec))
  def test(self, case, gop, bframes, tile_cols, tile_rows, bitrate, quality, fps, profile, tile_mode):
    self.init(spec, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode)
    self.encode()
