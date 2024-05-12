# yukakone-ai-plugin

[ゆかコネ](https://nmori.github.io/yncneo-Docs/)的LLM翻译插件

默认适配[Sakura](https://github.com/SakuraLLM/Sakura-13B-Galgame)的模型和接口，你也可以改成其他兼容OpenAI API的接口

## 使用方法

### 先决条件

1. 安装[ゆかコネ](https://nmori.github.io/yncneo-Docs/)
2. 安装Python 3.11以上版本，添加到PATH环境变量。如果你用了虚拟环境，要在虚拟环境的控制台中启动ゆかコネ
3. 安装依赖

    ```python
    pip install -r requirements.txt
    ```

4. （可选）[部署Sakura](https://github.com/SakuraLLM/Sakura-13B-Galgame/wiki/llama.cpp%E4%B8%80%E9%94%AE%E5%8C%85%E9%83%A8%E7%BD%B2%E6%95%99%E7%A8%8B)

### 设置ゆかコネ

1. 在关于讲话者里，把讲话者的语言设置为日语
2. 在翻译语音和引擎里，把第一个目标语言设置为简体中文，翻译引擎设置为关闭
3. 在 菜单 - 选项 里启用`减少翻译API的使用`和`最大限度的节约`

### 设置ゆかコネ插件

1. 在ゆかコネ的插件里启用`Python Connector`插件
2. 在Python Connector插件设置里点击`フォルダを開く`，打开Python插件目录
3. 把`llm_translator.py`文件复制到Python插件目录
4. 在Python Connector插件设置里点击`モジュール再読み込み`，重新加载Python插件。如果你在运行时修改了Python插件的内容，建议不要在这里重新加载，而是重启软件，否则可能会有多个Python插件版本同时运行
5. 在ゆかコネ手动输入内容测试，此时翻译应该已经生效，如果没有生效可以在Python插件目录看日志排查问题
