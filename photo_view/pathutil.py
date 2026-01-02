import pathlib

package_root = pathlib.Path(__file__).resolve().parents[1]

def resolvePackagePath( relative_path ):
    path = package_root/relative_path
    return str(path)
