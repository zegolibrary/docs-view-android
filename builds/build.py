#!/usr/bin/env python -u
# coding: utf-8

import os
import sys
import shutil
import zipfile
import argparse
import json
import pathlib


def delete(path):
    """
    删除一个文件/文件夹
    :param path: 待删除的文件路径
    :return:
    """
    if not os.path.exists(path):
        print ("[*] {} not exists".format(path))
        return

    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.isfile(path):
        os.remove(path)
    elif os.path.islink(path):
        os.remove(path)
    else:
        print ("[*] unknow type for: " + path)

def clean_folder(folder):
    """
    删除文件夹下的所有内容
    :param folder: 待处理的文件夹路径
    :return:
    """
    if not os.path.isdir(folder):
        print ("[*] {} not dir or not exists".format(folder))
        return

    for name in os.listdir(folder):
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

def check_dir(mount_path,tmp_sdk_copy_dir):
    if not os.path.exists(mount_path):
        os.makedirs(mount_path)
    insure_empty_dir(tmp_sdk_copy_dir)
    print('check finished')

def umount_share(mount_path):
    if os.path.ismount(mount_path):
        result = os.system("umount -fv {0}".format(mount_path))
        if result == 0 :
            print('umount success')
        else:
            raise Exception('umount fail, result={}'.format(result))

def zego_mount_share_content(mount_path):
    # if "SHARE_TO_FOLDER" in os.environ:
    #     mount_dir = "share02/product/{}".format(arguments.share_folder)
    # else:
    mount_dir = "share02/product/zego_sdk"

    if not os.path.exists(mount_path):
        os.makedirs(mount_path)
    if os.path.ismount(mount_path):
        print('share is mounted,umount...')
        umount_share(mount_path)
    if not os.path.ismount(mount_path):
        insure_empty_dir(mount_path)
        mount_cmd = 'mount -t smbfs //share:share%40zego@192.168.1.3/{0} {1}'.format(mount_dir,mount_path)
        result = os.system(mount_cmd)
        if result == 0 :
            print('mount {} success'.format(mount_dir))
        else:
            '''
            if os.path.exists(mount_path):
                if os.path.ismount(mount_path):
                    umount_share(mount_path)
                if not os.path.ismount(mount_path):
                    clean_folder(mount_path)
                    delete(mount_path)
            '''
            raise Exception('mount fail, result:{} cmd:{}'.format(result, mount_cmd))

def get_zip_file(input_path, result):
    """
    对目录进行深度优先遍历
    :param input_path:
    :param result:
    :return:
    """
    files = os.listdir(input_path)
    for file in files:
        if os.path.isdir(input_path + '/' + file):
            get_zip_file(input_path + '/' + file, result)
        else:
            result.append(input_path + '/' + file)


def zip_file_path(input_path, output_path, output_name):
    """
    压缩文件
    :param input_path: 压缩的文件夹路径
    :param output_path: 解压（输出）的路径
    :param output_name: 压缩包名称
    :return:
    """
    f = zipfile.ZipFile(output_path + '/' + output_name, 'w', zipfile.ZIP_DEFLATED)
    filelists = []
    get_zip_file(input_path, filelists)
    for file in filelists:
        f.write(file)
    # 调用了close方法才会保证完成压缩
    f.close()
    return output_path + r"/" + output_name
