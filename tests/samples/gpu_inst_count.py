import os
import subprocess
import sys

from samples import dpc_gemm
from samples import cl_gemm
from samples import ze_gemm
import utils

def config(path):
  cmake = ["cmake",\
    "-DCMAKE_BUILD_TYPE=" + utils.get_build_flag(), ".."]
  stdout, stderr = utils.run_process(cmake, path)
  if stderr and stderr.find("CMake Error") != -1:
    return stderr
  return None

def build(path):
  stdout, stderr = utils.run_process(["make"], path)
  if stderr and stderr.lower().find("error") != -1:
    return stderr
  return None

def parse(output):
  lines = output.split("\n")
  total_count = 0
  for line in lines:
    if line.find("[INFO]") != -1:
      continue
    if line.find("[") != 0:
      continue
    items = line.split("]")
    if len(items) == 2:
      if items[0].strip() and items[1].strip():
        count = int(items[0].lstrip("[").strip())
        if count < 0:
          return False
        total_count += count
  if total_count <= 0:
    return False
  return True

def run(path, option):
  if option == "cl":
    app_folder = utils.get_sample_executable_path("cl_gemm")
    app_file = os.path.join(app_folder, "cl_gemm")
    command = ["./gpu_inst_count", app_file, "gpu", "1024", "1"]
  elif option == "ze":
    app_folder = utils.get_sample_executable_path("ze_gemm")
    app_file = os.path.join(app_folder, "ze_gemm")
    command = ["./gpu_inst_count", app_file, "1024", "1"]
  else:
    app_folder = utils.get_sample_executable_path("dpc_gemm")
    app_file = os.path.join(app_folder, "dpc_gemm")
    command = ["./gpu_inst_count", app_file, "gpu", "1024", "1"]
  stdout, stderr = utils.run_process(command, path)
  if not stdout:
    return "stdout is empty"
  if not stderr:
    return "stderr is empty"
  if stdout.find(" CORRECT") == -1:
    return stdout
  if stderr.find("add") == -1 or stderr.find("mov") == -1 or stderr.find("send") == -1:
    return stderr
  if not parse(stderr):
    return stderr
  return None

def main(option):
  path = utils.get_sample_build_path("gpu_inst_count")
  if option == "cl":
    log = cl_gemm.main("gpu")
    if log:
      return log
  elif option == "ze":
    log = ze_gemm.main(None)
    if log:
      return log
  else:
    log = dpc_gemm.main("gpu")
    if log:
      return log
  log = config(path)
  if log:
    return log
  log = build(path)
  if log:
    return log
  log = run(path, option)
  if log:
    return log

if __name__ == "__main__":
  option = "cl"
  if len(sys.argv) > 1 and sys.argv[1] == "ze":
    option = "ze"
  if len(sys.argv) > 1 and sys.argv[1] == "dpc":
    option = "dpc"
  log = main(option)
  if log:
    print(log)