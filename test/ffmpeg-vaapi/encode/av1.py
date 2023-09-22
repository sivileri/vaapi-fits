###
### Copyright (C) 2019-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.ffmpeg.vaapi.util import *
from ....lib.ffmpeg.vaapi.encoder import EncoderTest

spec = load_test_spec("av1", "encode", "8bit")

@slash.requires(*have_ffmpeg_encoder("av1_vaapi"))
class AV1EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec = "av1-8",
      ffenc = "av1_vaapi",
    )

  def check_bitrate(self):
    pass # Disable RC controls for these tests in AV1, transcode/AV1 checks them with more suitable input streams

  # Use software decoding for AV1 metrics as ffmpeg decode has bugs with multi-tile
  def check_metrics(self):
    iopts = ""
    if vars(self).get("ffdecoder", None) is not None:
      iopts += "-c:v {ffdecoder} "
    iopts += "-i {osencoded}"


    name = (self.gen_name() + "-{width}x{height}-{format}").format(**vars(self))
    self.decoded = get_media()._test_artifact("{}.yuv".format(name))
    oopts = (
      " -pix_fmt {mformat} -f rawvideo"
      " -vsync passthrough -vframes {frames}"
      f" -y {filepath2os(self.decoded)}")
    self.call_ffmpeg(iopts.format(**vars(self)), oopts.format(**vars(self)), "", "", True) # Use sw decode

    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.source, self.decoded,
        self.width, self.height,
        self.frames, self.format),
      context = self.refctx,
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
  def init(self, tspec, case, gop, bframes, tile_cols, tile_rows, qp, quality, profile, tile_mode):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case      = case,
      gop       = gop,
      bframes   = bframes,
      qp        = qp,
      rcmode    = "cqp",
      quality   = quality,
      profile   = profile,
      tile_rows  = tile_rows,
      tile_cols  = tile_cols,
      tile_mode = tile_mode,
    )

  @slash.parametrize(*gen_av1_cqp_lp_parameters(spec))
  def test(self, case, gop, bframes, tile_cols, tile_rows, qp, quality, profile, tile_mode):
    self.init(spec, case, gop, bframes, tile_cols, tile_rows, qp, quality, profile, tile_mode)
    self.encode()