#
# def collect_builds_src_path_content(android_project_path, builds_src_path):
#     # |- builds
#     #    |- build_src (builds_src_path)
#     #       |- app
#     #          | - libs     **两个viewsdk，express/liveroom其中一个都会拷贝到这里来，不然so进不了apk**
#     #       |- build.gradle
#     #       |- gradle
#     #       |- src
#
#     shutil.copytree(os.path.join(android_project_path, "app"), os.path.join(builds_src_path, 'app'))
#     shutil.copyfile(os.path.join(android_project_path, "build.gradle"), os.path.join(builds_src_path, "build.gradle"))
#     shutil.copytree(os.path.join(android_project_path, "gradle"), os.path.join(builds_src_path, 'gradle'))
#     shutil.copyfile(os.path.join(android_project_path, "gradle.properties"), os.path.join(builds_src_path, "gradle.properties"))
#     shutil.copyfile(os.path.join(android_project_path, "gradlew"), os.path.join(builds_src_path, "gradlew"))
#     shutil.copymode(os.path.join(android_project_path, "gradlew"), os.path.join(builds_src_path, "gradlew"))
#     shutil.copyfile(os.path.join(android_project_path, "gradlew.bat"), os.path.join(builds_src_path, "gradlew.bat"))
#     shutil.copyfile(os.path.join(android_project_path, "settings.gradle"), os.path.join(builds_src_path, "settings.gradle"))
#
#     shutil.copyfile(os.path.join(android_project_path, "README.md"), os.path.join(builds_src_path, "README.md"))
#     shutil.copytree(os.path.join(android_project_path, 'docs'), os.path.join(builds_src_path, 'docs'))
#
#     # 从两个gradle配置当中移除子模块源码目录
#     print('[*] hide submodule src in *.gradle')
#     hide_special_line(os.path.join(builds_src_path, "settings.gradle"), 'ZegoWhiteboardViewSDK')
#     hide_special_line(os.path.join(builds_src_path, "settings.gradle"), 'ZegoDocsViewSDK')
#     hide_special_line(os.path.join(builds_src_path, "app", "build.gradle"), 'ZegoWhiteboardViewSDK')
#     hide_special_line(os.path.join(builds_src_path, "app", "build.gradle"), 'ZegoDocsViewSDK')
#
#     # 在两个gradle配置当中，将以模块形式引入的liveroom/express干掉，因为待会选择一个拷贝到app/libs
#     print('[*] remove liveroom/express in *.gradle')
#     hide_special_line(os.path.join(builds_src_path, "settings.gradle"), 'zegoliveroomlib')
#     hide_special_line(os.path.join(builds_src_path, "settings.gradle"), 'zegoexpresslib')
#     hide_special_line(os.path.join(builds_src_path, "app", "build.gradle"), 'zegoliveroomlib')
#     hide_special_line(os.path.join(builds_src_path, "app", "build.gradle"), 'zegoexpresslib')
#
#     print('[*] remove hide_tag in *.gradle')
#     hide_special_line(os.path.join(builds_src_path, "app", "build.gradle"), 'hide_tag')
#
#
#     sdk_wrapper_path = os.path.join(builds_src_path, 'app', 'src', 'main', 'java', 'im', 'zego', 'whiteboardexample', 'sdk')
#     if fwd_dict['USE_LIBRARY'] == 'express':
#         os.remove(os.path.join(sdk_wrapper_path, 'rtc', 'ZegoLiveRoomWrapper.kt'))
#     else:
#         os.remove(os.path.join(sdk_wrapper_path, 'rtc', 'ZegoExpressWrapper.kt'))
#
def hide_special_line(patch_file_path, hide_tag):
    print ("hide_special_line {} for {}".format(hide_tag, patch_file_path))

    with open(patch_file_path, 'r') as patch_file:
        content = patch_file.readlines()

    for (index, line) in enumerate(content):
        if hide_tag in line :
            print ("find {} in line {}".format(hide_tag, index))
            content[index] = ""
    with open(patch_file_path, 'w+') as f:
        f.writelines(content)

def replace_special_line(patch_file_path, replace_tag):
    print ("replace_special_line {} for {}".format(replace_tag, patch_file_path))

    with open(patch_file_path, 'r') as patch_file:
        content = patch_file.readlines()

    for (index, line) in enumerate(content):
        if replace_tag in line :
            print ("find {} in line {}".format(replace_tag, index))
            replace_content_start_pos = line.find(replace_tag) + len(replace_tag)
            content[index] = line[replace_content_start_pos:]
    with open(patch_file_path, 'w+') as f:
        f.writelines(content)

def delete_project_temp_build_dirs(android_project_path):
    """
    删除一些build目录，节省拷贝时间
    """
    print("start to delete_project_temp_build_dirs")
    os.chdir(android_project_path)

    delete(os.path.join('.','build'))
    delete(os.path.join('.','app','build'))

class BuildExecutor:
    def __init__(self):
        print(os.environ)

    script_path = ''
    @staticmethod
    def _get_script_path():
        if len(BuildExecutor.script_path) == 0:
            BuildExecutor.script_path = os.path.dirname(os.path.realpath(__file__))
            print("_get_script_path: " + BuildExecutor.script_path)
        return BuildExecutor.script_path

    project_path = ''
    @staticmethod
    def _get_project_path():
        if len(BuildExecutor.project_path) == 0:
            BuildExecutor.project_path = os.path.abspath(os.path.join(BuildExecutor._get_script_path(), '..'))
            print("_get_project_path: " + BuildExecutor.project_path)
        return BuildExecutor.project_path

    def update_libs(self):
        libs_json = json.load(open(os.path.join(self._get_script_path(), 'libs.json'), 'r'))
        if len(os.environ.get('DOCSVIEW_SDK_VERSION')) > 0:
            libs_json['docsviewsdk']['version'] = os.environ.get('DOCSVIEW_SDK_VERSION')

        update_py_cmd = "python3 {} {} \"{}\"".format(os.path.join(self._get_script_path(), 'update_libs.py'), self._get_project_path(), json.dumps(libs_json).replace('\"', '\\"'))
        run_os_cmd(update_py_cmd, True)

        ls_cmd = "ls -al {}".format(os.path.join(self._get_project_path(), 'docsviewsdk'))
        run_os_cmd(ls_cmd)

    def submit_new_tag(self):
        release_tag = os.environ.get('RELEASE_TAG')
        print("RELEASE_TAG: " + release_tag)

        opensource_branch_name = "master"

        run_os_cmd("git add .")
        run_os_cmd("git status")
        run_os_cmd("git commit -m 'update version: {}'".format(release_tag))
        run_os_cmd("git push --set-upstream origin {}".format(opensource_branch_name))
        run_os_cmd("git tag {}".format(release_tag))
        run_os_cmd("git push --set-upstream origin {} --tags".format(opensource_branch_name))


