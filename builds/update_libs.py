import os
import sys
import json
import tempfile
import shutil
import zipfile

from sys import platform

script_path = os.path.dirname(os.path.realpath(__file__))

def delete(path):
    """
    删除一个文件/文件夹
    :param path: 待删除的文件路径
    :return:
    """
    if not os.path.exists(path):
        print("[*] {} not exists".format(path))
        return

    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)
    elif os.path.islink(path):
        os.remove(path)
    else:
        print("[*] unknow type for: " + path)


def clean_folder(folder):
    """
    删除文件夹下的所有内容
    :param folder: 待处理的文件夹路径
    :return:
    """
    if not os.path.isdir(folder):
        print("[*] {} not dir or not exists".format(folder))
        return

    for name in os.listdir(folder):
        if name != '.gitkeep':
            delete(os.path.join(folder, name))


def insure_empty_dir(dir_path):
    """
    确保为一个空文件夹；如果不存在，则创建；
    如果已经存在，存清除文件中的任何已有文件和文件夹
    :param dir_path: 待检查的文件夹路径
    :return:
    """
    if os.path.exists(dir_path):
        clean_folder(dir_path)
    else:
        os.makedirs(dir_path)


def umount_share(mount_path):
    if os.path.ismount(mount_path):
        result = os.system("umount -fv {0}".format(mount_path))
        if result == 0:
            print('umount success')
        else:
            raise Exception('umount fail, result={}'.format(result))


def zego_mount_share_content(remote_path, mount_path):
    if not os.path.exists(mount_path):
        os.makedirs(mount_path)
    if os.path.ismount(mount_path):
        print('share is mounted,umount...')
        umount_share(mount_path)
    if not os.path.ismount(mount_path):
        insure_empty_dir(mount_path)
        __is_linux_os = (platform == "linux" or platform == "linux2")
        if __is_linux_os:
            mount_cmd = 'mount -t cifs //192.168.1.3/{0} {1} -o username=share,password=share@zego'.format(remote_path, mount_path)
        else:
            mount_cmd = 'mount -t smbfs //share:share%40zego@192.168.1.3/{0} {1}'.format(remote_path, mount_path)
        result = os.system(mount_cmd)
        if result == 0:
            print('mount {} success'.format(remote_path))
        else:
            raise Exception('mount fail, result:{} cmd:{}'.format(result, mount_cmd))


def prepare_default_mount_path(remote_path):
    mount_path = os.path.join(tempfile.gettempdir(), 'wbdemo_smb_temp')

    if not os.path.ismount(mount_path):
        insure_empty_dir(mount_path)
        zego_mount_share_content(remote_path, mount_path)
    return mount_path


# 版本号有异常的子目录列在这里
filter_list_archive_sub_folder = ['zegoliveroom_191128_113628_release-new-0-g94898fa22_video_bn2919_12',
                                  'zegoliveroom_200709_172721_release-new-0-g35dd5b122_bn4209_12_video_mediaplayer']


def find_special_version_in_archive(sdk_name, accurate_version, archive_path):
    print('founding {} in archive: {}'.format(accurate_version, archive_path))
    match_folder = ""

    file_list = os.listdir(archive_path)
    for folder_name in file_list:
        # 排除版本号有异常的子目录
        if folder_name in filter_list_archive_sub_folder:
            continue

        # print(folder_name)
        if accurate_version in folder_name:
            join_folder = os.path.join(archive_path, folder_name)
            if sdk_name == 'liveroom':
                # liveroom需检查子目录是否有android，因为同bn号下有其他端的制品目录
                if 'android' in os.listdir(join_folder):
                    match_folder = join_folder
                    break
            else:
                match_folder = join_folder
                break

    return match_folder


def get_find_relative_path_list(sdk_name):
    if sdk_name == 'docsviewsdk':
        return ['test/android', 'online/android']
    elif sdk_name == 'whiteboardviewsdk':
        return ['test/liveroom/android', 'online/liveroom/android']
    elif sdk_name == 'liveroom':
        return ['zegoliveroom_edu_test', 'zegoliveroom_other', 'zegoliveroom_release_new', 'zegoliveroom_stable']
    elif sdk_name == 'express':
        return ['develop/video_whiteboard', 'release/video_whiteboard', 'stable/video_whiteboard']


def get_find_accurate_version(sdk_name, version):
    if sdk_name == 'docsviewsdk':
        return "v{}_".format(version)
    elif sdk_name == 'whiteboardviewsdk':
        return "v{}_".format(version)
    elif sdk_name == 'liveroom':
        return "{}".format(version)
    elif sdk_name == 'express':
        return "_{}".format(version)


def get_match_file_path(sdk_name, match_folder, lib_file_name, accurate_version):
    if sdk_name == 'liveroom':
        match_file = 'not_found'
        file_list = os.listdir(os.path.join(match_folder, 'android'))
        for file_name in file_list:
            # print(file_name)
            if accurate_version in file_name and file_name.startswith('zegoliveroom'):
                match_file = os.path.join(match_folder, 'android', file_name)
                break
        return match_file
    elif sdk_name == 'express':
        match_file = 'not_found'
        file_list = os.listdir(os.path.join(match_folder, 'android-java'))
        for file_name in file_list:
            # print(file_name)
            if accurate_version in file_name and file_name.startswith('ZegoExpressEngine'):
                match_file = os.path.join(match_folder, 'android-java', file_name)
                break
        return match_file
    else:
        return os.path.join(match_folder, lib_file_name)