class cbr_lp(AV1EncoderLPTest):
  def init(self, tspec, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bframes = bframes,
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

  @slash.parametrize(*gen_av1_cbr_lp_parameters(spec))
  def test(self, case, gop, bframes, tile_cols, tile_rows, bitrate, quality, fps, profile, tile_mode):
    self.init(spec, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode)
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
  def init(self, tspec, case, gop, tile_rows, tile_cols, bframes, qp, quality, profile, tile_mode):
    vars(self).update(tspec[case].copy())
    maxSupportedTileRowsSupported = bool(get_vainfo_max_tile_rows(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][0])
    if (maxSupportedTileRowsSupported):
      maxSupportedTileRows=int(get_vainfo_max_tile_rows(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
      slash.logger.info("Underlying GPU max supported tile rows: " + str(maxSupportedTileRows))
      if (maxSupportedTileRows < tile_rows):
        slash.skip_test("Requested tile_rows higher than hardware supports.")

    maxSupportedTileColsSupported=bool(get_vainfo_max_tile_cols(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][0])
    if (maxSupportedTileColsSupported):
      maxSupportedTileCols=int(get_vainfo_max_tile_cols(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
      slash.logger.info("Underlying GPU max supported tile cols: " + str(maxSupportedTileCols))
      if (maxSupportedTileCols < tile_cols):
        slash.skip_test("Requested tile_cols higher than hardware supports.")

    maxSupportedTiles=int(get_vainfo_max_slices(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported slices: " + str(maxSupportedTiles))
    if (maxSupportedTiles < (tile_rows * tile_cols)):
      slash.skip_test("Number of tiles requested is not supported by underlying device.")
    maxSupportedBFrames = int(get_vainfo_num_lX_references(self.get_vaapi_profile(), "VAEntrypointEncSlice", "1", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported B frames: " + str(maxSupportedBFrames))
    if ((bframes > 0) and (maxSupportedBFrames == 0)):
      slash.skip_test("B frames are not supported by underlying device.")    
    if (tile_mode == 0) and not is_vainfo_slices_structure_supported(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice, "VA_ENC_SLICE_STRUCTURE_EQUAL_ROWS"): # Uniform
      slash.skip_test("Uniform tile mode not supported by underlying device.")
    if (tile_mode == 1) and not is_vainfo_slices_structure_supported(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice, "VA_ENC_SLICE_STRUCTURE_ARBITRARY_MACROBLOCKS"): # Arbitrary
      slash.skip_test("Arbitrary tile mode not supported by underlying device.")
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
  def test(self, case, gop, tile_rows, tile_cols, bframes, qp, quality, profile, tile_mode):
    self.init(spec, case, gop, tile_rows, tile_cols, bframes, qp, quality, profile, tile_mode)
    self.encode()

class cbr(AV1EncoderTest):
  def init(self, tspec, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode):
    vars(self).update(tspec[case].copy())
    maxSupportedTileRowsSupported = bool(get_vainfo_max_tile_rows(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][0])
    if (maxSupportedTileRowsSupported):
      maxSupportedTileRows=int(get_vainfo_max_tile_rows(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
      slash.logger.info("Underlying GPU max supported tile rows: " + str(maxSupportedTileRows))
      if (maxSupportedTileRows < tile_rows):
        slash.skip_test("Requested tile_rows higher than hardware supports.")

    maxSupportedTileColsSupported=bool(get_vainfo_max_tile_cols(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][0])
    if (maxSupportedTileColsSupported):
      maxSupportedTileCols=int(get_vainfo_max_tile_cols(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
      slash.logger.info("Underlying GPU max supported tile cols: " + str(maxSupportedTileCols))
      if (maxSupportedTileCols < tile_cols):
        slash.skip_test("Requested tile_cols higher than hardware supports.")

    maxSupportedTiles=int(get_vainfo_max_slices(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported slices: " + str(maxSupportedTiles))
    if (maxSupportedTiles < (tile_rows * tile_cols)):
      slash.skip_test("Number of tiles requested is not supported by underlying device.")
    maxSupportedBFrames = int(get_vainfo_num_lX_references(self.get_vaapi_profile(), "VAEntrypointEncSlice", "1", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported B frames: " + str(maxSupportedBFrames))
    if ((bframes > 0) and (maxSupportedBFrames == 0)):
      slash.skip_test("B frames are not supported by underlying device.")    
    if (tile_mode == 0) and not is_vainfo_slices_structure_supported(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice, "VA_ENC_SLICE_STRUCTURE_EQUAL_ROWS"): # Uniform
      slash.skip_test("Uniform tile mode not supported by underlying device.")
    if (tile_mode == 1) and not is_vainfo_slices_structure_supported(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice, "VA_ENC_SLICE_STRUCTURE_ARBITRARY_MACROBLOCKS"): # Arbitrary
      slash.skip_test("Arbitrary tile mode not supported by underlying device.")
    vars(self).update(
      bframes = bframes,
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
  def test(self, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode):
    self.init(spec, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode)
    self.encode()

class vbr(AV1EncoderTest):
  def init(self, tspec, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode):
    vars(self).update(tspec[case].copy())
    maxSupportedTileRowsSupported = bool(get_vainfo_max_tile_rows(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][0])
    if (maxSupportedTileRowsSupported):
      maxSupportedTileRows=int(get_vainfo_max_tile_rows(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
      slash.logger.info("Underlying GPU max supported tile rows: " + str(maxSupportedTileRows))
      if (maxSupportedTileRows < tile_rows):
        slash.skip_test("Requested tile_rows higher than hardware supports.")

    maxSupportedTileColsSupported=bool(get_vainfo_max_tile_cols(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][0])
    if (maxSupportedTileColsSupported):
      maxSupportedTileCols=int(get_vainfo_max_tile_cols(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
      slash.logger.info("Underlying GPU max supported tile cols: " + str(maxSupportedTileCols))
      if (maxSupportedTileCols < tile_cols):
        slash.skip_test("Requested tile_cols higher than hardware supports.")

    maxSupportedTiles=int(get_vainfo_max_slices(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported slices: " + str(maxSupportedTiles))
    if (maxSupportedTiles < (tile_rows * tile_cols)):
      slash.skip_test("Number of tiles requested is not supported by underlying device.")
    maxSupportedBFrames = int(get_vainfo_num_lX_references(self.get_vaapi_profile(), "VAEntrypointEncSlice", "1", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported B frames: " + str(maxSupportedBFrames))
    if ((bframes > 0) and (maxSupportedBFrames == 0)):
      slash.skip_test("B frames are not supported by underlying device.")    
    if (tile_mode == 0) and not is_vainfo_slices_structure_supported(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice, "VA_ENC_SLICE_STRUCTURE_EQUAL_ROWS"): # Uniform
      slash.skip_test("Uniform tile mode not supported by underlying device.")
    if (tile_mode == 1) and not is_vainfo_slices_structure_supported(self.get_vaapi_profile(), "VAEntrypointEncSlice", self.renderDevice, "VA_ENC_SLICE_STRUCTURE_ARBITRARY_MACROBLOCKS"): # Arbitrary
      slash.skip_test("Arbitrary tile mode not supported by underlying device.")      
    vars(self).update(
      bframes = bframes,
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
  def test(self, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode):
    self.init(spec, case, gop, bframes, tile_cols, tile_rows, bitrate, fps, quality, profile, tile_mode)
    self.encode()
