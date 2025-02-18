#!/usr/bin/env python3

import subprocess
import requests
import os
import tempfile
import shutil

#BASE_URL = 'http://termux.net/'
BASE_URL = 'http://termux.comma.ai/'

# Create mirror using
# lftp -c "mirror --use-pget-n=10 --verbose http://termux.net"
# azcopy --source dists/ --destination https://termuxdist.blob.core.windows.net/dists --recursive --dest-key $(az storage account keys list --account-name termuxdist --output tsv --query "[0].value")


DEFAULT_PKG = ['apt', 'bash', 'busybox', 'ca-certificates', 'command-not-found', 'dash', 'dash', 'dpkg', 'gdbm', 'gpgv', 'libandroid-support', 'libbz2', 'libc++', 'libcrypt', 'libcrypt-dev', 'libcurl', 'libffi', 'libgcrypt', 'libgpg-error', 'liblzma', 'libnghttp2', 'libsqlite', 'libutil', 'ncurses', 'ncurses-ui-libs', 'openssl', 'python', 'readline', 'termux-am', 'termux-exec', 'termux-tools', 'qt5-base', 'qt5-declarative', 'libicu', 'swig', 'gettext', 'ripgrep']

# The checked-in debs are built using the neos branch on:
# https://github.com/commaai/termux-packages/tree/neos/
#
# Quick Start:
#  * start docker: scripts/run-docker.sh
#  * build inside container: ./build-package.sh -a aarch64 python
#  * copy the deb from termux-packages/debs/

