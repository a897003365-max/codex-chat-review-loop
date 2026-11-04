# 本机回执与验收消息

先把本轮材料放入专用目录。例如 `result.txt` 供上传，`evidence.json` 供 Chat 在本机读取，另可放一份准确绑定当前工作树的补丁。证据按任务选择：实际入口、基线与验收阈值、复测方法、必要原始样本、测试结果和剩余缺口。对在线行为，记录正在提供服务的版本或资源哈希。保存数量或哈希足以验收时，省略个人记录、密钥、Cookie、账单明细和原始会话。

### 准备本轮回执

调用随技能安装的 [receipt.py](../scripts/receipt.py)，只需 Python 3.8+ 标准库。脚本读取明确点名的文件，在回执同目录下解析相对路径，并拒绝目录越界及覆盖旧回执。目录和文件名替换成当前任务的实际位置。

```powershell
$root = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $env:USERPROFILE '.codex' }
$receiptTool = Join-Path $root 'skills/codex-chat-review-loop/scripts/receipt.py'
# 在本轮材料目录运行，result.txt 与 evidence.json 已经生成。
python -X utf8 -B $receiptTool create local-receipt.json --round R1 result.txt evidence.json
```

每轮正式 Pro 送审先按 [SKILL.md](../SKILL.md) 新开独立普通 Chat，核对空白上下文、Chat/Work 模式、Pro 选择器和已选插件；发送后记录新的 conversation ID。把 `result.txt` 上传至本轮已选插件的普通 Chat。消息里给出 `local-receipt.json` 和证据在**远端设备**上的绝对路径。回执和回读码仅由 Chat 从本机获取；同轮开始后保持材料稳定。如需修改，准备下一轮材料并生成新回执。

### 可直接改写的审阅提示

> 请独立正式验收本轮成果。任务为〈任务标识〉、轮次为〈轮次〉，附件是〈报告名〉。本轮背景如下：任务前因与目标〈内容〉；用户最终需求及有效变更〈内容〉；当前行为与不做范围〈内容〉；送审版本/哈希〈值〉；已做检查及结果〈内容〉；未做检查〈内容〉；证据路径〈路径〉；逐项验收清单〈清单〉。若为返修或补件，必要的客观问题是〈问题〉，本轮变化是〈变化，含实现是否变更〉。请仅依据本轮材料与亲自核验作判断。请使用已选中的 Remote Desktop Commander 调用 list_devices，选中〈目标电脑〉，再用 read_file 读取〈回执绝对路径〉及〈证据绝对路径〉。请回传回执中的轮次和 readback_code，核对文件哈希，并针对〈关键验收项〉独立复算或执行授权的只读检查。明确哪些动作是你亲自执行，哪些结论来自你读到的测试记录。权限仅限上述范围内的只读核验，不要写入设备或代为部署。输出格式为各项结论与依据、亲自执行和读取记录的区分、未覆盖项及必修项，最后单列 PASS、CHANGES_NEEDED、NEEDS_DATA 或 BLOCKED。设备不可读时说明具体错误。

完整答复返回后，用其中的实际值运行：

```powershell
python -X utf8 -B $receiptTool check local-receipt.json --round R1 --readback '从本轮最终答复取得的值'
```

退出码 0 表示回读码、本轮标识、各送审路径解析后的目标和文件哈希均匹配。检查从原始相对路径重新解析，目录联接改向时，即使新目标内容相同也会拒绝。旧回执若缺少路径绑定，重新生成新一轮回执。还须审阅 Chat 的实际工具调用、实质判定及运行版本。若代码已变、附件在别的会话、只有工具中间消息，或校验失败，按 [SKILL.md](../SKILL.md) 的对应分支处理。
