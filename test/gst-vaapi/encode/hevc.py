###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ....lib import *
from ....lib.gstreamer.vaapi.util import *
from ....lib.gstreamer.vaapi.encoder import EncoderTest

spec      = load_test_spec("hevc", "encode", "8bit")
spec_r2r  = load_test_spec("hevc", "encode", "8bit", "r2r")

@slash.requires(*have_gst_element("vaapih265enc"))
@slash.requires(*have_gst_element("vaapih265dec"))
class HEVC8EncoderBaseTest(EncoderTest):
  def before(self):
    super().before()
    vars(self).update(
      codec         = "hevc-8",
      gstencoder    = "vaapih265enc",
      gstdecoder    = "vaapih265dec",
      gstmediatype  = "video/x-h265",
      gstparser     = "h265parse",
    )
    hasSupport = have_vainfo_entrypoint("VAProfileHEVCMain", "VAEntrypointEncSlice", self.renderDevice)
    if(not hasSupport[0]):
      slash.skip_test(hasSupport[1])
    if not have_gst_version("1.23.0"):
      slash.skip_test("Gstreamer does not query VAConfigAttribValEncHEVCBlockSizes or VAConfigAttribEncHEVCFeatures which is needed for D3D12/VA.")

  def get_file_ext(self):
    return "h265"

@slash.requires(*platform.have_caps("encode", "hevc_8"))
class HEVC8EncoderTest(HEVC8EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("encode", "hevc_8"),
      lowpower  = False,
    )

@slash.requires(*platform.have_caps("vdenc", "hevc_8"))
class HEVC8EncoderLPTest(HEVC8EncoderBaseTest):
  def before(self):
    super().before()
    vars(self).update(
      caps      = platform.get_caps("vdenc", "hevc_8"),
      lowpower  = True,
    )

class cqp(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, qp, quality, profile):
    vars(self).update(tspec[case].copy())
    maxSupportedSlices=int(get_vainfo_max_slices("VAProfileHEVCMain", "VAEntrypointEncSlice", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported slices: " + str(maxSupportedSlices))
    if (maxSupportedSlices < slices):
      slash.skip_test("Number of slices requested is not supported by underlying device.")
    maxSupportedBFrames = int(get_vainfo_num_lX_references("VAProfileHEVCMain", "VAEntrypointEncSlice", "1", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported B frames: " + str(maxSupportedBFrames))
    if ((bframes > 0) and (maxSupportedBFrames == 0)):
      slash.skip_test("B frames are not supported by underlying device.")    
    vars(self).update(
      bframes = bframes,
      case    = case,
      gop     = gop,
      qp      = qp,
      quality = quality,
      profile = profile,
      rcmode  = "cqp",
      slices  = slices,
    )

  @slash.parametrize(*gen_hevc_cqp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec, case, gop, slices, bframes, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cqp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, bframes, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cqp_lp(HEVC8EncoderLPTest):
  def init(self, tspec, case, gop, slices, qp, quality, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      case         = case,
      gop          = gop,
      qp           = qp,
      quality      = quality,
      profile      = profile,
      rcmode       = "cqp",
      slices       = slices,
    )

  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, qp, quality, profile):
    self.init(spec, case, gop, slices, qp, quality, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cqp_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, qp, quality, profile):
    self.init(spec_r2r, case, gop, slices, qp, quality, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, profile):
    vars(self).update(tspec[case].copy())
    maxSupportedSlices=int(get_vainfo_max_slices("VAProfileHEVCMain", "VAEntrypointEncSlice", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported slices: " + str(maxSupportedSlices))
    if (maxSupportedSlices < slices):
      slash.skip_test("Number of slices requested is not supported by underlying device.")
    maxSupportedBFrames = int(get_vainfo_num_lX_references("VAProfileHEVCMain", "VAEntrypointEncSlice", "1", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported B frames: " + str(maxSupportedBFrames))
    if ((bframes > 0) and (maxSupportedBFrames == 0)):
      slash.skip_test("B frames are not supported by underlying device.")    
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
      slices  = slices,
    )

  @slash.parametrize(*gen_hevc_cbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cbr_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class cbr_lp(HEVC8EncoderLPTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate      = bitrate,
      case         = case,
      fps          = fps,
      gop          = gop,
      maxrate      = bitrate,
      minrate      = bitrate,
      profile      = profile,
      rcmode       = "cbr",
      slices       = slices,
    )

  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec, case, gop, slices, bitrate, fps, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_cbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr(HEVC8EncoderTest):
  def init(self, tspec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    vars(self).update(tspec[case].copy())
    maxSupportedSlices=int(get_vainfo_max_slices("VAProfileHEVCMain", "VAEntrypointEncSlice", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported slices: " + str(maxSupportedSlices))
    if (maxSupportedSlices < slices):
      slash.skip_test("Number of slices requested is not supported by underlying device.")
    maxSupportedBFrames = int(get_vainfo_num_lX_references("VAProfileHEVCMain", "VAEntrypointEncSlice", "1", self.renderDevice)[0][1])
    slash.logger.info("Underlying GPU max supported B frames: " + str(maxSupportedBFrames))
    if ((bframes > 0) and (maxSupportedBFrames == 0)):
      slash.skip_test("B frames are not supported by underlying device.")    
    vars(self).update(
      bframes = bframes,
      bitrate = bitrate,
      case    = case,
      fps     = fps,
      gop     = gop,
      ## target percentage 70% (hard-coded in gst-vaapi)
      ## gst-vaapi sets max-bitrate = bitrate and min-bitrate = bitrate * 0.70
      maxrate = int(bitrate / 0.7),
      minrate = bitrate,
      profile = profile,
      quality = quality,
      rcmode  = "vbr",
      refs    = refs,
      slices  = slices,
    )

  @slash.parametrize(*gen_hevc_vbr_parameters(spec, ['main']))
  def test(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_vbr_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bframes, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bframes, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()

class vbr_lp(HEVC8EncoderLPTest):
  def init(self, tspec, case, gop, slices, bitrate, fps, quality, refs, profile):
    vars(self).update(tspec[case].copy())
    vars(self).update(
      bitrate      = bitrate,
      case         = case,
      fps          = fps,
      gop          = gop,
      ## target percentage 70% (hard-coded in gst-vaapi)
      ## gst-vaapi sets max-bitrate = bitrate and min-bitrate = bitrate * 0.70
      maxrate      = int(bitrate / 0.7),
      minrate      = bitrate,
      profile      = profile,
      quality      = quality,
      rcmode       = "vbr",
      refs         = refs,
      slices       = slices,
    )

  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec, ['main']))
  def test(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec, case, gop, slices, bitrate, fps, quality, refs, profile)
    self.encode()

  @slash.parametrize(*gen_hevc_vbr_lp_parameters(spec_r2r, ['main']))
  def test_r2r(self, case, gop, slices, bitrate, fps, quality, refs, profile):
    self.init(spec_r2r, case, gop, slices, bitrate, fps, quality, refs, profile)
    vars(self).setdefault("r2r", 5)
    self.encode()
