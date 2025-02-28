import argparse
import sys
import io
import os
import struct
import subprocess
import re
import shutil
import json


class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help()


def check_install(name):
    result = subprocess.run(["which", name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0


def get_file_name_without_extension(file_path):
    file_name, _ = os.path.splitext(os.path.basename(file_path))
    return file_name


def run_command(command, shell=False):
    # 运行命令并捕获输出
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True, shell=shell
    )

    # 实时读取并显示标准输出
    for line in iter(process.stdout.readline, ''):
        print(line, end='')

    # 等待进程结束并获取返回码
    process.stdout.close()
    process.wait()

    # 获取标准错误输出（如果有）
    stderr_output = process.stderr.read()

    # 如果有错误输出，显示
    if stderr_output:
        print(f"错误信息: {stderr_output}")

    return process.returncode


def unpack_dmg(dmg_file, dir_path):
    if not dmg_file:
        print(
            f"未找到包含 deveco-studio*.dmg 镜像,请下载 Mac (X86) 版本的 DevEco Studio ,解压并且将dmg镜像放进文件夹{dir_path}")
        print("https://developer.huawei.com/consumer/cn/download/")
        sys.exit(1)
    deveco_studio_result = os.path.join(dir_path, f"{get_file_name_without_extension(dmg_file)}.txt")
    img_file = os.path.join(dir_path, "deveco-studio.img")
    img_dir = os.path.join(dir_path, "DevEco-Studio-Img")
    dev_eco_studio_dir = os.path.join(img_dir, "DevEco-Studio")
    hfsx_file = os.path.join(img_dir, "disk image.hfsx")
    try:
        if not os.path.exists(deveco_studio_result):
            if os.path.exists(img_file):
                os.remove(img_file)
            if os.path.exists(hfsx_file):
                os.remove(hfsx_file)
            if os.path.exists(img_dir):
                shutil.rmtree(img_dir)
            return_code = run_command(["dmg2img", dmg_file, img_file])
            if return_code != 0:
                print(
                    f"{dmg_file}转换失败")
                sys.exit(1)
            return_code = run_command(["7z", "x", img_file, f"-o{img_dir}"])
            if return_code != 0:
                print(
                    f"{dmg_file}解包失败")
                sys.exit(1)
            return_code = run_command(["7z", "x", hfsx_file, f"-o{img_dir}"])
            with open(deveco_studio_result, "x") as file:
                pass
    except Exception as e:
        print(f"{e}")
        sys.exit(1)
    return dev_eco_studio_dir


def unpack_ctl(ctl_file, dir_path):
    if not ctl_file:
        print(
            f"未找到包含 commandline-tools-linux 压缩文件,请下载 Linux 版本的 commandline-tools ,解压并且将zip文件放进文件夹{dir_path}")
        print("https://developer.huawei.com/consumer/cn/download/")
        sys.exit(1)
    ctl_dir = os.path.join(dir_path, "command-line-tools")
    ctl_result = os.path.join(dir_path, f"{get_file_name_without_extension(ctl_file)}.txt")
    try:
        if not os.path.exists(ctl_result):
            if os.path.exists(ctl_dir):
                shutil.rmtree(ctl_dir)
            return_code = run_command(["unzip", ctl_file, "-d", dir_path])
            if return_code != 0:
                print(
                    f"{ctl_dir}解压失败")
                sys.exit(1)
            return_code = run_command(["chmod", "a+xw", "-R", ctl_dir])
            with open(ctl_result, "x") as file:
                pass
    except Exception as e:
        print(f"{e}")
        sys.exit(1)
    return ctl_dir


def read_json_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        return data
    except json.JSONDecodeError as e:
        print(f"JSON 解码错误: {e}")
    except FileNotFoundError:
        print(f"文件 '{file_path}' 不存在。")
    except Exception as e:
        print(f"发生错误: {e}")


def get_version(build_number):
    version_parts = build_number.split('.')
    return int(version_parts[0]), int(version_parts[1]), int(version_parts[2])


def copy_jar_files(src_dir, dest_dir):
    if not os.path.exists(dest_dir):
        return

    for root, _, files in os.walk(src_dir):
        for file in files:
            if file.endswith(".jar"):
                relative_path = os.path.relpath(root, src_dir)
                target_dir = os.path.join(dest_dir, relative_path)
                os.makedirs(target_dir, exist_ok=True)
                src_file = os.path.join(root, file)
                dest_file = os.path.join(target_dir, file)

                shutil.copy2(src_file, dest_file)
                print(f"已复制: {src_file} -> {dest_file}")


def copy_directory_with_structure(src_dir, dest_dir):
    try:
        for root, dirs, files in os.walk(src_dir):
            relative_path = os.path.relpath(root, src_dir)
            target_dir = os.path.join(dest_dir, relative_path)
            os.makedirs(target_dir, exist_ok=True)
            for file in files:
                src_file = os.path.join(root, file)
                dest_file = os.path.join(target_dir, file)

                shutil.copy2(src_file, dest_file)
                print(f"已复制: {src_file} -> {dest_file}")
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)


