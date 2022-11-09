###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from .common import call
import os
from lib.common import is_windows_libva_driver

class Capture:
  def __init__(self):
    self.dmesg = list()

  def __dmesg(self):
    self.dmesg = ["system(dmesg): {}".format(i) for i in call(
      "dmesg", False).strip().split('\n')]

  def checkpoint(self):
    if is_windows_libva_driver():
      return ""
    else:
      last = len(self.dmesg)
      self.__dmesg()
      return '\n'.join(self.dmesg[last:]).strip()
