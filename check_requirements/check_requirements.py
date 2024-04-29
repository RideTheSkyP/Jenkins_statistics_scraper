import os
import subprocess


parent_directory = os.path.abspath(os.path.join(os.getcwd(), '..'))

with open(f'{parent_directory}/requirements.txt') as f:
    required_packages = f.read().splitlines()

installed_packages = subprocess.check_output(['pip3', 'freeze']).decode().split('\n')
installed_package_names = [pkg for pkg in installed_packages]
missing_packages = [pkg for pkg in required_packages if pkg not in installed_package_names]


if missing_packages:
    print('These packages are missing:')
    print('\n'.join(missing_packages))
    exit(1)
else:
    print('All required packages are installed.')
