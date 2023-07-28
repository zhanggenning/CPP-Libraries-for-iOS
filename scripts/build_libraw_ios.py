import os
import sys
import build_tools as tools

name = 'LibRaw'
target = 'libraw'
version = '0.21.1'

root = sys.path[0]
source_code = f'{root}/source/{name}-{version}'
output_root = f'{root}/output/{name.lower()}'
build_root = lambda arch: f'{output_root}/build-{arch}'

enable_openmp = False
openmp_lib_path = f'{root}/output/openmp/lib'
openmp_header_path = f'{root}/output/openmp/include'

enable_lcms2 = False
lcms2_lib_path = f'{root}/output/lcms2/lib'
lcms2_header_path = f'{root}/output/lcms2/include'


def clean_source_code(): tools.remove_dir(source_code)


def download_source_code():
    package = f"https://www.libraw.org/data/{name}-{version}.tar.gz"
    tools.fetch_source_code(package, source_code)
    os.chdir(source_code)


def clean_library(): tools.remove_dir(output_root)


def compile_library(arch):
    if arch == 'ios':
        platform = 'arm64'
        host = 'arm-apple-darwin'
        min_version = 'miphoneos-version-min'
    elif arch == 'simulator':
        platform = 'x86_64'
        host = 'i386-apple-darwin'
        min_version = 'mios-simulator-version-min'
    else:
        raise Exception(f'Unsuppper arch {arch}!', 1000)

    cc = tools.get_clang(arch)
    sdk = tools.get_sdk_path(arch)
    os.environ['DEVROOT'] = f"{tools.get_platform_path(arch)}/Developer"
    os.environ['SDKROOT'] = sdk
    os.environ['CC'] = cc
    os.environ['CXX'] = cc

    # CFLAGS
    cflags = f'-arch {platform} -{min_version}=13.0 -pipe -Os -gdwarf-2 -isysroot {sdk}'
    if enable_openmp:
        cflags += f' -Xclang -openmp -D_OPENMP -I{openmp_header_path}'
    if enable_lcms2:
        cflags += f' -DUSE_LCMS2 -I{lcms2_header_path}'
    os.environ['CFLAGS'] = cflags
    os.environ['CXXFLAGS'] = cflags

    # LDFLAGS
    ldflags = f'-arch {platform} -isysroot {sdk}'
    if enable_openmp:
        ldflags += f' -L{openmp_lib_path} -lomp'
    if enable_lcms2:
        ldflags += f' -L{lcms2_lib_path} -llcms2'
    os.environ['LDFLAGS'] = ldflags

    # Configure
    config = f"--host={host} \
            --prefix={build_root(arch)} \
            --disable-jpeg \
            --disable-lcms \
            --disable-shared \
            --disable-examples \
            --disable-jasper \
            --enable-zlib "
    if enable_openmp:
        config += '--enable-openmp '
    else:
        config += '--disable-openmp '

    if enable_lcms2:
        config += '--enable-lcms '
    else:
        config += '--disable-lcms '

    os.system(f'./configure {config}')
    os.system('make clean')
    os.system('make')
    os.system('make install')

    # Install
    library = f'{build_root(arch)}/lib/{target}.a'
    if not os.path.exists(library):
        raise Exception('Compile code failed!', 1001)
    header = f'{build_root(arch)}/include/libraw'
    return tools.export(arch, library, header, output_root)


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
    clean_library()
    try:
        config_options(options)
        download_source_code()
        tools.build(compile_library, target)
    except Exception as e:
        print(f'Error: {e.args[0]}')


def clean():
    tools.remove_dir(output_root)
    clean_source_code()


if __name__ == "__main__":
    tools.main(build, clean)