def to_absolute_path(path):
    if not os.path.isabs(path):
        abs_path = os.path.abspath(path)
        return abs_path
    else:
        return path


def copy_sdk(ctl_dir, idea_dir):
    sdk_dir = os.path.join(ctl_dir, "sdk")
    copy_directory_with_structure(sdk_dir, os.path.join(idea_dir, "sdk"))

    hvigor_dir = os.path.join(ctl_dir, "hvigor")
    copy_directory_with_structure(hvigor_dir, os.path.join(idea_dir, "tools/hvigor"))

    ohpm_dir = os.path.join(ctl_dir, "ohpm")
    copy_directory_with_structure(ohpm_dir, os.path.join(idea_dir, "tools/ohpm"))

    node_dir = os.path.join(ctl_dir, "tool/node")
    copy_directory_with_structure(node_dir, os.path.join(idea_dir, "tools/node"))

    llvm_dir = os.path.join(dev_eco_studio_app_dir, "tools/llvm")
    copy_directory_with_structure(llvm_dir, os.path.join(idea_dir, "tools/llvm"))


def link_file(src_path, dst_path):
    if not os.path.exists(dst_path) and (os.path.exists(src_path) or not os.path.isabs(src_path)):
        run_command(["ln", "-s", src_path, dst_path])


def link_sdk(ctl_dir, idea_dir, dev_eco_studio_app_dir, is_absolute_path):
    if not is_absolute_path:
        ctl_dir = "../command-line-tools"

    sdk_dir = os.path.join(ctl_dir, "sdk")
    link_file(sdk_dir, os.path.join(idea_dir, "sdk"))

    idea_tools_dir = os.path.join(idea_dir, "tools")
    if not os.path.exists(idea_tools_dir):
        os.makedirs(idea_tools_dir, exist_ok=True)

    if not is_absolute_path:
        ctl_dir = f"../{ctl_dir}"
    hvigor_dir = os.path.join(ctl_dir, "hvigor")
    link_file(hvigor_dir, os.path.join(idea_tools_dir, "hvigor"))

    ohpm_dir = os.path.join(ctl_dir, "ohpm")
    link_file(ohpm_dir, os.path.join(idea_tools_dir, "ohpm"))

    node_dir = os.path.join(ctl_dir, "tool/node")
    link_file(node_dir, os.path.join(idea_tools_dir, "node"))

    llvm_dir = os.path.join(dev_eco_studio_app_dir, "tools/llvm")
    copy_directory_with_structure(llvm_dir, os.path.join(idea_dir, "tools/llvm"))


