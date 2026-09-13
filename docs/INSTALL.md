# 从克隆目录安装

适用范围：Codex、Claude Code 的本地项目级和用户级技能目录。适配与实测状态见 [兼容性说明](COMPATIBILITY.md) 和 [测试报告](TEST_REPORT.md)。

## 获取源文件

```text
git clone https://github.com/cloudwallker/Reuse-Scout.git
cd Reuse-Scout
```

以下步骤均从这个克隆目录根目录开始。已有克隆时直接进入其根目录，确认存在 `skills/reuse-scout/SKILL.md`。安装只复制 **`skills/reuse-scout/` 整个目录**，包括 references、assets、agents 和随包许可；不复制仓库根目录、开发用 AGENTS.md、tests 或 tools。

下载 Release ZIP 时，先核对同版 `.sha256` 校验和，解压后以里面的 `reuse-scout/` 作为源目录。当前预览版是否已有远程标签和附件，以 GitHub 页面为准。

ZIP 用户先进入解压后的外层目录，确认当前目录下存在 `reuse-scout/SKILL.md`，然后执行下文对应宿主的首次安装步骤，只替换其中的源目录赋值行：

```powershell
$reuseSource = (Resolve-Path -LiteralPath './reuse-scout' -ErrorAction Stop).Path
```

```bash
reuse_source=$(realpath -e -- ./reuse-scout) || exit 1
```

以上是替换行，不是在原有源目录检查之后追加；目标选择、查重与复制步骤相同。ZIP 安装无需克隆仓库；开发和测试仍需完整克隆。

## 选择宿主和范围

| 宿主 | 项目级目录 | 用户级目录 | 宿主说明 |
| --- | --- | --- | --- |
| Codex | `.agents/skills/reuse-scout/` | `~/.agents/skills/reuse-scout/` | [Codex](INSTALL_CODEX.md) |
| Claude Code | `.claude/skills/reuse-scout/` | `~/.claude/skills/reuse-scout/` | [Claude Code](INSTALL_CLAUDE_CODE.md) |

项目级优先；用户级安装影响多个项目，仅在你选择后操作。`~` 指当前用户主目录，是宿主约定位置。

安装前记录源、目标、已有同名副本和备份位置。在目标项目相关父目录及所选宿主的用户级技能列表中，以 frontmatter 的 `name` 和宿主显示的来源查重。不要假设两个宿主的同名优先级相同。检查符号链接或 Windows 联接没有改变预期位置；源与目标不能相同或互相包含。

备份放在所有技能扫描目录之外。不要在 `.agents/skills` 或 `.claude/skills` 中保存 `reuse-scout-old` 等同名副本。

## Windows PowerShell：首次安装

在克隆根目录运行。Codex 使用 `codex`，Claude Code 将第一行改为 `claude-code`。目标项目可以输入相对于克隆目录的路径。

```powershell
$reuseHost = 'codex'
$reuseSkillRoots = @{ codex = '.agents/skills'; 'claude-code' = '.claude/skills' }
if (-not $reuseSkillRoots.ContainsKey($reuseHost)) { throw '不支持的宿主。' }
$reuseSource = (Resolve-Path -LiteralPath './skills/reuse-scout' -ErrorAction Stop).Path
$reuseProject = (Resolve-Path -LiteralPath (Read-Host '目标项目路径') -ErrorAction Stop).Path
if (-not (Test-Path -LiteralPath $reuseProject -PathType Container)) { throw '目标项目必须是目录。' }
$reuseParent = Join-Path $reuseProject $reuseSkillRoots[$reuseHost]
$reuseTarget = Join-Path $reuseParent 'reuse-scout'
[pscustomobject]@{ source = $reuseSource; target = $reuseTarget; host = $reuseHost }
Test-Path -LiteralPath $reuseTarget
```

用户级安装仅在你选择该范围时，用下一段重新设置目标。项目级跳过此段。

