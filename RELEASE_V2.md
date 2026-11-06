# HowToMakeMoneyOnYouTube · V2.0 发布说明

**时间**：2026-11-05｜**状态**：本地源码与部署包已生成；GitHub 仓库已创建，代码已提交；GitHub Pages 部署结果待核验。所有示例观看、询盘与收入均为标注的测试数据或假设，不是实际频道成绩。

## V2 的实质升级

| 子系统 | V1 | V2 |
| --- | --- | --- |
| 指南 | 20 章，重步骤 | 36 章，每章含具体案例、常见失败、验收门槛 |
| 选题库 | 12 条 | 36 条，有原创资产、观众及验证要求 |
| 执行计划 | 90 天任务 | 90 天任务 + 可检查的逐日完成证据 + 12 周选题日历 |
| 视频实战 | 基础录屏工作坊 | FreePhoto 长片 6–8 分钟完整脚本 + 2 Short 分镜 + 30 天工作坊 |
| 增长判断 | 手工反思 | 网站数据诊断 + CSV 本地分析 + 跨格式/来源/时间窗隔离 |
| 商业化 | 价格与合作说明 | 网站收入情景模拟 + 台账 + 线索归因 + 单位经济文档 |
| 发布审核 | Markdown 检查表 | manifest 文件存在性检查 + 必须人工审批的发布门禁 |
| 工程质量 | 9 项内容测试 | 22 项单元测试 + 2 种视口交互测试 + FFmpeg 两种分辨率导出验证 |

## 复现测试

```bash
python3 scripts/build.py
python3 -m unittest discover -s tests -v
node --check docs/assets/app.js
python3 tests/e2e_browser.py     # 可选：pip install playwright 并有 Chromium
python3 scripts/analyze_metrics.py examples/DEMO_ANALYTICS_INPUT.csv
python3 scripts/new_episode.py --slug first-real-episode --title "我的第一条完整实测"
# 将实际视频素材、封面、授权与来源整理完后再检查，默认应 BLOCK
python3 scripts/check_episode.py episodes/first-real-episode/manifest.json
```

**注意**：浏览器测试加载本地静态资源验证 DOM 与交互；上线后的 GitHub Actions/Pages、网络资源可用性、YouTube Studio 真实账户功能仍需在仓库发布后验证。FFmpeg 工具测试使用人工生成的音视频输入，不代表已拍摄真实 YouTube 视频。

## 发布到 GitHub

1. 打开 `https://github.com/new`，仓库名 `HowToMakeMoneyOnYouTube`，Public，先不要自动生成 README。
2. 在本地解压此项目 ZIP；在解压目录执行 `git init -b main`、`git add .`、`git commit -m "feat: faceless youtube playbook v2"`。
3. 执行 `git remote add origin https://github.com/AIPMAndy/HowToMakeMoneyOnYouTube.git` 与 `git push -u origin main`。
4. 仓库 Settings → Pages → Source 选择 GitHub Actions。检查 `ci.yml` 与 `pages.yml` 成功，再打开 Pages 链接。
5. 用真实 YouTube 频道做 4 周测试；**不可**把本站假设模型或模拟 CSV 写成真实成绩。

## 尚未解决的事情（不冒充完成）

- 未有第三方零基础学习者完成从 GitHub 到真实 YouTube 发布的完整可用性实验。
- 未接入真实 YouTube Studio 历史数据；目前数据分析需要先填写规范化 CSV。
- 未在新 YouTube 频道录制、发布第一条原创视频，也没有新频道真实收入。
- GitHub Pages URL 尚需启用并核验，所有 `https://github.com/AIPMAndy/HowToMakeMoneyOnYouTube` 仍是预期地址。