def copy_to_idea(dev_eco_studio_app_dir, idea_dir, ctl_dir, product_info_json, prefix_path, dmg_name, major, minor,
                 jbrsdk_tar, deveco_java_agent_jar):
    try:
        jars_result = os.path.join(dev_eco_studio_app_dir, f"{dmg_name}.txt")
        version_txt = None
        if not os.path.exists(jars_result):
            idea_lib_dir = os.path.join(idea_dir, "lib")
            idea_plugins_dir = os.path.join(idea_dir, "plugins")

            shutil.rmtree(idea_plugins_dir)
            dev_eco_studio_lib_dir = os.path.join(dev_eco_studio_app_dir, "lib")
            dev_eco_studio_plugins_dir = os.path.join(dev_eco_studio_app_dir, "plugins")

            app_client_jar = os.path.join(dev_eco_studio_lib_dir, "app-client.jar")
            # if os.path.exists(app_client_jar):
            #     os.remove(app_client_jar)

            copy_jar_files(dev_eco_studio_lib_dir, idea_lib_dir)
            copy_directory_with_structure(dev_eco_studio_plugins_dir, idea_plugins_dir)

            hamony_tool_home = os.environ.get('HAMONY_TOOL_HOME')
            is_absolute_path = True
            jbr_dir = os.path.join(idea_dir, "jbr")
            if major >= 5:
                if hamony_tool_home and prefix_path:
                    is_absolute_path = os.path.join(prefix_path, "command-line-tools") == hamony_tool_home
                    tmp = os.path.join(prefix_path, "command-line-tools")
                    if re.search(tmp, hamony_tool_home):
                        index = hamony_tool_home.index(tmp)
                        if index == 0:
                            is_absolute_path = len(hamony_tool_home) - (index + len(tmp)) > 1
                if hamony_tool_home and os.path.exists(hamony_tool_home):
                    link_sdk(hamony_tool_home, idea_dir, dev_eco_studio_app_dir, is_absolute_path)
                elif prefix_path:
                    link_sdk(hamony_tool_home, idea_dir, dev_eco_studio_app_dir, False)
                else:
                    copy_sdk(ctl_dir, idea_dir)
            else:
                hvigor_dir = os.path.join(dev_eco_studio_app_dir, "tools/hvigor")
                copy_directory_with_structure(hvigor_dir, os.path.join(idea_dir, "tools/hvigor"))

                llvm_dir = os.path.join(dev_eco_studio_app_dir, "tools/llvm")
                copy_directory_with_structure(llvm_dir, os.path.join(idea_dir, "tools/llvm"))

                # ohpm_dir = os.path.join(ctl_dir, "ohpm")
                # run_command(f"cd {ohpm_dir}&&zip -r ../ohpm.zip  .", True)
                shutil.copy2(os.path.join(dev_eco_studio_app_dir, "tools/ohpm.zip"),
                             os.path.join(idea_dir, "tools/ohpm.zip"))

                jbrsdk_dir = None
                if jbrsdk_tar and os.path.exists(jbrsdk_tar):
                    jbrsdk_dir = jbrsdk_tar[:jbrsdk_tar.index(".tar.gz")]
                if not jbrsdk_dir:
                    print(
                        f"未找到包含 jbrsdk_jcef-17.0.6-linux-x64-b829.1.tar.gz 文件,请下载并且将文件夹放进{dir_path}")
                    print("https://github.com/JetBrains/JetBrainsRuntime/releases/tag/jbr-release-17.0.6b829.1")
                    sys.exit(1)

                result = run_command(f"tar -xvzf  {jbrsdk_tar} -C  {dir_path}", True)
                if result != 0:
                    print(
                        f"jbrsdk_jcef-17.0.6-linux-x64-b829.1.tar.gz 解压出错")
                    sys.exit(1)

                if os.path.exists(jbr_dir):
                    shutil.rmtree(jbr_dir)
                copy_directory_with_structure(jbrsdk_dir, jbr_dir)

                if os.path.exists(deveco_java_agent_jar):
                    shutil.copy2(deveco_java_agent_jar,
                                 os.path.join(idea_dir, "bin/deveco-java-agent.jar"))
                    version_txt = os.path.join(idea_dir, "bin/version.txt")   
                    with open(version_txt, "w") as file:
                        file.write(f"{major}.{minor}")
            run_command(
                f"cd {jbr_dir}&&mkdir -p Contents/Home&&ln -s ../../bin ./Contents/Home/bin", True)
            devecostudio_svg = "bin/devecostudio.svg"
            shutil.copy2(os.path.join(dev_eco_studio_app_dir, devecostudio_svg),
                         os.path.join(idea_dir, devecostudio_svg))

            with open(jars_result, "x") as file:
                pass

        idea_sh = os.path.join(idea_dir, "bin/idea.sh")
        idea_bak_sh = os.path.join(idea_dir, "bin/idea_bak.sh")

        if not os.path.exists(idea_bak_sh):
            shutil.copy2(idea_sh,
                         idea_bak_sh)

        launch = product_info_json["launch"][0]
        boot_class_path_jar_names = launch["bootClassPathJarNames"]
        additional_jvm_arguments = launch["additionalJvmArguments"]

        class_path_list = []
        for index, boot_class_path_jar_name in enumerate(boot_class_path_jar_names):
            if index == 0:
                class_path_list.append(f"CLASS_PATH=\"$IDE_HOME/lib/{boot_class_path_jar_name}\"\n")
            else:
                class_path_list.append(f"CLASS_PATH=\"$CLASS_PATH:$IDE_HOME/lib/{boot_class_path_jar_name}\"\n")
        vendor_name = None
        paths_selector = None
        platform_prefix = None
        for additional_jvm_argument in additional_jvm_arguments:
            if "idea.vendor.name" in additional_jvm_argument:
                vendor_name = additional_jvm_argument
            elif "idea.paths.selector" in additional_jvm_argument:
                paths_selector = additional_jvm_argument
            elif "idea.platform.prefix" in additional_jvm_argument:
                platform_prefix = additional_jvm_argument

        with open(idea_bak_sh, 'r') as file:
            is_append_class_path = False
            is_split_d = False
            result = []
            for line in file:
                if is_split_d and line.strip().startswith("-D"):
                    arr = line.strip().split(" ")
                    for index, item in enumerate(arr):
                        if item.startswith("-Didea.vendor.name") and vendor_name:
                            result.append(f"{vendor_name}")
                        elif item.startswith("-Didea.paths.selector") and paths_selector:
                            result.append(f"{paths_selector}")
                        elif item.startswith("-Didea.platform.prefix") and platform_prefix:
                            result.append(f"{platform_prefix}")
                        elif len(arr) - 1 == index:
                            result.append(" \\\n")
                        else:
                            result.append(f"{item}")
                        if len(arr) - 2 > index:
                            result.append(" \\\n")
                    if major < 5:
                        result.append("\"-DIDE_HOME=$IDE_HOME\" \\\n")
                        result.append("\"-javaagent:$IDE_HOME/bin/deveco-java-agent.jar\" \\\n")
                    is_split_d = False
                    continue

                if not line.strip().startswith("CLASS_PATH"):
                    result.append(line)
                    if line.strip().startswith("${IDE_PROPERTIES_PROPERTY}"):
                        is_split_d = True
                elif not is_append_class_path:
                    is_append_class_path = True
                    result.extend(class_path_list)

        content = ''.join(result)
        # print(f"content:{content}")
        with open(idea_sh, 'w') as file:
            file.write(content)
    except Exception as e:
        print(f"发生错误: {e}")
        sys.exit(1)


