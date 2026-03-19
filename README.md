# AstrBot Subagent Shell 插件

这是一个为 AstrBot 子代理设计的 Shell 执行权限补丁。

## 简介

本插件旨在解决子代理（Subagent）人格在 “选择指定函数工具” 模式下，因为无法勾选系统内置终端工具导致无法执行shell命令的问题。

通过本插件，你可以直接在子代理的工具列表里勾选并授予其终端（Shell）执行权限。

## 功能

- 提供 `subagent_execute_shell` 工具，使subagent人格在白名单“选择指定函数工具” 模式下可以执行终端命令。
- 支持本地（Local）与沙箱（Sandbox）环境。

## 使用场景
当给subagent配置skills时,需要执行shell命令读取skill内容以指导subagent的决策。

## 安装方法

将插件安装至 `data/plugins/`。

## 注意事项

- **仅限子代理使用**：请勿在主 Agent 中勾选或使用此工具。主 Agent 已自带功能更全的终端处理权限，此工具仅为解决子代理配置痛点而设计。

---
