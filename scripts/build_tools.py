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
    def get_top_level_folder_name(tar_path):
        with tarfile.open(tar_path, "r") as tar:
            members = tar.getmembers()  # 获取所有成员的信息

        top_level_folder_name = None
        min_levels = float('inf')

        for member in members:
            # 获取目录层级：用 os.path.normpath 函数处理路径，然后计算路径分隔符的数量
            levels = os.path.normpath(member.name).count(os.sep)

            # 如果目录层级比当前最小层级还小，并且成员是一个目录
            if levels < min_levels and member.isdir():
                min_levels = levels
                top_level_folder_name = member.name

        return top_level_folder_name

    filename = file.split('/')[-1]
    target_dir_name = target_dir.split('/')[-1]
    target_dir_root = os.path.dirname(os.path.normpath(target_dir))
    top_dir_name = get_top_level_folder_name(file)
    print(f'Begin uncompress package: {filename}')
    with tarfile.open(file) as tar:
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
    if len(libraries) == 0:
        raise Exception('Merge library failed!', 1004)
    root = os.path.commonpath(libraries)
    if len(root) == 0:
        raise Exception('Merge library failed!', 1003)

    target_library = f"{root}/{target}.a"
    cmd = f'lipo -create {" ".join(libraries)} -output {target_library}'
    os.system(cmd)
    if not os.path.exists(target_library):
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


def build(compile, target, archs=['ios', 'simulator']):
    # Build
    libraries = []
    for arch in archs:
        library = compile(arch)
        libraries.append(library)

    # Merge
    merge_library(libraries, target)


def export(arch, library, header, target_root):
    target_library_path = f'{target_root}/lib'
    target_header_path = f'{target_root}/include'
    target_name = os.path.splitext(os.path.basename(library))[0]
    src_root = os.path.commonprefix([library, header])

    # copy library
    create_dir(target_library_path)
    target_library_file = f'{target_library_path}/{target_name}-{arch}.a'
    shutil.copy(library, target_library_file)

    # copy header
    if not os.path.exists(target_header_path):
        shutil.copytree(header, target_header_path)

    remove_dir(src_root)
    return target_library_file


def sdk_name(arch):
    if arch == 'ios':
        return 'iphoneos'
    elif arch == 'simulator':
        return 'iphonesimulator'
    else:
        raise Exception(f'Unsuppper arch {arch}!', 1000)


def get_platform_path(arch):
    result = subprocess.check_output(["xcrun", "--sdk", sdk_name(arch), "--show-sdk-platform-path"])
    return result.decode('utf-8').strip()


def get_sdk_path(arch):
    result = subprocess.check_output(["xcrun", "--sdk", sdk_name(arch), "--show-sdk-path"])
    return result.decode('utf-8').strip()


def get_clang(arch):
    result = subprocess.check_output(["xcrun", "--sdk", sdk_name(arch), "-f", "clang"])
    return result.decode('utf-8').strip()


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