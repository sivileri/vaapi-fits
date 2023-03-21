###
### Copyright (C) 2018-2019 Intel Corporation
###
### SPDX-License-Identifier: BSD-3-Clause
###

from datetime import datetime as dt
import functools
import os
import slash
import subprocess
import threading
import time

def is_windows_libva_driver():
  vaDrvName = os.environ.get("LIBVA_DRIVER_NAME", None)
  return ("vaon12" == vaDrvName) or ("vaon12_warp" == vaDrvName)

def sorted_by_resolution(cases):
  size = lambda kv: kv[1]["width"] * kv[1]["height"]
  return [kv[0] for kv in sorted(cases.items(), key = size)]

def timefn(label):
  def count(function):
    # Keep track of the number of times this function was called from the
    # current test context.  This allows us to use a unique label for the
    # test details.
    count = get_media()._test_state_value(function, 0)
    count.value += 1
    return count.value

  def inner(function):
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
      start = dt.now()
      try:
        ret = function(*args, **kwargs)
      except:
        raise
      finally:
        stotal = (dt.now() - start).total_seconds()
        kdetail = "time({}:{})".format(label, count(function))
        get_media()._set_test_details(**{kdetail : "{:.4f}s".format(stotal)})
      return ret
    return wrapper

  return inner

def parametrize_with_unused(names, values, unused):
  def inner(func):
    used = vars(func).setdefault("__params_used__", list())
    @functools.wraps(func)
    @slash.parametrize(names, sorted(values))
    def wrapper(*args, **kwargs):
      params = kwargs.copy()
      for param in unused:
        slash.logger.notice("NOTICE: '{}' parameter unused".format(param))
        del params[param]
      if params in used:
        slash.skip_test("Test case is redundant")
      used.append(params)
      func(*args, **kwargs)
    return wrapper
  return inner

class memoize:
  def __init__(self, function):
    self.function = function
    self.memoized = {}

  def __call__(self, *args):
    try:
      return self.memoized[args]
    except KeyError:
      r = self.function(*args)
      self.memoized[args] = r
      return r

  def __repr__(self):
    return str(self.function.__name__)

@memoize
def get_media():
  return slash.plugins.manager.get_plugin("media")

def killproc(proc):
  result = proc.poll()
  if result is not None:
    return result

  # try to 'gently' terminate proc
  proc.terminate()
  for i in range(5):
    result = proc.poll()
    if result is not None:
      return result
    time.sleep(1) # wait a little longer for proc to terminate

  # failed to terminate proc, so kill it
  proc.kill()
  for i in range(10):
    result = proc.poll()
    if result is not None:
      return result
    time.sleep(1) # give system more time to kill proc

  # failed to kill proc
  if result is None:
    slash.logger.warn('Failed to kill process with pid {}'.format(proc.pid))

  return result

def startproc(command, logger = slash.logger.debug):
  # Without "exec", the shell will launch the "command" in a child process and
  # proc.pid will represent the shell (not the "command").  And therefore, the
  # "command" will not get killed with proc.terminate() or proc.kill().
  #
  # When we use "exec" to run the "command". This will cause the "command" to
  # inherit the shell process and proc.pid will represent the actual "command".
  command_prefix = ""
  if not is_windows_libva_driver():
    command_prefix = "exec "
  proc = subprocess.Popen(
    command_prefix + command,
    stdin = subprocess.PIPE,
    stdout = subprocess.PIPE,
    stderr = subprocess.STDOUT,
    shell = True,
    universal_newlines = True)

  logger("CALL: {} (pid: {})".format(command, proc.pid))

  return proc

def call(command, withSlashLogger = True, ignore_proc_code = False):

  ignore_proc_code = ignore_proc_code or (os.environ.get('D3D12_VAAPIFITS_IGNORE_EXITCODE') != None)

  calls_allowed = get_media()._calls_allowed()
  assert calls_allowed, "call refused"

  if withSlashLogger:
    logger = slash.logger.debug
  else:
    logger = lambda x: None

  def readproc(proc):
    for line in iter(proc.stdout.readline, ''):
      readproc.output += line
      logger(line.rstrip('\n'))
  readproc.output = ""

  def timeout(proc):
    timeout.triggered = proc.poll() is None
    killproc(proc)
  timeout.triggered = False

  error = False
  message = ""

  proc = startproc(command, logger)

  reader = threading.Thread(target = readproc, args = [proc])
  timer = threading.Timer(get_media()._get_call_timeout(), timeout, [proc])
  reader.daemon = True
  timer.daemon = True
  reader.start()
  timer.start()

  try: # in case of user interrupt
    proc.wait()
    timer.cancel()
  except:
    killproc(proc)
    raise
  finally:
    timer.cancel()
    timer.join(30)
    reader.join(30)
    proc.stdin.close()
    proc.stdout.close()

  if timeout.triggered:
    error = True
    get_media()._report_call_timeout()
    message = "CALL TIMEOUT: timeout after {} seconds (pid: {}).".format(
      timer.interval, proc.pid)
  elif (not ignore_proc_code and (proc.returncode != 0)):
    error = True
    message = "CALL ERROR: failed with exitcode {} (pid: {})".format(proc.returncode, proc.pid)

  assert not error, message
  return readproc.output

def try_call_with_output(command, use_shell = True):
  proc_out=""
  try:
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.STDOUT, shell=use_shell)
    proc_out = proc.communicate()[0]
    return proc_out != b'', proc_out
  except:
    return False, proc_out
  return True, proc_out


def try_call(command, communicate=False):
  try:
    if(communicate):
      proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr = subprocess.STDOUT)
      proc_out = proc.communicate()[0]
      return proc_out != b''
    else:
      subprocess.check_output(command, stderr = subprocess.STDOUT, shell = True)
  except:
    return False
  return True

def mapRange(value, srcRange, destRange):
  (smin, smax), (dmin, dmax) = srcRange, destRange
  return dmin + ((value - smin) * (dmax - dmin) / (smax - smin))

def mapRangeInt(value, srcRange, destRange):
  (smin, smax), (dmin, dmax) = srcRange, destRange
  return int(dmin + ((value - smin) * (dmax - dmin) // (smax - smin)))

def mapRangeWithDefault(value, srcRange, dstRange):
  # Normalizes a value from the source range into the destination range,
  # taking the midpoint/default of each range into account.
  smin, smid, smax = srcRange
  dmin, dmid, dmax = dstRange
  if value < smid:
    return (value - smin) / (smid - smin) * (dmid - dmin) + dmin
  return (value - smid) / (smax - smid) * (dmax - dmid) + dmid

# some path helpers
def abspath(path):
  if is_windows_libva_driver():
    return os.path.abspath(path).lstrip(os.path.sep)
  else:
    return os.path.sep + os.path.abspath(path).lstrip(os.path.sep)

def pathexists(path):
  return os.path.exists(abspath(path))

def makepath(path):
  if not pathexists(path):
    os.makedirs(abspath(path))

@memoize
def exe2os(name):
  if is_windows_libva_driver():
    return f"{name}.exe"
  elif "linux" == get_media()._get_os():
    return f"{name}"
  elif "wsl" == get_media()._get_os():
    return f"{name}"
  else:
    return f"{name}.exe"

@memoize
def filepath2os(file_path):
  return file_path