LOCAL_OVERRIDE_PKG = {
    'apt':'apt_1.4.9-4_aarch64.deb',
    'autoconf':'autoconf_2.69_all.deb',
    'automake':'automake_1.16.1_all.deb',
    'bash':'bash_5.0.7-1_aarch64.deb',
    'binutils':'binutils_2.32-2_aarch64.deb',
    'bison':'bison_3.4.1_aarch64.deb',
    'busybox':'busybox_1.30.1-2_aarch64.deb',
    'ca-certificates':'ca-certificates_20190515_all.deb',
    'clang':'clang_8.0.0-1_aarch64.deb',
    'cmake':'cmake_3.14.4_aarch64.deb',
    'command-not-found':'command-not-found_1.37_aarch64.deb',
    'coreutils':'coreutils_8.31-2_aarch64.deb',
    'curl':'curl_7.65.0_aarch64.deb',
    'dropbear':'dropbear_2019.78_aarch64.deb',
    'dash':'dash_0.5.10.2-1_aarch64.deb',
    'dpkg':'dpkg_1.19.6_aarch64.deb',
    'ffmpeg-dev':'ffmpeg-dev_4.1.3-3_aarch64.deb',
    'ffmpeg':'ffmpeg_4.1.3-3_aarch64.deb',
    'flex':'flex_2.6.4_aarch64.deb',
    'freetype':'freetype_2.10.0-1_aarch64.deb',
    'gdb':'gdb_8.3-1_aarch64.deb',
    'gdbm':'gdbm_1.18.1_aarch64.deb',
    'gettext':'gettext_0.20.1-3_aarch64.deb',
    'git-lfs':'git-lfs_2.7.2-1_aarch64.deb',
    'git':'git_2.21.0-3_aarch64.deb',
    'glib':'glib_2.60.3_aarch64.deb',
    'gpgv':'gpgv_2.2.15-1_aarch64.deb',
    'grep':'grep_3.3-1_aarch64.deb',
    'htop':'htop_2.2.0-2_aarch64.deb',
    'jq':'jq_1.6_aarch64.deb',
    'jsoncpp':'jsoncpp_1.8.4-2_aarch64.deb',
    'krb5':'krb5_1.16.3_aarch64.deb',
    'ldns':'ldns_1.7.0-5_aarch64.deb',
    'less':'less_530-2_aarch64.deb',
    'libandroid-glob':'libandroid-glob_0.4_aarch64.deb',
    'libandroid-support':'libandroid-support_24-3_aarch64.deb',
    'libarchive':'libarchive_3.3.3-4_aarch64.deb',
    'libbz2':'libbz2_1.0.6-3_aarch64.deb',
    'libc++':'libc++_19b_aarch64.deb',
    'libcroco':'libcroco_0.6.13_aarch64.deb',
    'libcrypt-dev':'libcrypt-dev_0.2-1_aarch64.deb',
    'libcrypt':'libcrypt_0.2-1_aarch64.deb',
    'libcurl-dev':'libcurl-dev_7.65.0_aarch64.deb',
    'libcurl':'libcurl_7.65.0_aarch64.deb',
    'libdb':'libdb_18.1.32_aarch64.deb',
    'libedit':'libedit_20190324-3.1-0_aarch64.deb',
    'libevent':'libevent_2.1.10_aarch64.deb',
    'libexpat':'libexpat_2.2.6-1_aarch64.deb',
    'libffi-dev':'libffi-dev_3.2.1-2_aarch64.deb',
    'libffi':'libffi_3.2.1-2_aarch64.deb',
    'libgcrypt':'libgcrypt_1.8.4_aarch64.deb',
    'libgmp':'libgmp_6.1.2-2_aarch64.deb',
    'libgnutls':'libgnutls_3.6.8_aarch64.deb',
    'libgpg-error':'libgpg-error_1.36_aarch64.deb',
    'libiconv':'libiconv_1.16-2_aarch64.deb',
    'libicu':'libicu_65.1-1_aarch64.deb',
    'libidn2':'libidn2_2.2.0_aarch64.deb',
    'libjpeg-turbo-dev':'libjpeg-turbo-dev_2.0.2-1_aarch64.deb',
    'libjpeg-turbo':'libjpeg-turbo_2.0.2-1_aarch64.deb',
    'libllvm':'libllvm_8.0.0-1_aarch64.deb',
    'libltdl':'libltdl_2.4.6-5_aarch64.deb',
    'liblz4-dev':'liblz4-dev_1.9.1_aarch64.deb',
    'liblz4':'liblz4_1.9.1_aarch64.deb',
    'liblzma':'liblzma_5.2.4_aarch64.deb',
    'liblzo-dev':'liblzo-dev_2.10_aarch64.deb',
    'liblzo':'liblzo_2.10_aarch64.deb',
    'libmp3lame':'libmp3lame_3.100_aarch64.deb',
    'libmpc':'libmpc_1.1.0_aarch64.deb',
    'libmpfr':'libmpfr_4.0.2_aarch64.deb',
    'libnettle':'libnettle_3.4.1_aarch64.deb',
    'libnghttp2':'libnghttp2_1.38.0_aarch64.deb',
    'libogg':'libogg_1.3.3_aarch64.deb',
    'libopus':'libopus_1.3.1-1_aarch64.deb',
    'libpcap-dev':'libpcap-dev_1.9.0_aarch64.deb',
    'libpcap':'libpcap_1.9.0_aarch64.deb',
    'libpng':'libpng_1.6.37-1_aarch64.deb',
    'libpopt':'libpopt_1.16-2_aarch64.deb',
    'libsoxr':'libsoxr_0.1.3-1_aarch64.deb',
    'libsqlite':'libsqlite_3.28.0-1_aarch64.deb',
    'libtool':'libtool_2.4.6-5_aarch64.deb',
    'libunistring':'libunistring_0.9.10-2_aarch64.deb',
    'libutil':'libutil_0.4_aarch64.deb',
    'libuuid-dev':'libuuid-dev_1.0.3-2_aarch64.deb',
    'libuuid':'libuuid_1.0.3-2_aarch64.deb',
    'libuv':'libuv_1.29.1_aarch64.deb',
    'libvorbis':'libvorbis_1.3.6-1_aarch64.deb',
    'libvpx':'libvpx_1.8.0-1_aarch64.deb',
    'libx264':'libx264_20190215_aarch64.deb',
    'libx265':'libx265_3.0-1_aarch64.deb',
    'libxml2':'libxml2_2.9.9-3_aarch64.deb',
    'm4':'m4_1.4.18-1_aarch64.deb',
    'make':'make_4.2.1-2_aarch64.deb',
    'man':'man_1.14.5-1_aarch64.deb',
    'nano':'nano_4.2_aarch64.deb',
    'ncurses-dev':'ncurses-dev_6.1.20190511-1_aarch64.deb',
    'ncurses-ui-libs':'ncurses-ui-libs_6.1.20190511-1_aarch64.deb',
    'ncurses':'ncurses_6.1.20190511-1_aarch64.deb',
    'ndk-sysroot':'ndk-sysroot_19b-4_aarch64.deb',
    'openssh':'openssh_8.0p1-1_aarch64.deb',
    'openssl-dev':'openssl-dev_1.1.1c_aarch64.deb',
    'openssl-tool':'openssl-tool_1.1.1c_aarch64.deb',
    'openssl':'openssl_1.1.1c_aarch64.deb',
    'patchelf':'patchelf_0.10_aarch64.deb',
    'pcre2':'pcre2_10.33_aarch64.deb',
    'pcre':'pcre_8.43-1_aarch64.deb',
    'perl':'perl_5.28.2-1_aarch64.deb',
    'pkg-config':'pkg-config_0.29.2_aarch64.deb',
    'python':'python_3.8.5_aarch64.deb',
    'qt5-base':'qt5-base_5.12.8-28_aarch64.deb',
    'qt5-declarative':'qt5-declarative_5.12.8-28_aarch64.deb',
    'readline':'readline_8.0-1_aarch64.deb',
    'rhash':'rhash_1.3.8-1_aarch64.deb',
    'ripgrep':'ripgrep_11.0.2-1_aarch64.deb',
    'rsync':'rsync_3.1.3-4_aarch64.deb',
    'rust':'rust_1.49.0-4_aarch64.deb',
    'sed':'sed_4.7_aarch64.deb',
    'strace':'strace_5.0_aarch64.deb',
    'swig':'swig_4.0.1-1_aarch64.deb',
    'tar':'tar_1.32-2_aarch64.deb',
    'termux-am':'termux-am_0.2_all.deb',
    'termux-auth':'termux-auth_1.1_aarch64.deb',
    'termux-exec':'termux-exec_0.3_aarch64.deb',
    'termux-licenses':'termux-licenses_1.0_all.deb',
    'termux-tools':'termux-tools_0.66_all.deb',
    'tmux':'tmux_2.9a_aarch64.deb',
    'vim-runtime':'vim-runtime_8.1.1400_all.deb',
    'vim':'vim_8.1.1400_aarch64.deb',
    'wget':'wget_1.20.3-2_aarch64.deb',
    'xvidcore':'xvidcore_1.3.5_aarch64.deb',
    'xz-utils':'xz-utils_5.2.4_aarch64.deb',
    'zlib-dev':'zlib-dev_1.2.11_aarch64.deb',
    'zlib':'zlib_1.2.11_aarch64.deb'
}

