from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("helloworld", "YourName", "一个简单的 Hello World 插件", "1.0.0")
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)

    async def initialize(self):
        """可选择实现异步的插件初始化方法，当实例化该插件类之后会自动调用该方法。"""

    # 注册指令的装饰器。指令名为 helloworld。注册成功后，发送 `/helloworld` 就会触发这个指令，并回复 `你好, {user_name}!`
    @filter.command("helloworld")
    async def helloworld(self, event: AstrMessageEvent):
        """这是一个 hello world 指令""" # 这是 handler 的描述，将会被解析方便用户了解插件内容。建议填写。
        user_name = event.get_sender_name()
        message_str = event.message_str # 用户发的纯文本消息字符串
        message_chain = event.get_messages() # 用户所发的消息的消息链 # from astrbot.api.message_components import *
        logger.info(message_chain)
        yield event.plain_result(f"Hello, {user_name}, 你发了 {message_str}!") # 发送一条纯文本消息

    async def terminate(self):
        """可选择实现异步的插件销毁方法，当插件被卸载/停用时会调用。"""
import json
import traceback
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star
from astrbot.api import logger
from astrbot.core.computer.computer_client import get_booter, get_local_booter

class CustomShellPlugin(Star):
    """
    提供给 Subagent 专属的 Shell 执行工具，支持自动识别沙箱/本地环境
    """
    def __init__(self, context: Context):
        super().__init__(context)

    @filter.llm_tool(name="subagent_execute_shell")
    async def execute_shell(self, event: AstrMessageEvent, command: str, background: bool = False):
        """
        Execute a command in the shell.
        Args:
            command(string): The shell command to execute in the current runtime shell (for example, cmd.exe on Windows). Equal to 'cd {working_dir} && {your_command}'.
            background(boolean): Whether to run the command in the background.
        """
        try:
            # 1. 自动从系统配置中读取当前的运行模式 (local, sandbox, 或 none)
            cfg = self.context.get_config(umo=event.unified_msg_origin)
            provider_settings = cfg.get("provider_settings", {})
            runtime = str(provider_settings.get("computer_use_runtime", "local"))

            # 2. 根据模式获取对应的执行器（Booter）
            if runtime == "local":
                # 强制本地执行
                sb = get_local_booter()
            elif runtime == "none":
                return "Error: 系统设置中已禁用计算机使用权限（computer_use_runtime = none）。"
            else:
                # 否则（通常是 sandbox 模式），获取沙箱执行器
                # get_booter 会自动处理容器的启动和状态维护
                sb = await get_booter(
                    self.context,
                    event.unified_msg_origin,
                )
                logger.info(f"获取沙箱执行器成功: {sb}")
            
            # 3. 执行并返回结果
            result = await sb.shell.exec(command, background=background)
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Custom Shell Plugin Error: {traceback.format_exc()}")
            return f"Error executing command: {str(e)}"
