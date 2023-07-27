import os
import sys
import shutil
import build_tools as tools

name = 'LibRaw'
target = 'libraw'
archs = ['ios', 'simulator']
version = '0.21.1'

root = sys.path[0]
source_code_root = f'{root}/source'
source_code_name = f'{name}-{version}'
source_code_path = f'{source_code_root}/{source_code_name}'
output_root = f'{root}/output/{name.lower()}'
output_library_path = f'{output_root}/lib'
output_header_path = f'{output_root}/include'

enable_openmp = False
openmp_lib_path = f'{root}/output/openmp/lib'
openmp_header_path = f'{root}/output/openmp/include'

enable_lcms2 = False
lcms2_lib_path = f'{root}/output/lcms2/lib'
lcms2_header_path = f'{root}/output/lcms2/include'

def clean_source_code(): tools.remove_dir(source_code_path)


def download_source_code():
    url_base = 'https://www.libraw.org/data/'
    package = f'{name}-{version}.tar.gz'
    tools.fetch_source_code(f'{url_base}/{package}', source_code_path)


def clean_library(): tools.remove_dir(output_root)


def build_library():
    os.chdir(source_code_path)

    def do_config(arch):
        # ARCH
        clang_root = '/Applications/Xcode.app/Contents/Developer'
        if arch == 'ios':
            platform = 'arm64'
            host = 'arm-apple-darwin'
            devroot = f'{clang_root}/Platforms/iPhoneOS.platform/Developer'
            sdkroot = f'{devroot}/SDKs/iPhoneOS.sdk'
            minversion = f'miphoneos-version-min'
        elif arch == 'simulator':
            platform = 'x86_64'
            host = 'i386-apple-darwin'
            devroot = f'{clang_root}/Platforms/iPhoneSimulator.platform/Developer'
            sdkroot = f'{devroot}/SDKs/iPhoneSimulator.sdk'
            minversion = f'miphoneos-version-min'
        else:
            raise Exception(f'Unsuppper arch {arch}!', 1000)
        os.environ['DEVROOT'] = devroot
        os.environ['SDKROOT'] = sdkroot
        os.environ['CC'] = f'{clang_root}/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang'

        # CFLAGS
        # cflags = f'-arch {platform} -target arm64-apple-ios13.0 -pipe -Os -gdwarf-2 -isysroot {sdkroot}'
        cflags = f'-arch {platform} -{minversion}=13.0 -pipe -Os -gdwarf-2 -isysroot {sdkroot}'
        if enable_openmp:
            cflags += f' -Xclang -openmp -D_OPENMP -I{openmp_header_path}'
        if enable_lcms2:
            cflags += f' -DUSE_LCMS2 -I{lcms2_header_path}'
        os.environ['CFLAGS'] = cflags

        # LDFLAGS
        ldflags = f'-arch {platform} -isysroot {sdkroot}'
        if enable_openmp:
            ldflags += f' -L{openmp_lib_path} -lomp'
        if enable_lcms2:
            ldflags += f' -L{lcms2_lib_path} -llcms2'
        os.environ['LDFLAGS'] = ldflags
        os.environ['CXX'] = os.environ.get('CC')
        os.environ['CXXFLAGS'] = os.environ.get('CFLAGS')

        # Configure
        cmd = './configure '
        cmd += f'--host={host} '
        cmd += '--disable-jpeg '
        cmd += '--disable-lcms '
        cmd += '--disable-shared '
        cmd += '--disable-examples '
        cmd += '--disable-jasper '
        cmd += '--enable-zlib '
        if enable_openmp:
            cmd += '--enable-openmp '
        else:
            cmd += '--disable-openmp '

        if enable_lcms2:
            cmd += '--enable-lcms '
        else:
            cmd += '--disable-lcms '

        os.system(cmd)

    def do_compile(arch):
        do_config(arch)
        os.system('make clean')
        os.system('make')

        # copy library
        library_file = f'{source_code_path}/lib/.libs/{target}.a'
        if not os.path.exists(library_file):
            raise Exception('Compile code failed!', 1001)
        tools.create_dir(output_library_path)
        target_library_file = f'{output_library_path}/{target}-{arch}.a'
        shutil.copy(library_file, target_library_file)

        # copy header
        header_file = f'{source_code_path}/libraw'
        if not os.path.exists(output_header_path):
            shutil.copytree(header_file, output_header_path)

        # clean
        os.system('make clean')
        return target_library_file

    # Build
    libraries = []
    for arch in archs:
        library = do_compile(arch)
        libraries.append(library)

    # Merge
    tools.merge_library(libraries, f'{output_library_path}/{target}.a')

    # Framework
    # tools.make_framework("LibRaw", output_header_path, f'{output_library_path}/{target}.a', output_root)

def config_options(options):
    print(options)
    if len(options) == 0:
        show_options_menu()
        raise Exception('Option params error!', 1004)
    if '--enable-openmp' in options:
        if os.path.exists(openmp_lib_path) and os.path.exists(openmp_header_path):
            global enable_openmp
            enable_openmp = True
        else:
            raise Exception("Can't found openmp library, please run 'build_openmp_ios.py' first!", 1005)
    if '--enable-lcms2' in options:
        if os.path.exists(lcms2_lib_path) and os.path.exists(lcms2_header_path):
            global enable_lcms2
            enable_lcms2 = True
        else:
            raise Exception("Can't found openmp library, please run 'build_openmp_ios.py' first!", 1005)

def show_options_menu():
    print("Options Config:")
    print("--enable-openmp: use OpenMP in LibRaw")
    print("--enable-lcms2: use LCMS2 in LibRaw")


def build(options=[]):
    try:
        download_source_code()
        config_options(options)
        clean_library()
        build_library()
    except Exception as e:
        clean_library()
        print(f'Error: {e.args[0]}')


def clean():
    tools.remove_dir(output_root)
    clean_source_code()


if __name__ == "__main__":
    tools.main(build, clean)
