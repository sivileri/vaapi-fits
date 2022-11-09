###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib.common import memoize, try_call, try_call_with_output, call, exe2os
from ...lib.formats import FormatMapper
import os
from lib.common import is_windows_libva_driver

@memoize
def have_ffmpeg():
  if is_windows_libva_driver():
    return try_call(f"powershell.exe {exe2os('ffmpeg')} | Select-String 'ffmpeg version' -Quiet", communicate=True)
  else:
    return try_call(f"which {exe2os('ffmpeg')}")

@memoize
def have_ffmpeg_hwaccel(accel):
  if is_windows_libva_driver():
    result = try_call(f"powershell.exe {exe2os('ffmpeg')} -hide_banner -hwaccels | Select-String {accel} -Quiet", communicate=True)
  else:
    result = try_call(f"{exe2os('ffmpeg')} -hide_banner -hwaccels | grep {accel}")
  return result, accel

@memoize
def have_ffmpeg_filter(name):
  if is_windows_libva_driver():
    result = try_call(f"powershell.exe {exe2os('ffmpeg')} -hide_banner -filters | Select-String {name} -Quiet", communicate=True)  
  else:
    result = try_call(f"{exe2os('ffmpeg')} -hide_banner -filters | awk '{{print $2}}' | grep -w {name}")
  return result, name  

@memoize
def have_ffmpeg_encoder(encoder):
  if is_windows_libva_driver():
    result = try_call(f"powershell.exe {exe2os('ffmpeg')} -hide_banner -encoders | Select-String {encoder} -Quiet", communicate=True)  
  else:
    result = try_call(f"{exe2os('ffmpeg')} -hide_banner -encoders | awk '{{print $2}}' | grep -w {encoder}")
  return result, encoder  

@memoize
def have_vainfo_entrypoint(profile, entrypoint, adapter_index):
  if is_windows_libva_driver():
    result = try_call(f"powershell.exe {exe2os('vainfo')} --display win32 --device {adapter_index} 2>&1 | Select-String \"{profile} \" | Select-String \"{entrypoint}\" -Quiet", communicate=True)
  else:
    result = try_call(f"{exe2os('vainfo')} --display drm --device {adapter_index} 2>&1 | grep '{profile} ' | grep '{entrypoint}'")
  return result, "vainfo support for device:" + adapter_index + " " + profile + " " + entrypoint

@memoize
def get_vainfo_num_lX_references(profile, entrypoint, lX, adapter_index):
  if is_windows_libva_driver():
    group_id = int(lX) + 2
    result = try_call_with_output(f"powershell.exe \"[regex]::match(({exe2os('vainfo')} -a --display win32 --device {adapter_index} 2>&1),'{profile}/{entrypoint}(.*?)l0=(.*?)l1=(.*?) (.*?)VAProfile').Groups[{group_id}].Value\"", use_shell = False)
    result = (result[0], str(result[1]).replace("b", "").replace("'", "").replace("\\n", "").replace("\\r", ""))
  else:
    result = try_call_with_output(f"{exe2os('vainfo')} -a --display drm --device {adapter_index} 2>&1 | sed -n -e '/{profile}\\/{entrypoint}/,/VAProfile/ p' | head -n -2 | grep 'l{lX}=' | cut -f2 -d=")
  return result, "vainfo support for device:" + adapter_index + " " + profile + " " + entrypoint + " num l{lX} references (" + str(result) + ")"

@memoize
def get_vainfo_max_slices(profile, entrypoint, adapter_index):
  if is_windows_libva_driver():
    result = try_call_with_output(f"powershell.exe \"[regex]::match(({exe2os('vainfo')} -a --display win32 --device {adapter_index} 2>&1),'{profile}/{entrypoint}(.*?)VAConfigAttribEncMaxSlices(.*?):(.*?)VAConfigAttribEncSliceStructure(.*?)VAProfile').Groups[3].Value.Trim()\"", use_shell = False)
    result = (result[0], str(result[1]).replace("b", "").replace("'", "").replace("\\n", "").replace("\\r", ""))
  else:
    result = try_call_with_output(f"{exe2os('vainfo')} -a --display drm --device {adapter_index} 2>&1 | sed -n -e '/{profile}\\/{entrypoint}/,/VAProfile/ p' | head -n -2 | grep 'VAConfigAttribEncMaxSlices' | cut -f2 -d: | xargs")  
  if (result[1] == b'\n'):
    result = (True, 1)
  return result, "vainfo support for device:" + adapter_index + " " + profile + " " + entrypoint + " max slices (" + str(result) + ")"

@memoize
def have_ffmpeg_decoder(decoder):
  if is_windows_libva_driver():
    result = try_call(f"powerhell.exe {exe2os('ffmpeg')} -hide_banner -decoders | Select-String {decoder} -Quiet", communicate=True)  
  else:
    result = try_call(f"{exe2os('ffmpeg')} -hide_banner -decoders | awk '{{print $2}}' | grep -w {decoder}")
  return result, decoder  

def ffmpeg_probe_resolution(filename):
  return call(
    f"{exe2os('ffprobe')} -v quiet -select_streams v:0"
    " -show_entries stream=width,height -of"
    f" csv=s=x:p=0 {filename}"
  ).strip().strip('x')

class BaseFormatMapper(FormatMapper):
  def get_supported_format_map(self):
    return {
      "I420"  : "yuv420p",
      "NV12"  : "nv12",
      "P010"  : "p010le",
      "P012"  : "p012",
      "I010"  : "yuv420p10le",
      "YUY2"  : "yuyv422",
      "422H"  : "yuv422p",
      "422V"  : "yuv440p",
      "444P"  : "yuv444p",
      "Y800"  : "gray8",
      "ARGB"  : "rgb32",
      "BGRA"  : "bgra",
      "Y210"  : "y210",
      "Y212"  : "y212",
      "Y410"  : "y410",
      "Y412"  : "y412",
      "AYUV"  : "0yuv", # 0yuv is same as microsoft AYUV except the alpha channel
    }
