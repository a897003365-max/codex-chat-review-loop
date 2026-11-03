# 通道、插件与配置

| 能力 | 使用方式及证据 |
| --- | --- |
| Codex 桌面会话工具 `codex-app-tools` | `read_thread` 按 threadId 读回用户指定的 Chat；引用预览为空时从 turnLimit=10 开始，按游标补齐。用户授权向指定既有对话发纯文本时可用 `send_message_to_thread`。模型和 thinking 覆盖只适用于 Codex 线程。 |
| 已登录的 ChatGPT 网页与浏览器控制 | 普通 Chat 创建、Pro 选择、附件上传、插件点选，用当前环境允许的浏览器工具操作。本机验证过 `mcp__cua_repl.js` 和 Chrome 浏览器扩展。先按该工具的初始化与页面读取规则操作。 |
| Remote Desktop Commander | Chat 端须能在撰写器选中此插件；Windows 本机须有已配对、在线的 Remote 客户端。设备端运行、Codex 端可读、Chat 实际完成读取分别核验。 |
| 本地相关技能 | 项目代码实施按适用的 `native-dev-workflow`；面向用户的文字按项目要求使用 `anti-defensive-writing`。浏览器动作遵循当前浏览器工具说明，Windows 原生应用操作按适用的 `computer-use`。创建或维护本技能用 `skill-creator`。这些辅助技能不决定对话模式。 |

### 普通 Chat 与 Pro

- 发现工具时检查当前 schema。`create_thread(target=chatgptWorkCloud)` 创建 **Work**，`projectless` 创建 **Codex**。新建普通 Chat 的已验证入口是已登录浏览器中的 ChatGPT 首页。独立标签页满足新会话；如明确要求独立系统窗口，另行核实窗口确实已创建。
- 对新聊天读取撰写器状态，例如“聊天”选中、“工作”未选中。打开模型选择器，按当时显示的选项选择 Pro，再检查收起后的控件文本。账户套餐、会话标题、“已发送”和模型自述均不能证明这一轮用了 Pro。指定 Pro 而账户不可选时，先作说明。
- 发第一条后，以服务端生成的 `/c/<id>` 固定对话；若地址仍含 `local-chatgpt:` 或其 URL 编码，等页面换成持久 ID 再记录。已有普通 Chat 再送审时，检查这个 ID、当轮档位及附件。可用原生工具读回正文；`kind=chatgpt` 单独不足以区分 Chat/Work。
- `wait_threads` 的适用范围以 schema 为准；曾在普通 Chat 上返回无法确定 Codex 线程。此时检查同一 Chat 的页面或 `read_thread`。原生快照可能滞后，也可能只含本轮用户消息。若只看到旧轮或截断回答，等到本轮最终正文完整；发送结果不明时先查原会话，避免重复投递。

### Windows 本机连接器

先查当前目标电脑是否已在相同账户的 Remote Desktop Commander `list_devices` 中 Online，并确认名称或设备 ID。多设备时显式向读取工具传所选 deviceId。已经在线就复用；离线时先检查本机是否已有匹配进程及其输出，避免多起一份。Windows 发起连接需要 Node.js、`npx.cmd`、网络和已有账户配对。

用户授权本机连接且需要隐藏启动时，以下 PowerShell 在**本任务已有的专用工作目录**执行。运行一次后再次核对本机日志的 connected/Online 与远端设备列表。已在运行但离线时先看原因。首次账户配对、登录、敏感权限或需要扩大允许目录时，按实际授权处理。

```powershell
Get-Command npx.cmd -ErrorAction Stop | Out-Null
$workDir = (Get-Location).Path
$tag = Get-Date -Format 'yyyyMMdd-HHmmss'
$startInfo = @{
  FilePath = $env:ComSpec
  ArgumentList = '/d /c npx --yes @wonderwhy-er/desktop-commander@latest remote'
  WorkingDirectory = $workDir
  WindowStyle = 'Hidden'
  RedirectStandardOutput = Join-Path $workDir "dc-$tag.out.log"
  RedirectStandardError = Join-Path $workDir "dc-$tag.err.log"
  PassThru = $true
}
$launcher = Start-Process @startInfo
$launcher.Id
```

此命令启动当前设备的后台连接。PID 只证明启动动作。配对链接和登录内容可能出现在启动日志，只摘取状态；不把原始日志放入附件、技能或长期记忆。配置沿用账户现有连接与访问范围。证据路径被拒绝时，可将本任务的脱敏副本置于已授权目录后重新生成回执。

### 附件与插件在同一条消息

1. 在目标普通 Chat 输入 `@Remote Desktop Commander`，从联想结果点选该插件。确认草稿中出现插件标签，或已发送消息出现插件链接。单独粘贴名称不能证明已挂载。
2. 选择“添加照片和文件/从计算机上传”。经浏览器工具操作时按其文件上传说明，在点击前监听 filechooser，再交给选择器本机绝对路径。等文件名出现、上传完成、发送按钮可用。需要补充文字时保留插件标签和附件。
3. 发出后核对用户消息中的文件名和插件，等待 Chat 调用工具。完成后保留原 Chat 链接和完整验收文字；按宿主要求保留可核对的截图。Chat 仅复述附件时请它补做本机读取。

### 本技能的发现位置

Codex 主版本位于 `$CODEX_HOME/skills/codex-chat-review-loop`，未设置 `CODEX_HOME` 时使用 `~/.codex/skills/` 下的同名目录。本机 Windows 的 `~/.agents/skills/codex-chat-review-loop` 是指向主版本的目录联接，维护时只编辑主版本，联接即时可见。用 `Get-Item` 的 LinkType/Target 及入口文件 SHA-256 核对。导出的 ZIP 是发布时的快照，更新后重新打包；其他平台的发现路径与浏览器能力按该平台确认。