```powershell
$reuseUserRoot = [Environment]::GetFolderPath('UserProfile')
if ([string]::IsNullOrWhiteSpace($reuseUserRoot)) { throw '无法确定用户主目录。' }
$reuseParent = Join-Path $reuseUserRoot $reuseSkillRoots[$reuseHost]
$reuseTarget = Join-Path $reuseParent 'reuse-scout'
[pscustomobject]@{ source = $reuseSource; target = $reuseTarget; scope = 'user' }
```

核对输出并完成查重和链接检查；仅在目标不存在时复制，已存在则走更新步骤。

```powershell
if (Test-Path -LiteralPath $reuseTarget) { throw '目标已存在；请先按更新步骤处理。' }
if (Get-Item -LiteralPath $reuseTarget -Force -ErrorAction SilentlyContinue) { throw '目标已有目录项；请检查链接或旧副本。' }
New-Item -ItemType Directory -Path $reuseParent -Force -ErrorAction Stop | Out-Null
Copy-Item -LiteralPath $reuseSource -Destination $reuseTarget -Recurse -ErrorAction Stop
Get-Item -LiteralPath (Join-Path $reuseTarget 'SKILL.md') -ErrorAction Stop
```

目标必须直接包含 SKILL.md，不能再嵌套一层 reuse-scout。在新会话核对宿主实际加载来源。

## Linux Bash：首次安装

在克隆根目录运行。Claude Code 将第一行改为 `reuse_host=claude-code`。

```bash
reuse_host=codex
case "$reuse_host" in
  codex) reuse_skill_root=.agents/skills ;;
  claude-code) reuse_skill_root=.claude/skills ;;
  *) printf '%s\n' '不支持的宿主。'; exit 1 ;;
esac
reuse_source=$(realpath -e -- ./skills/reuse-scout) || exit 1
read -r -p '目标项目路径: ' reuse_project_input
reuse_project=$(realpath -e -- "$reuse_project_input") || exit 1
[ -d "$reuse_project" ] || { printf '%s\n' '目标项目必须是目录。'; exit 1; }
reuse_parent="$reuse_project/$reuse_skill_root"
reuse_target="$reuse_parent/reuse-scout"
printf 'source: %s\ntarget: %s\n' "$reuse_source" "$reuse_target"
```

用户级安装仅在你选择后，将复制前的目标赋值改为：

```bash
[ -n "$HOME" ] || { printf '%s\n' '无法确定用户主目录。'; exit 1; }
reuse_parent="$HOME/$reuse_skill_root"
reuse_target="$reuse_parent/reuse-scout"
printf 'source: %s\ntarget: %s\n' "$reuse_source" "$reuse_target"
```

核对路径、同名副本和链接后执行首次复制：

```bash
if [ ! -f "$reuse_source/SKILL.md" ]; then
  printf '%s\n' '源技能无效；停止复制。'
elif [ -e "$reuse_target" ] || [ -L "$reuse_target" ]; then
  printf '%s\n' '目标已存在；请先按更新步骤处理。'
else
  mkdir -p -- "$reuse_parent" && cp -R -- "$reuse_source" "$reuse_target"
fi
```

检查目标中的 SKILL.md、LICENSE、THIRD_PARTY_NOTICES.md。输出“目标已存在”不代表安装成功；不得重设 HOME 或宿主配置目录来解决安装问题。

## 更新、回退和卸载

1. 在克隆根目录运行 `git status --short`，保护本地修改。选择 GitHub 上确实存在的目标版本标签或提交，更新克隆中的源文件；不要把尚未发布的预览版本号当成现成标签。
2. 结束使用技能的会话，记录唯一安装目标。完整备份旧副本到所有扫描目录之外，并核对旧版本和内容。
3. 用文件管理器将已确认的旧安装目录移出扫描位置。确认目标不存在后，从更新后的克隆根目录重做首次复制；不要合并新旧文件。
4. 重新启动所选宿主，检查版本、来源和手动调用。回退时以完整旧备份替换同一目标，重新验收。
5. 卸载只移出或删除这一已确认的技能目录，保留其他技能及父级目录。若自行添加过该技能的禁用或覆盖设置，仅清理对应条目；新会话确认不再发现该副本。

两宿主调用与启停差异见各自说明。这些操作不自动改变模型、代理、MCP 或执行权限。
