from os.path import dirname, basename

VERSION = '0.0.1'
PACKAGE_DIR = basename(dirname(__file__))

print(f"Package:{PACKAGE_DIR} Version:{VERSION}")