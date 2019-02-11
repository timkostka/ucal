"""Build a new PyPI release and upload it."""

import os
import re
import glob

####################
# START OF OPTIONS #
####################

# if True, major version will be incremented before building
increment_major_version = False

# if True, minor version will be incremented before building
increment_minor_version = False

# if True, build number will be incremented
increment_build_number = True

# if True, will pause before building
confirm_before_building = True

# if True, must run and pass unit tests
run_and_pass_unit_tests = True

# if True, git diff must return no changes
force_clean_git_diff = True

# if True, will commit changes after uploading
commit_after_uploading = True

# if True, will upload package to PyPI after building
upload_new_package = True

##################
# END OF OPTIONS #
##################

# ensure valid options configuration
if commit_after_uploading and not force_clean_git_diff:
    print('ERROR: invalid options')
    print('if commit_after_uploading is True, force_clean_git_diff must be '
          'True')
if not increment_build_number:
    print('ERROR: invalid options')
    print('increment_build_number must be True')


def get_package_directory():
    """Return the root directory of the package."""
    path = os.path.dirname(__file__)
    if not path:
        path = os.getcwd()
    while not os.path.isfile(os.path.join(path, 'setup.py')):
        new_path = os.path.dirname(path)
        assert new_path != path
        path = new_path
    return path


# get root directory
directory = get_package_directory()

# change to root directory
print(directory)
os.chdir(directory)

# run unit tests
if run_and_pass_unit_tests:
    print('\nRunning unit tests')
    files = []
    files.extend(glob.glob('test*/test*.py'))
    if not files:
        print('ERROR: no unit tests found')
        exit(1)
    for file in files:
        print('Running %s' % file)
        result = os.system('python %s' % file)
        if result != 0:
            print('ERROR: unit tests failed')
            exit(1)
    print('\nUnit tests passed')

# store the setup filename
setup_filename = 'setup.py'
assert os.path.isfile('setup.py')

# ensure clean git diff
if force_clean_git_diff:
    print('\nRunning git diff')
    result = os.system('git diff --exit-code')
    if result != 0:
        print('\nERROR: git diff shows uncommitted changes')
        exit(1)
    print('- No changes found')

# read the current version
with open(setup_filename, 'r') as f:
    text = f.read()
# read the current version
match = re.search(r'version=[\'"]([0-9]+[.][0-9]+[.][0-9]+)[\'"]', text)
if not match:
    print('ERROR: unable to find version number')
    exit(1)
version = match.group(1)
major, minor, build = [int(x) for x in version.split('.')]
# increment version
if increment_build_number:
    build += 1
if increment_minor_version:
    minor += 1
    build = 0
if increment_major_version:
    major += 1
    minor = 0
    build = 0
new_version = '.'.join(str(x) for x in [major, minor, build])
# create new text
new_text = text[:match.start(1)] + new_version + text[match.end(1):]

# print changes to be made
print('\nPackage directory: %s' % directory)
print('Version: %s --> %s' % (version, new_version))

# pause to  confirm changes
if confirm_before_building:
    input('\nPress Enter to continue...')

# overwrite setup file
with open(setup_filename, 'w') as f:
    f.write(new_text)

# build module
print('\nBuilding')
result = os.system('python setup.py bdist_wheel')
if result != 0:
    print('ERROR: build failed')
    exit(1)

# upload
if upload_new_package:
    print('\nUploading')
    result = os.system('python -m twine upload --skip-existing dist/*')
    if result != 0:
        print('ERROR: upload failed')
        exit(1)

if commit_after_uploading:
    result = os.system('git add setup.py')
    if result != 0:
        print('ERROR: error during git add')
        exit(1)
    os.system('git commit -m "uploaded v%s PyPI package"' % new_version)
    if result != 0:
        print('ERROR: error during git commit')
        exit(1)
    os.system('git push')
    if result != 0:
        print('ERROR: error during git push')
        exit(1)

print('\nSuccess!')