def create_desktop(install_path, major):
    if major:
        major = f"-{major}"
    desktop_content = f"""[Desktop Entry]
Name=DevEco-Studio{major}
Exec=\"{install_path}/bin/idea.sh\" %f
Icon={install_path}/bin/devecostudio.svg
Type=Application
Categories=Development;Hamony;IDE;
Terminal=false
StartupWMClass=huawei-deveco-studio{major}
StartupNotify=true"""
    home_dir = os.path.expanduser("~")
    desktop_path = os.path.join(home_dir, f".local/share/applications/DevEco-Studio{major}.desktop")
    with open(desktop_path, 'w') as file:
        file.write(desktop_content)


if __name__ == "__main__":
    parser = CustomArgumentParser(description="将DevEco-Studio进行Ubuntu移植")
    parser.add_argument('-d', '--dir', type=str,
                        help='包含deveco-studio*.img和commandline-tools-linux-x64*.zip文件夹路径')
    parser.add_argument('-p', '--prefix', type=str,
                        help='安装路径,有安装路径会创建快捷图标')
    parser.add_argument('-dcd', '--disable_create_desktop', type=str,
                        help='是否创建创建快捷图标')

    if not check_install("7z") or not check_install("dmg2img"):
        msg = "安装 p7zip-full, dmg2img 失败"
        try:
            subprocess.run(["sudo", "apt", "install", "-y", "p7zip-full", "dmg2img"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"{msg}：{e}")
            sys.exit(1)

    stderr_backup = sys.stderr
    sys.stderr = io.StringIO()

    args, unknown = parser.parse_known_args()
    dir_path = args.dir
    if not dir_path:
        if unknown:
            dir_path = unknown[0]
        else:
            sys.exit(1)
    dir_path = to_absolute_path(dir_path)
    if not os.path.exists(dir_path):
        print(f"{dir_path} 不存在")
        sys.exit(1)

    files = [f for f in os.listdir(dir_path)]
    dmg_file = None
    ctl_file = None
    idea_dir = None
    jbrsdk_tar = None
    current_dir = os.path.dirname(os.path.abspath(__file__))
    deveco_java_agent_jar = os.path.join(current_dir, "deveco_java_agent.jar")
    for file in files:
        if re.match(r"deveco-studio-.*\.dmg", file):
            dmg_file = os.path.join(dir_path, file)
        if re.match(r"commandline-tools-linux-.*\.zip", file):
            ctl_file = os.path.join(dir_path, file)
        if re.match(r"idea-IC-*", file):
            idea_dir = os.path.join(dir_path, file)
        if re.match(r"jbrsdk_jcef-17.0.6-linux-x64-b829.1.tar.gz", file):
            jbrsdk_tar = os.path.join(dir_path, file)

    dev_eco_studio_dir = unpack_dmg(dmg_file, dir_path)
    dev_eco_studio_app_dir = os.path.join(dev_eco_studio_dir, "DevEco-Studio.app/Contents")

    product_info_json = read_json_file(os.path.join(dev_eco_studio_app_dir, "Resources/product-info.json"))

    # hamony_tool_home = os.environ.get('HAMONY_TOOL_HOME')
    # ctl_dir = None
    # if not hamony_tool_home or not os.path.exists(hamony_tool_home):
    ctl_dir = unpack_ctl(ctl_file, dir_path)

    build_number = product_info_json["buildNumber"]
    version = product_info_json["version"]
    idea_major, idea_minor, idea_patch = get_version(build_number)
    major, minor, patch = get_version(version)
    idea_name = f"idea-IC-{idea_major}.{idea_minor}.{idea_patch}"
    if not idea_dir or not idea_dir.endswith(idea_name):
        print(
            f"未找到包含 {idea_name} 文件夹,请下载 Linux 版本 IntelliJ IDEA Community Edition 的 Linux x86_64 (tar.gz) ,解压并且将文件夹放进{dir_path}")
        print("https://www.jetbrains.com/zh-cn/idea/download/other.html")
        sys.exit(1)

    prefix_path = args.prefix
    copy_to_idea(dev_eco_studio_app_dir, idea_dir, ctl_dir, product_info_json, prefix_path,
                 get_file_name_without_extension(dmg_file), major, minor, jbrsdk_tar, deveco_java_agent_jar)

    if prefix_path:
        if not os.path.exists(prefix_path):
            os.makedirs(prefix_path)
        install_path = os.path.join(prefix_path, "DevEco-Studio")
        prefix_ctl_path = os.path.join(prefix_path, "command-line-tools")
        desktop_major = ""
        if major < 5:
            desktop_major = f"{major}.{minor}"
            install_path = os.path.join(prefix_path, f"DevEco-Studio-{desktop_major}")
            prefix_ctl_path = os.path.join(install_path, "command-line-tools")

        if os.path.exists(install_path):
            shutil.rmtree(install_path)
        shutil.copytree(idea_dir, install_path, symlinks=True)
        copy_directory_with_structure(ctl_dir, prefix_ctl_path)
        if args.disable_create_desktop is None or not args.disable_create_desktop:
            create_desktop(install_path, f"{desktop_major}")
        print(f"转换完成,并且安装路径:{install_path}")
    else:
        print(f"转换完成路径:{idea_dir}")
