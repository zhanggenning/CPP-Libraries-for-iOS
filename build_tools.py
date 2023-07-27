import os
import sys
import requests
import tarfile
import shutil
import plistlib
import subprocess
from shutil import rmtree


def remove_dir(path):
    if os.path.exists(path):
        rmtree(path)


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def download_file(url, target_dir):
    requests.packages.urllib3.disable_warnings()
    filename = url.split('/')[-1]
    target_file = f'{target_dir}/{filename}'
    print(f'Begin download package: {filename}')
    with requests.get(url, verify=False, stream=True) as r:
        r.raise_for_status()
        with open(target_file, 'wb') as f:
            total_length = int(r.headers.get('content-length'))
            downloaded = 0
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                print(f'Downloaded {downloaded / total_length * 100}%')

    if not os.path.exists(target_file):
        raise Exception(f'{target_file} down failed!', 1000)

    return target_file


def uncompress_file(file, target_dir):
    filename = file.split('/')[-1]
    target_dir_name = target_dir.split('/')[-1]
    target_dir_root = os.path.dirname(os.path.normpath(target_dir))
    top_dir_name = target_dir_name
    print(f'Begin uncompress package: {filename}')

    with tarfile.open(file, 'r:gz') as tar:
        names = tar.getnames()
        top_dir_name = os.path.commonprefix(names)
        tar.extractall(target_dir_root)

    if top_dir_name and top_dir_name != target_dir_name:
        os.rename(f'{target_dir_root}/{top_dir_name}', f'{target_dir_root}/{target_dir_name}')

def fetch_source_code(url, local_dir):
    print("Start check source code ...")
    if os.path.exists(local_dir):
        print('Check Source code: ok!')
        return

    print(f"Start fetch {url.split('/')[-1]} ...")
    local_root = os.path.dirname(os.path.normpath(local_dir))
    create_dir(local_root)

    # Download
    package = download_file(url, local_root)

    # Uncompress
    uncompress_file(package, local_dir)
    os.remove(package)
    print('Check Source code: ok!')


def merge_library(libraries, target):
    cmd = f'lipo -create {" ".join(libraries)} -output {target}'
    os.system(cmd)
    if not os.path.exists(target):
        raise Exception('Merge library failed!', 1002)
    for library in libraries:
        os.remove(library)


def make_framework(name, header, library, target_dir):

    def make_info_plist():
        info_dict = {
            'CFBundleIdentifier': f'com.liit.{name}',
            'CFBundleName': name,
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0',
            'CFBundleExecutable': name
        }
        plist_path = f'{framework}/Info.plist'
        with open(plist_path, 'wb') as plist_file:
            plistlib.dump(info_dict, plist_file)

    framework = f'{target_dir}/{name}.framework'
    os.makedirs(framework)
    shutil.copytree(header, f'{framework}/Headers')
    os.system(f'libtool -static -o {framework}/{name} {library}')
    make_info_plist()


def get_xcode_path():
    result = subprocess.check_output(["xcode-select", "-print-path"])
    return result.decode('utf-8').strip()


def get_sdk_version():
    result = subprocess.check_output(["xcrun", "--sdk", "iphoneos", "--show-sdk-version"])
    return result.decode('utf-8').strip()


def get_sys_root(platform, sdk_version=''):
    if not sdk_version:
        sdk_version = get_sdk_version()
    result = subprocess.check_output(["xcrun", "--sdk", platform, "-show-sdk-platform-path"])
    platform_path = result.decode('utf-8').strip()
    return f'{platform_path}/Developer/SDKs/{platform}{sdk_version}.sdk'

def show_menu():
    print('Option List:')
    print('1) option: build options')
    print('2) clean: clean build and source code')


def main(build, clean):
    if len(sys.argv) == 1:
        build(sys.argv[2:])
    else:
        if sys.argv[1] == 'clean':
            clean()
        elif sys.argv[1] == 'option':
            build(sys.argv[2:])
        else:
            show_menu()