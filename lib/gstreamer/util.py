###
### Copyright (C) 2021 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from ...lib.common import memoize, try_call, try_call_with_output, call, exe2os
import os

@memoize
def have_gst():
  return try_call("which gst-launch-1.0") and try_call("which gst-inspect-1.0")

@memoize
def have_gst_element(element):
  result = try_call("gst-inspect-1.0 {}".format(element))
  return result, element

def gst_discover(filename):
  return call("gst-discoverer-1.0 {} -v".format(filename))

@memoize
def have_gst_version(versionStr):
  result = try_call_with_output("gst-launch-1.0 --version | grep version | cut -f3 -d' ' | xargs")
  installedVersion = str(result[1]).replace("\\n", "").replace("b", "").replace("\'", "")
  return bool(int(installedVersion.replace(".", "")) >= int(versionStr.replace(".", "")))

@memoize
def have_vainfo_entrypoint(profile, entrypoint, adapter_index):
  if "vaon12" == os.environ.get("LIBVA_DRIVER_NAME", None):
    result = try_call(f"powershell.exe {exe2os('vainfo')} --display win32 --device {adapter_index} 2>&1 | Select-String \"{profile} \" | Select-String \"{entrypoint}\" -Quiet", communicate=True)
  else:
    result = try_call(f"{exe2os('vainfo')} --display drm --device {adapter_index} 2>&1 | grep '{profile} ' | grep '{entrypoint}'")
  return result, "vainfo support for device:" + adapter_index + " " + profile + " " + entrypoint

@memoize
def get_vainfo_num_lX_references(profile, entrypoint, lX, adapter_index):
  if "vaon12" == os.environ.get("LIBVA_DRIVER_NAME", None):
    group_id = int(lX) + 2
    result = try_call_with_output(f"powershell.exe \"[regex]::match(({exe2os('vainfo')} -a --display win32 --device {adapter_index} 2>&1),'{profile}/{entrypoint}(.*?)l0=(.*?)l1=(.*?) (.*?)VAProfile').Groups[{group_id}].Value\"", use_shell = False)
    result = (result[0], str(result[1]).replace("b", "").replace("'", "").replace("\\n", "").replace("\\r", ""))
  else:
    result = try_call_with_output(f"{exe2os('vainfo')} -a --display drm --device {adapter_index} 2>&1 | sed -n -e '/{profile}\\/{entrypoint}/,/VAProfile/ p' | head -n -2 | grep 'l{lX}=' | cut -f2 -d=")
  return result, "vainfo support for device:" + adapter_index + " " + profile + " " + entrypoint + " num l{lX} references (" + str(result) + ")"

@memoize
def get_vainfo_max_slices(profile, entrypoint, adapter_index):
  if "vaon12" == os.environ.get("LIBVA_DRIVER_NAME", None):
    result = try_call_with_output(f"powershell.exe \"[regex]::match(({exe2os('vainfo')} -a --display win32 --device {adapter_index} 2>&1),'{profile}/{entrypoint}(.*?)VAConfigAttribEncMaxSlices(.*?):(.*?)VAConfigAttribEncSliceStructure(.*?)VAProfile').Groups[3].Value.Trim()\"", use_shell = False)
    result = (result[0], str(result[1]).replace("b", "").replace("'", "").replace("\\n", "").replace("\\r", ""))
  else:
    result = try_call_with_output(f"{exe2os('vainfo')} -a --display drm --device {adapter_index} 2>&1 | sed -n -e '/{profile}\\/{entrypoint}/,/VAProfile/ p' | head -n -2 | grep 'VAConfigAttribEncMaxSlices' | cut -f2 -d: | xargs")  
  if (result[1] == b'\n'):
    result = (True, 1)
  return result, "vainfo support for device:" + adapter_index + " " + profile + " " + entrypoint + " max slices (" + str(result) + ")"
