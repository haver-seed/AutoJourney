# Superpowers Skills — Project Activation

本项目使用 [Superpowers 中文增强版](https://github.com/jnMetaCode/superpowers-zh) 来组织开发工作流。

## 如何使用

当你收到任务时，检查 `.claude/commands/skills/` 中的技能是否适用：

1. **任何创造性工作之前**：使用 `brainstorming`
2. **实现功能/修 Bug**：使用 `test-driven-development`
3. **调试**：使用 `systematic-debugging`
4. **规划工作**：使用 `writing-plans`
5. **执行计划**：使用 `executing-plans` 或 `subagent-driven-development`
6. **代码审查**：使用 `requesting-code-review` 或 `receiving-code-review`
7. **Git 工作流**：使用 `using-git-worktrees` 或 `finishing-a-development-branch`

### 中国特色技能

8. **中文代码审查**：使用 `chinese-code-review`
9. **中文 Git 提交规范**：使用 `chinese-commit-conventions`
10. **中文文档规范**：使用 `chinese-documentation`
11. **国内 Git 平台适配**：使用 `chinese-git-workflow`
12. **MCP 服务端构建**：使用 `mcp-builder`
13. **YAML 工作流编排**：使用 `workflow-runner`

## Skills 位置

所有技能在 `.claude/commands/skills/` 下，每个目录包含 `SKILL.md` 详细说明。

## 规则

如果某个技能适用，必须使用它。不要因为"简单"而跳过技能。技能的存在是为了防止未经检视的假设。

## 用户指令优先

如果用户给出的具体指令与技能冲突，以用户指令为准。用户始终掌控。
