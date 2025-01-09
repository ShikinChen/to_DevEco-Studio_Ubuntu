### 将Mac的DevEco-Studio进行Ubuntu的移植

暂时 DevEco-Studio 只有 Mac 和 Windows 版, DevEco-Studio 是基于 idea 社区版进行开发,所以移植也是基于 idea
社区版,但是华为有些jar、插件和模拟器涉及到c++的动态库,肯定有些功能没办法使用,但是不影响编程和打包happ,
也希望华为快点出Linux版本

#### 所有操作在终端进行

#### 拉取项目

```shell
git clone https://github.com/ShikinChen/to_DevEco-Studio_Ubuntu.git
```

#### 安装必要工具(可选)

如果没有安装,使用脚本也会提示安装,如果担心脚本植入什么东西,可以先进行安装,这个唯一使用 sudo 地方

```shell
sudo apt install p7zip-full dmg2img -y
```

#### [command-line-tools](https://developer.huawei.com/consumer/cn/download/) 环境配置(可选,下载Linux版本)

不一定配置,如果以后需要使用[鸿蒙的flutter](https://gitee.com/openharmony-sig/flutter_flutter)
进行开发还是建议配置,也可以节省一定硬盘空间<br>
编辑~/.bashrc

```shell
vim ~/.bashrc
```

解压后根据自己放置路径修改下面 HAMONY_HOME 配置路径,然后在~/.bashrc追加下面配置

```shell
# HamonyOS SDK
export HAMONY_HOME=/path/Hamony #放置command-line-tools的父目录,下面不变
export HAMONY_TOOL_HOME=$HAMONY_HOME/command-line-tools
export DEVECO_SDK_HOME=$HAMONY_TOOL_HOME/sdk
export PATH=$HAMONY_TOOL_HOME/ohpm/bin:$PATH
export PATH=$HAMONY_TOOL_HOME/hvigor/bin:$PATH
export PATH=$HAMONY_TOOL_HOME/node/bin:$PATH
export PATH=$HAMONY_TOOL_HOME/sdk/default/openharmony/toolchains/:$PATH
```

重新加载

```shell
source ~/.bashrc
```

#### 进行转换

下载[Mac (X86) 版本的 DevEco Studio ](https://developer.huawei.com/consumer/cn/download/)
和[Linux版本 command-line-tools ](https://developer.huawei.com/consumer/cn/download/),然后解压DevEco
Studio的压缩包得到dmg镜像,然后将dmg镜像和command-line-tools压缩包放到to_DevEco-Studio_Ubuntu文件夹,如果知道DevEco
Studio使用[idea社区版版本可以提前下载]((https://www.jetbrains.com/zh-cn/idea/download/other.html))
,并且解压得到类似idea-IC-233.14475.28文件夹,不是ideaIC-2023.3.4这种,不知道也没关系脚本也会提示版本号,
也放在to_DevEco-Studio_Ubuntu文件夹<br>
目录结构例如:

```shell
├── commandline-tools-linux-x64-5.0.5.310.zip
├── deveco-studio-5.0.5.315.dmg
├── idea-IC-233.14475.28
└── to_ubuntu.py
```

```shell
cd to_DevEco-Studio_Ubuntu
python3 ./to_ubuntu.py -d ./ -p 安装路径
```

安装成功后会生成应用快捷图标DevEco-Studio