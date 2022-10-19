解析obsidian笔记为hexo支持的格式并发布到github pages, 支持双链和本地资源迁移.

**原理**

发布时发布工具自动检测 obsidian 中带 `#share` 标签的markdown笔记,解析并添加 hexo metadata

**示例**

https://qiaogaojian.github.io/7754587453101531348/

**配套 Hexo 仓库**

https://github.com/qiaogaojian/note_hexo

**使用**

- 根据注释配置工具同名的配置文件
- 需要发布的笔记添加发布标签(默认`#share`)
- 运行release下的 `obsidian2hexo.exe` 或者直接运行脚本(需要安装 python3.6+ 运行环境并配置环境变量)
```sh
python obsidian2hexo.py
```

默认后台运行, 想看进度的话可以在程序目录的log文件夹查看日志

**TODO**

- 定期自动同步+发布
- 做成 Obsidian 插件的形式
