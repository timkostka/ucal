"""
This script compiles the GUI into a self-contained EXE using PyInstaller.

"""

import os
import sys
import shutil
import datetime

####################
# START OF OPTIONS #
####################

# if True, hide the console
hide_console = True

# if True, upload file to the network
upload_to_network = True

##################
# END OF OPTIONS #
##################

# path to the network EXE location
network_exe_location = (
    r"\\snlca\collaborative\JTA & Mech Systems\Unit Calculator"
)

# path of the EXE to create
exe_path = os.path.abspath("./dist/unit_calculator.exe")

# get Python EXE location
python_exe = os.path.abspath(sys.executable)
assert os.path.isfile(python_exe)

# get PyInstaller EXE location
pyinstaller_exe = os.path.join(os.path.dirname(python_exe), "pyinstaller.exe")
assert os.path.isfile(pyinstaller_exe)

# delete existing EXE
if os.path.isfile(exe_path):
    os.remove(exe_path)

# date assignement line
date_assignment = 'u"Software version: '

# replace software date with todays date
# new_date = datetime.datetime.now().strftime("%B %#d, %Y @ %#I:%M %p")
# print("Replacing software date as %s" % new_date)
# # read original code
# with open("hdr_readout_form_base.py", "r") as f:
#     code = f.read()
# # replace date with current date
# assert date_assignment in code
# before = code[: code.index(date_assignment)]
# after = code[code.index(date_assignment) + len(date_assignment) :]
# after = after[after.index("\n") :]
# new_code = before + date_assignment + '%s",' % new_date + after
# # replace with new code
# with open("hdr_readout_form_base.py", "w") as f:
#     f.write(new_code)

# create the EXE
arguments = [
    '"%s"' % pyinstaller_exe,
    "-n unit_calculator",
    "--clean",
    "--noconsole" if hide_console else "",
    "--onefile",
    "-i ucal_gui/ucal.ico",
    "--add-data ucal_gui/ucal.ico;.",
    "start_ucal_gui.py",
]
print("Running command:")
print(" ".join(arguments))
os.system(" ".join(arguments))

# if file wasn't created, something went wrong
if not os.path.isfile(exe_path):
    print("\nERROR: could not create EXE file")
    exit(1)

# report success
mb = os.path.getsize(exe_path) / 1024 ** 2
print("\nStandalone EXE (%.2f MB) created" % mb)
print("%s" % exe_path)

# upload if requested
if upload_to_network:
    print("\nUploading EXE to network drive...")
    if os.path.isfile(network_exe_location):
        print("- Deleted old EXE")
        os.remove(network_exe_location)
    shutil.copy2(exe_path, network_exe_location)
    print("- EXE copied to %s" % network_exe_location)