def load_packages():
    pkg_deps = {}
    pkg_filenames = {}

    r = requests.get(BASE_URL + 'dists/stable/main/binary-aarch64/Packages').text
    r += requests.get(BASE_URL + 'dists/stable/main/binary-all/Packages').text
    print(BASE_URL + 'dists/stable/main/binary-aarch64/Packages')

    for l in r.split('\n'):
        if l.startswith("Package:"):
            pkg_name = l.split(': ')[1]
            pkg_depends = []
        elif l.startswith('Depends: '):
            pkg_depends = l.split(': ')[1].split(',')
            pkg_depends = [p.replace(' ', '') for p in pkg_depends]

            # strip version (eg. gnupg (>= 2.2.9-1))
            pkg_depends = [p.split('(')[0] for p in pkg_depends]
        elif l.startswith('Filename: '):
            pkg_filename = l.split(': ')[1]
            pkg_deps[pkg_name] = pkg_depends
            pkg_filenames[pkg_name] = pkg_filename
    return pkg_deps, pkg_filenames


def get_dependencies(pkg_deps, pkg_name):
    r = [pkg_name]
    try:
        new_deps = pkg_deps[pkg_name]
        for dep in new_deps:
            r += get_dependencies(pkg_deps, dep)
    except KeyError:
        pass

    return r


