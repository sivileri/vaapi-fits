###
### Copyright (C) 2018-2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

import os
import re
import slash
import pathlib

from ...lib.common import timefn, get_media, call, exe2os, filepath2os, is_windows_libva_driver
from ...lib.metrics import calculate_psnr
from ...lib.ffmpeg.util import have_ffmpeg, ffmpeg_probe_resolution

@slash.requires(have_ffmpeg)
class BaseTranscoderTest(slash.Test):
  def before(self):
    super().before()
    self.refctx = []
    self.renderDevice = get_media().render_device

  def get_requirements_data(self, ttype, codec, mode):
    return  self.requirements[ttype].get(
      codec, {}).get(
        mode, (None, (False, "{}:{}:{}".format(ttype, codec, mode)), None))

  def get_decoder(self, codec, mode):
    _, _, decoder = self.get_requirements_data("decode", codec, mode)
    assert decoder is not None, "failed to find a suitable decoder: {}:{}".format(codec, mode)
    return decoder.format(**vars(self))

  def get_encoder(self, codec, mode):
    _, _, encoder = self.get_requirements_data("encode", codec, mode)
    assert encoder is not None, "failed to find a suitable encoder: {}:{}".format(codec, mode)
    return encoder.format(**vars(self))

  def get_vpp_scale(self, width, height, mode):
    if width is None and height is None:
      return None
    _, _, scale = self.get_requirements_data("vpp", "scale", mode)
    assert scale is not None, "failed to find a suitable vpp scaler: {}".format(mode)
    return scale.format(width = width or self.width, height = height or self.height)

  def get_codec_from_file_ext(self, ext):
    return {
      ".h264"  : "avc",
      ".h265"  : "hevc",
      ".av1"   : "av1",
    }.get(ext, "???")

  def get_file_ext(self, codec):
    return {
      "av1"            : "av1",
      "avc"            : "h264",
      "hevc"           : "h265",
      "hevc-8"         : "h265",
      "mpeg2"          : "m2v",
      "mjpeg"          : "mjpeg",
    }.get(codec, "???")

  def validate_caps(self):
    assert len(self.outputs), "Invalid test case specification, outputs data empty"
    assert self.mode in ["sw", "hw", "lp"], "Invalid test case specification as mode type not valid"

    icaps, ireq, _ =  self.get_requirements_data("decode", self.codec, self.mode)
    requires = [ireq,]

    if icaps is None:
      slash.skip_test(
        "decode.{codec}.{mode} unsupported".format(**vars(self)))

    maxw, maxh = icaps["maxres"]
    if self.width > maxw or self.height > maxh:
      slash.skip_test(
        "decode.{codec}.{mode}.{width}x{height} unsupported".format(**vars(self)))

    for output in self.outputs:
      codec = output["codec"]
      mode  = output["mode"]
      assert mode in ["sw", "hw", "lp"], "Invalid test case specification as output mode type not valid"
      ocaps, oreq, _ = self.get_requirements_data("encode", codec, mode)
      requires.append(oreq)

      if ocaps is None:
        slash.skip_test(
          "encode.{codec}.{mode} unsupported".format(codec = codec, mode = mode))

      maxw, maxh = ocaps["maxres"]
      w = output.get("width", None)
      h = output.get("height", None)
      if (w or self.width) > maxw or (h or self.height) > maxh:
        slash.skip_test(
          "encode.{codec}.{mode}.{width}x{height} unsupported".format(
            codec = codec, mode = mode,
            width = (w or self.width),
            height = (h or self.height)))

      if w is not None or h is not None:
        ocaps, oreq, _ = self.get_requirements_data("vpp", "scale", mode)
        requires.append(oreq)

        if ocaps is None:
          slash.skip_test(
            "vpp.scale.{mode} unsupported".format(mode = mode))

    # check required
    unmet = set([m for t,m in requires if not t])
    if len(unmet) != 0:
      slash.skip_test(
        "Missing one or more required ffmpeg elements: {}".format(list(unmet)))

  def gen_input_opts(self):
    opts = "-init_hw_device {hwaccel}=hw:{renderDevice}"
    opts += " -hwaccel_output_format {hwaccel}"
    opts += " -filter_hw_device hw"
    if "hw" == self.mode:
      opts += " -hwaccel {hwaccel}"

    source_codec = self.get_codec_from_file_ext(pathlib.Path(filepath2os(self.source)).suffix)
    if source_codec != "???" and source_codec != self.codec:
      opts += " -c:v {}".format(self.get_decoder(source_codec, self.mode))
    else:
      opts += " -c:v {}".format(self.get_decoder(self.codec, self.mode))
    opts += f" -i {filepath2os(self.source)}"

    return opts.format(**vars(self))

  def gen_output_opts(self):
    self.goutputs = dict()

    opts = "-an -vsync passthrough"

    for n, output in enumerate(self.outputs):
      codec = output["codec"]
      mode = output["mode"]
      encoder = self.get_encoder(codec, mode)
      ext = self.get_file_ext(codec)

      # WA: LDB is not enabled by default for HEVCe on gen11+, yet.
      if codec.startswith("hevc") and get_media()._get_gpu_gen() > 10:
        encoder += " -b_strategy 1"
      if "lp" == mode:
        encoder += " -low_power 1"

      filters = []
      tmode = (self.mode, mode)

      if ("hw", "sw") == tmode:   # HW to SW transcode
        filters.extend(["hwdownload", "format=nv12"])
      elif ("sw", "hw") == tmode: # SW to HW transcode
        filters.extend(["format=nv12", "hwupload"])
        if vars(self).get("hwframes", None) is not None:
          filters[-1] += "=extra_hw_frames={hwframes}"

      self.rcmode = output.get("rcmode", None)
      if self.rcmode is not None:
        opts += " -rc_mode {rcmode}"
        if (self.rcmode.upper() == "CBR"):
          self.rc_avg_bitrate = output.get("avg_bitrate", None)
          opts += " -b:v {rc_avg_bitrate}k"
        elif (self.rcmode.upper() == "VBR"):
          self.rc_avg_bitrate = output.get("avg_bitrate", None)
          opts += " -b:v {rc_avg_bitrate}k"
          self.rc_peak_bitrate = output.get("max_bitrate", None)
          opts += " -maxrate {rc_peak_bitrate}k"
        elif (self.rcmode.upper() == "QVBR"):
          self.rc_avg_bitrate = output.get("avg_bitrate", None)
          opts += " -b:v {rc_avg_bitrate}k"
          self.rc_peak_bitrate = output.get("max_bitrate", None)
          opts += " -maxrate {rc_peak_bitrate}k"
          self.qvbr_quality = output.get("qvbr_quality", None)
          opts += " -global_quality {qvbr_quality}"
        else:
          print(self.rcmode)
          assert False # Unsupported RC mode for transcode

        self.rc_max_frame_size = output.get("rc_max_frame_size_bytes", None)
        if self.rc_max_frame_size is not None:
          opts += " -max_frame_size {rc_max_frame_size}" # this is in bytes

        self.bufsize = output.get("rc_buffer_size", None)
        if self.bufsize is not None:
          opts += " -bufsize {bufsize}k"

        self.rc_init_occupancy = output.get("rc_init_occupancy", None)
        if self.rc_init_occupancy is not None:
          opts += " -rc_init_occupancy {rc_init_occupancy}k"

        self.framerate = output.get("fps", None)
        if self.framerate is not None:
          opts += " -framerate {framerate}"

        self.qmin = output.get("qmin", None)
        if self.qmin is not None:
          opts += " -qmin {qmin}"

        self.qmax = output.get("qmax", None)
        if self.qmax is not None:
          opts += " -qmax {qmax}"

      vppscale = self.get_vpp_scale(
        output.get("width", None), output.get("height", None), mode)
      if vppscale is not None:
        filters.append(vppscale)

      for channel in range(output.get("channels", 1)):
        ofile = get_media()._test_artifact(
          "{}_{}_{}.{}".format(self.case, n, channel, ext))
        self.goutputs.setdefault(n, list()).append(ofile)
        osofile = filepath2os(ofile)

        if len(filters):
          opts += " -vf \"{}\"".format(','.join(filters))
        opts += " -c:v {}".format(encoder)
        opts += " -vframes {frames}"
        opts += " -y {}".format(osofile)

    # dump decoded source to yuv for reference comparison
    self.srcyuv = get_media()._test_artifact(
      "src_{case}.yuv".format(**vars(self)))
    self.ossrcyuv = filepath2os(self.srcyuv)
    if "hw" == self.mode:
      opts += " -vf \"hwdownload,format=nv12\""
    opts += " -pix_fmt yuv420p -f rawvideo"
    opts += " -vframes {frames} -y {ossrcyuv}"

    opts += " -loglevel trace"
    return opts.format(**vars(self))

  def check_output(self):
    m = re.search(
      "not supported for hardware decode", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

    m = re.search(
      "hwaccel initialisation returned error", self.output, re.MULTILINE)
    assert m is None, "Failed to use hardware decode"

    # rate control mode
    if self.rcmode is not None:
      rcmsgs = dict(
        cqp = (
          "Using constant-quality mode"
          "|RC mode: CQP"
          "|Driver does not report any supported rate control modes: assuming constant-quality"
        ),
        cbr = "RC mode: CBR",
        vbr = "RC mode: VBR",
        qvbr = "RC mode: QVBR",
      )
      m = re.search(rcmsgs[self.rcmode.lower()], self.output, re.MULTILINE)
      assert m is not None, "Possible incorrect RC mode used"
      if self.rcmode == "QVBR":
        m = re.search("RC quality: {qvbr_quality}".format(**vars(self)), self.output, re.MULTILINE)
        assert m is not None, "Possible incorrect RC Quality Value used"

      if self.rc_max_frame_size is not None:
        m = re.search("Set max frame size: {rc_max_frame_size} bytes.".format(**vars(self)), self.output, re.MULTILINE)
        assert m is not None, "Possible incorrect RC max_frame_size used"

      if self.bufsize is not None:
        assert self.rc_init_occupancy is not None
        # Put 000 to convert from "{bufsize}k" in command line
        m = re.search("RC buffer: {bufsize}000 bits, initial fullness {rc_init_occupancy}000 bits.".format(**vars(self)), self.output, re.MULTILINE)
        assert m is not None, "Possible incorrect RC VBV buffer values used"

      # ffmpeg sometimes rounds the argument, disable check
      #if self.framerate is not None:
      #  m = re.search("RC framerate: {framerate}/1".format(**vars(self)), self.output, re.MULTILINE)
      #  assert m is not None, "Possible incorrect RC frame rate used"

  @timefn("ffmpeg")
  def call_ffmpeg(self, iopts, oopts, envvars = "", undoenvvars=""):
    return call(f"{envvars} {exe2os('ffmpeg')}"
                " -v verbose {} {}".format(iopts, oopts)
                + f" {undoenvvars}")

  def transcode(self):
    self.validate_caps()
    iopts = self.gen_input_opts()
    oopts = self.gen_output_opts()

    get_media().test_call_timeout = vars(self).get("call_timeout", 0)

    if is_windows_libva_driver():
      envvars = "powershell.exe "
      undoenvvars = ";"
      # We are testing the actual encoding VBV params here, so disable any overriding
      if self.rcmode is not None:
        envvars += "$env:backup_D3D12_VIDEO_ENC_CBR_FORCE_VBV_EQUAL_BITRATE=$env:D3D12_VIDEO_ENC_CBR_FORCE_VBV_EQUAL_BITRATE;"
        envvars += "$env:D3D12_VIDEO_ENC_CBR_FORCE_VBV_EQUAL_BITRATE=\"0\";"
        undoenvvars += "$env:D3D12_VIDEO_ENC_CBR_FORCE_VBV_EQUAL_BITRATE=$env:backup_D3D12_VIDEO_ENC_CBR_FORCE_VBV_EQUAL_BITRATE;"
    else:
      envvars = "env "
      undoenvvars = ""
      # We are testing the actual encoding VBV params here, so disable any overriding
      if self.rcmode is not None:
        envvars += "D3D12_VIDEO_ENC_CBR_FORCE_VBV_EQUAL_BITRATE=0"

    self.output = self.call_ffmpeg(iopts, oopts, envvars.format(**vars(self)), undoenvvars.format(**vars(self)))
    self.check_output()

    for n, output in enumerate(self.outputs):
      get_media()._set_test_details(**{"output.{}".format(n) : output})
      for channel in range(output.get("channels", 1)):
        encoded = self.goutputs[n][channel]
        osencoded = filepath2os(encoded)
        yuv = get_media()._test_artifact(
          "{}_{}_{}.yuv".format(self.case, n, channel))
        osyuv = filepath2os(yuv)
        vppscale = self.get_vpp_scale(self.width, self.height, "sw")
        iopts = "-i {}"
        oopts = "-vf \"{}\" -pix_fmt yuv420p -f rawvideo -vframes {} -y {}"
        self.call_ffmpeg(
          iopts.format(osencoded), oopts.format(vppscale, self.frames, osyuv))
        if self.rcmode is not None:
          self.check_bitrate(output, osencoded)
        self.check_resolution(output, osencoded)
        self.check_metrics(yuv, refctx = [(n, channel)])
        # delete yuv file after each iteration
        get_media()._purge_test_artifact(yuv)

  def check_resolution(self, output, encoded):
    actual = ffmpeg_probe_resolution(encoded)
    expect = "{}x{}".format(
      output.get("width", self.width), output.get("height", self.height))
    assert expect == actual

  def check_bitrate(self, output, encoded):
    encsize = os.path.getsize(encoded)
    bitrate_actual = encsize * 8 * vars(self).get("fps", 25) / 1024.0 / self.frames
    get_media()._set_test_details(
      size_encoded = encsize,
      bitrate_actual = "{:-.2f}".format(bitrate_actual))

    if "cbr" == self.rcmode:
      bitrate_gap = abs(bitrate_actual - self.bitrate) / self.bitrate
      get_media()._set_test_details(bitrate_gap = "{:.2%}".format(bitrate_gap))

      # acceptable bitrate within 13% of bitrate
      if (os.environ.get('D3D12_VAAPIFITS_IGNORE_BITRATE_GAP') == None):
        assert(bitrate_gap <= 0.13)

    elif (("vbr" == self.rcmode) or ("qvbr" == self.rcmode)):
      # acceptable bitrate within 25% of minrate and 10% of maxrate
      assert(self.minrate * 0.75 <= bitrate_actual <= self.maxrate * 1.10)

  def check_metrics(self, yuv, refctx):
    get_media().baseline.check_psnr(
      psnr = calculate_psnr(
        self.srcyuv, yuv,
        self.width, self.height,
        self.frames),
      context = self.refctx + refctx,
    )