def submit_opensource(self):
        project_path = self._get_project_path()
        auth_file_path = os.path.join(project_path, 'app', 'src', 'main', 'java', 'im', 'zego', 'superboarddemo', 'KeyCenter.java')
        replace_special_line(auth_file_path, 'replace_tag:')
        hide_special_line(os.path.join(project_path, 'app', 'src', 'main', 'java', 'im', 'zego', 'superboarddemo', 'KeyCenter.java'), 'hide_tag')

        login_activity_path = os.path.join(project_path, 'app', 'src', 'main', 'java', 'im', 'zego', 'superboarddemo', 'ui', 'login', 'LoginActivity.java')
        replace_special_line(login_activity_path, 'replace_tag:')
        hide_special_line(os.path.join(project_path, 'app', 'src', 'main', 'java', 'im', 'zego', 'superboarddemo', 'ui', 'login', 'LoginActivity.java'), 'hide_tag')
        hide_special_line(os.path.join(project_path, 'app', 'src', 'main', 'java', 'im', 'zego', 'superboarddemo', 'ui', 'setting', 'SettingActivity.java'), 'hide_tag')
        hide_special_line(os.path.join(project_path, 'app', 'src', 'main', 'java', 'im', 'zego', 'superboarddemo', 'sdk', 'rtc', 'ZegoRTCManager.java'), 'hide_tag')

        hide_special_line(os.path.join(project_path, "settings.gradle"), 'hide_tag')
        hide_special_line(os.path.join(project_path, "app", "build.gradle"), 'hide_tag')

        print('清空libs目录，添加.gitkeep')
        libs_path = os.path.join(project_path, 'app', 'libs')
        # 清空libs下各种SDK依赖库
        insure_empty_dir(libs_path)
        pathlib.Path(os.path.join(libs_path, '.gitkeep')).touch()

        print('删除编译生成')
        delete(os.path.join(project_path, '.gradle'))
        delete(os.path.join(project_path, '.idea'))
        delete(os.path.join(project_path, '.gitmodules'))
        delete(os.path.join(project_path, 'app', 'build'))
        delete(os.path.join(project_path, 'app', 'src', 'test'))
        delete(os.path.join(project_path, 'app', 'src', 'androidTest'))
        delete(os.path.join(project_path, 'build'))
        delete(os.path.join(project_path, 'superboard'))
        delete(os.path.join(project_path, 'whiteboardsdk'))

        print('源码替换到 release/opensource 分支')
        push_to_opensource_branch(project_path, project_path, self._get_build_version())

# if "STORE_PASSWORD" in os.environ:
#     store_password = os.environ["STORE_PASSWORD"]
# else:
#     store_password = None
#
# if "KEY_PASSWORD" in os.environ:
#     key_password = os.environ["KEY_PASSWORD"]
# else:
#     key_password = None

def push_to_opensource_branch(builds_src_path, android_project_path, version_name):
    print('builds_src_path: {}'.format(builds_src_path))
    print('android_project_path: {}'.format(android_project_path))

    os.chdir(android_project_path)

    opensource_branch_name = "release/opensource"

    try:
        run_os_cmd("git branch -D {}".format(opensource_branch_name))
    except Exception as e:
        print('\n Git cmd Exception at: {}\n'.format(e))

    try:
        run_os_cmd("git push origin --delete {}".format(opensource_branch_name))
    except Exception as e:
        print('\n Git cmd Exception at: {}\n'.format(e))

    run_os_cmd("git checkout -b {}".format(opensource_branch_name))

    print('delete builds folder')
    delete(os.path.join(android_project_path, 'builds'))

    run_os_cmd("git add .")
    run_os_cmd("git status")
    run_os_cmd("git commit -m 'submit opensource ver: {}'".format(version_name))
    run_os_cmd("git push --set-upstream origin {}".format(opensource_branch_name))

def run_os_cmd(git_command, silence = False):
    if not silence:
        print('% {}'.format(git_command))
    result = os.system(git_command)
    if result != 0:
        raise Exception('os.system fail, cmd:{}'.format(git_command))

if __name__ == '__main__':
    print("当前python版本", sys.version)

    builder = BuildExecutor()
    builder.update_libs()
    builder.submit_new_tag()