def get_lib_special_version(sdk_name, mount_dir, lib_file_name, version):
    match_folder = ''
    accurate_version = get_find_accurate_version(sdk_name, version)
    relative_path_list = get_find_relative_path_list(sdk_name)

    for relative_path in relative_path_list:
        find_folder = os.path.join(mount_dir, relative_path)
        match_folder = find_special_version_in_archive(sdk_name, accurate_version, find_folder)
        if len(match_folder) > 0:
            break

    match_file = ''
    if len(match_folder) > 0:
        match_file = get_match_file_path(sdk_name, match_folder, lib_file_name, accurate_version)
        if os.path.exists(match_file):
            print('founded {} size:{} path:{}'.format(lib_file_name, os.path.getsize(match_file), match_file))
        else:
            match_file = ''

    if len(match_file) == 0:
        print('not founded')

    return match_file


def remove_pre_lib(sdk_name, lib_file_name, local):
    try:
        local_full_path = os.path.join(project_base_path, local)

        if sdk_name == 'docsviewsdk' or sdk_name == 'whiteboardviewsdk':
            delete(os.path.join(local_full_path, lib_file_name))
        elif sdk_name == 'liveroom':
            delete(os.path.join(local_full_path, 'ZegoExpressEngine.jar'))
            delete(os.path.join(local_full_path, 'zegoliveroom.jar'))
            delete(os.path.join(local_full_path, 'arm64-v8a'))
            delete(os.path.join(local_full_path, 'armeabi-v7a'))
        elif sdk_name == 'express':
            delete(os.path.join(local_full_path, 'zegoliveroom.jar'))
            delete(os.path.join(local_full_path, 'ZegoExpressEngine.jar'))
            delete(os.path.join(local_full_path, 'arm64-v8a'))
            delete(os.path.join(local_full_path, 'armeabi-v7a'))

    except Exception:
        print('rm not fonud: {} in {}'.format(lib_file_name, local))
    finally:
        print('remove pre lib ok')

def update(sdk_name, remote, lib_file_name, version, local):
    remove_pre_lib(sdk_name, lib_file_name, local)

    mount_dir = prepare_default_mount_path(remote)
    try:
        lib_remote_path = get_lib_special_version(sdk_name, mount_dir, lib_file_name, version)
        if len(lib_remote_path) > 0:
            if lib_remote_path.endswith('.zip'):
                print("extract to {}".format(os.path.join(project_base_path, local)))
                zip_file = zipfile.ZipFile(lib_remote_path, 'r')
                for name in zip_file.namelist():
                    if 'arm64-v8a' in name or 'armeabi-v7a' in name or name.endswith('.jar'):
                        zip_file.extract(name, os.path.join(project_base_path, local))
                zip_file.close()

                # liveroom 的补充处理
                if sdk_name == 'liveroom':
                    whiteboardviewsdk_module_libs = os.path.join(project_base_path, 'ZegoWhiteboardViewSDK', 'zegoliveroomlib', 'libs')
                    if os.path.isdir(whiteboardviewsdk_module_libs):
                        shutil.copyfile(os.path.join(project_base_path, local, 'zegoliveroom.jar'), os.path.join(whiteboardviewsdk_module_libs, 'zegoliveroom.jar'))

                # express 的补充处理
                if sdk_name == 'express':
                    local_full_path = os.path.join(project_base_path, local)
                    os.chdir(local_full_path)
                    for name in os.listdir(local_full_path):
                        if name.startswith('ZegoExpressEngine'):
                            shutil.move('{}/arm64-v8a'.format(name), '.')
                            shutil.move('{}/armeabi-v7a'.format(name), '.')
                            shutil.move('{}/ZegoExpressEngine.jar'.format(name), '.')
                            delete(name)
            else:
                copy_dest_folder = os.path.join(project_base_path, local)
                print("copy to {}".format(copy_dest_folder))
                shutil.copyfile(lib_remote_path, os.path.join(copy_dest_folder, lib_file_name))
                if os.path.isfile(os.path.join(copy_dest_folder, lib_file_name)):
                    print("copy succ")
                else:
                    print("copy FAIL")
        else:
            raise Exception('找不到指定版本的lib')
    except Exception:
        raise Exception("找不到指定版本的lib")
    finally:
        umount_share(mount_dir)
        delete(mount_dir)

def inplace_change(filename, old_string, new_string):
    newlines = []
    with open(filename) as f:
        content = f.readlines()
        for line in content:
            if old_string in line:
                newlines.append(new_string)
            else:
                newlines.append(line)
    with open(filename, 'w') as f:
        # print('======= start =========')
        for line in newlines:
            # print('{}'.format(line))
            f.write(line)
        # print('======= end =========')

if __name__ == '__main__':
    android_project_path = os.path.abspath(os.path.join(script_path, '..'))

    project_base_path = android_project_path
    libs_json = json.load(open(os.path.join(script_path, 'libs.json'), 'r'))

    if len(sys.argv) >= 3:
        libs_json = json.loads(sys.argv[2])
    if len(sys.argv) >= 2:
        project_base_path = sys.argv[1]

    print('project_base_path: {}'.format(project_base_path))
    print('libs_json: {}'.format(libs_json))

    for arg_sdk_name in ['docsviewsdk']:
        lib_info = libs_json[arg_sdk_name]
        if len(lib_info['version']) > 0:
            update(arg_sdk_name, lib_info['remote'], lib_info['lib_name'], lib_info['version'], lib_info['local'])