def install_package(pkg_deps, pkg_filenames, pkg):
    if not os.path.exists('out'):
        os.mkdir('out')

    build_usr_dir = os.getcwd()
    tmp_dir = tempfile.mkdtemp()

    if pkg in LOCAL_OVERRIDE_PKG:
        deb_name = LOCAL_OVERRIDE_PKG[pkg]
        deb_path = os.path.join(os.path.join(build_usr_dir, "debs"), deb_name)
        print("Using local copy of package %s - %s - %s" % (pkg, tmp_dir, deb_name))
    elif pkg in pkg_filenames:
        url = BASE_URL + pkg_filenames[pkg]
        print("Downloading %s - %s - %s" % (pkg, tmp_dir, url))
        r = requests.get(url)
        deb_name = 'out.deb'
        deb_path = os.path.join(tmp_dir, deb_name)
        open(deb_path, 'wb').write(r.content)
    else:
        print("%s not found" % pkg)
        return ""

    subprocess.check_call(['ar', 'x', deb_path], cwd=tmp_dir)
    subprocess.check_call(['tar', '-C', './out', '-p', '-xf', os.path.join(tmp_dir, 'data.tar.xz')])
    if os.path.exists(os.path.join(tmp_dir, 'control.tar.gz')):
        subprocess.check_call(['tar', '-xf', os.path.join(tmp_dir, 'control.tar.gz')], cwd=tmp_dir)
    else:
        subprocess.check_call(['tar', '-xf', os.path.join(tmp_dir, 'control.tar.xz')], cwd=tmp_dir)

    control = open(os.path.join(tmp_dir, 'control')).read()
    control += 'Status: install ok installed\n'

    files = subprocess.check_output(['dpkg', '-c', deb_path], cwd=tmp_dir, encoding='utf-8')

    file_list = ""
    for f in files.split('\n'):
        try:
            filename = f.split()[5][1:]
            if filename == '/':
                filename = '/.'  # this is what apt does
            file_list += filename + "\n"

        except IndexError:
            pass

    info_path = 'out/data/data/com.termux/files/usr/var/lib/dpkg/info'
    if not os.path.exists(info_path):
        os.makedirs(info_path)

    open(os.path.join(info_path, pkg + '.list'), 'w').write(file_list)

    copies = ['conffiles', 'postinst', 'prerm']

    for copy in copies:
        f = os.path.join(tmp_dir, copy)
        if os.path.exists(f):
            target = os.path.join(info_path, pkg + '.' + copy)
            shutil.copyfile(f, target)

    return control


if __name__ == "__main__":
    to_install = DEFAULT_PKG
    to_install += [
        'autoconf',
        'automake',
        'bison',
        'clang',
        'cmake',
        'coreutils',
        'curl',
        'ffmpeg',
        'ffmpeg-dev',
        'flex',
        'gdb',
        'git',
        'git-lfs',
        'htop',
        'jq',
        'libcurl-dev',
        'libffi-dev',
        'libjpeg-turbo',
        'libjpeg-turbo-dev',
        'liblz4',
        'liblz4-dev',
        'liblzo',
        'liblzo-dev',
        'libmpc',
        'libtool',
        'libuuid-dev',
        #'libzmq',
        'libpcap',
        'libpcap-dev',
        'make',
        'man',
        'nano',
        'ncurses-dev',
        'openssh',
        'openssl-dev',
        'openssl-tool',
        'patchelf',
        'pkg-config',
        'rsync',
        'strace',
        'tar',
        'tmux',
        'vim',
        'wget',
        'xz-utils',
        'zlib-dev',
    ]

    pkg_deps, pkg_filenames = load_packages()
    deps = []
    for pkg in to_install:
        deps += get_dependencies(pkg_deps, pkg)
    deps = set(deps)

    status = ""

    for pkg in deps:
        s = install_package(pkg_deps, pkg_filenames, pkg)
        status += s + "\n"
    print(deps)

    try:
        os.makedirs('out/data/data/com.termux/files/usr/var/lib/dpkg/')
    except OSError:
        pass

    status_file = 'out/data/data/com.termux/files/usr/var/lib/dpkg/status'
    open(status_file, 'w').write(status)
