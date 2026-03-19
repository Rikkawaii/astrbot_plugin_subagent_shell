import json
import traceback
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star
from astrbot.api import logger
from astrbot.core.computer.computer_client import get_booter, get_local_booter

@register("astrbot_plugin_subagent_shell", "Rikkawaii", "subagent shell", "1.0.0")
class SubagentShellPlugin(Star):
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
            
            # 3. 执行并返回结果
            result = await sb.shell.exec(command, background=background)
            return json.dumps(result)
            
        except Exception as e:
            logger.error(f"Custom Shell Plugin Error: {traceback.format_exc()}")
            return f"Error executing command: {str(e)}"
