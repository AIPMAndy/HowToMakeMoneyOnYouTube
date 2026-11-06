# 实战六：30 天从零到 4 条长视频 + 8 条 Shorts

**目标**：形成可持续的原创教程制作方法；不是保证 30 天涨粉，也不是保证赚钱。先准备一个 Mac、一个个人演示账号、免费录屏剪辑软件、GitHub 素材目录。

## Day 1–4：前置准备（验收：频道与选题表）

1. 打开 `templates/CHANNEL_ONEPAGE.md`，只确定一种语言、一类核心观众。首季默认中文 AI 工具实测。
2. 在 YouTube 搜索 10 个相关频道和 20 个具体问题，复制原始 URL 与核查日期到 `templates/COMPETITOR_RESEARCH.csv`。
3. 把问题扩展成 50 条，不要使用“AI 赚钱”“效率提升”这种没有可操作结果的标题。用 `scripts/score_topics.py` 做人工评分。
4. 选第一条：能在一天内使用你自己开发/维护的工具完整演示，且有实物前后比较。

## Day 5–7：第一次完整发布（验收：3 条链接）

1. 复制 `examples/EPISODE_001_EXAMPLE.md`，明确结果镜头和真实工具版本；不用固定脚本硬套新功能。
2. Mac 屏录时关闭通知、清空私人文件与标签，保证观众看得到点击行为。录一次错误排查，而不是完美配音覆盖实际操作。
3. 打开 `templates/VIDEO_SCORECARD.md`，逐项核实。任何原创性/隐私/错误信息 BLOCK 未解决不发布。
4. 完成长视频，再从其中独立剪辑两个自洽 Shorts。不能简单把整幅 16:9 画面缩小套成 9:16。
5. 开 YouTube Studio 上传长视频，填写标题、封面、字幕、章节、说明和项目链接；如果上传 Shorts，使用相关视频承接，不靠 Shorts 文本 URL。
6. 用手机打开链接和资源后再发 Threads/X，避免别人点到 404。

## Day 8–30：固定每周一次循环（验收：4 长 8 短）

- 周一：查 10 条真实评论/搜索问题；选 1 个主题。
- 周二：脚本 + 事实校验 + 3 套不同角度标题。
- 周三：原始操作和声音素材。
- 周四：长视频剪辑、字幕、封面、红队审核。
- 周五：发布；Short A 提取一个独立结果。
- 周六：Short B 讲一个独立错误排查，分发 Threads/X。
- 周日：登记 7 天或已有观察窗口的 Studio 指标和真正用户问题。没有数据明确留空。

**不可跳过的每周验收物**：长视频 URL、2 条 Short URL、GitHub 资源链接、1 份数据表、1 个下一轮假设。建议文件名 `YYMMDD_topic_{script|thumb|metrics}.ext`。

## 直接可执行命令

```bash
python3 scripts/new_episode.py --slug mac-freephoto-test --title "Mac 图片压缩免费实测"
python3 scripts/video_kit.py --input ~/Movies/screen.mov --output ./output/mac-freephoto-long.mp4 --mode long
python3 scripts/analyze_metrics.py templates/METRICS_INPUT.csv
```

视频工具只做导出画幅：Mac 录屏需要亲自完成，竖屏导出后必须再检查字与按钮是否可看。分析器需要先填写真实 CSV 行，空模板只会产生空报告。
