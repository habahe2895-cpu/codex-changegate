# Codex ChangeGate（中文说明）

为 AI 辅助开发团队提供一套简单、可审计的 GitHub PR 多人审批门禁。适用于 Codex、Claude Code 或其他开发工具生成的代码；运行时不需要购买 AI API。

## 当前实现

- 按路径设置保护范围，例如 `infra/**` 和 `.github/workflows/**`。
- 按 GitHub 用户名指定有审批权的成员。
- 指定最低有效审批票数（如 2 人）。
- 默认禁止 PR 作者给自己投票，并且新提交后旧批准票失效。
- 使用 GitHub 原生的 PR Review，不需要安装单独的机器人。
- 内置 GitHub Actions；使用只读 GitHub API，不执行 PR 分支的代码。
- 提供自动化单元测试及离线演示数据。

## 在电脑上立即体验

安装 Python 3.10 或更新版本，在项目根目录运行：

```bash
python -m changegate check --config examples/sample-policy.json --fixture examples/approved-pr.json
python -m changegate check --config examples/sample-policy.json --fixture examples/blocked-pr.json
python -m unittest discover -s tests -v
```

第一条应显示 `PASS`，第二条应显示 `BLOCK` 并返回退出码 1。演示投票为虚构测试数据，并不是 GitHub 上的真实审批。

## 运行到 GitHub

1. 将项目文件提交到公共仓库的 `main` 分支。
2. 修改 `.changegate.json` 中的 `voters` 与 `minimum_approvals`，填写真实审核成员。
3. 在 GitHub 仓库 `Settings` 中配置 `main` 分支的保护规则，强制要求 `ChangeGate / vote-gate` 状态检查通过后才能合并。
4. 打开修改受保护文件的 Pull Request，让受信任审核者提交 GitHub 的 `Approve` 审核。

**重要：** 只配置工作流但不配置分支保护，无法保证阻止合并。当前版本属于 0.1.0 原型，尚未经过线上仓库端到端验证。单人开发时，作者默认不能审核自己的高风险改动，这是有意的安全限制。

完整功能、配置、安全边界及贡献说明请查看英文 [README](README.md)、[SECURITY](SECURITY.md) 与 [CONTRIBUTING](CONTRIBUTING.md)。

本项目与 OpenAI 无关联，使用 MIT 许可证发布。
