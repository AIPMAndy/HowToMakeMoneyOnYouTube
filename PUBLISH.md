# GitHub 发布清单（预期仓库：AIPMAndy/HowToMakeMoneyOnYouTube）

## 1. 上传

在 GitHub 页面创建 **Public** 仓库 `HowToMakeMoneyOnYouTube`。如果准备使用 GitHub CLI：

```bash
# 在项目根目录执行；需要 gh 登录且具有创建仓库权限
git init -b main
git add . && git commit -m "feat: initial faceless YouTube playbook"
gh repo create AIPMAndy/HowToMakeMoneyOnYouTube --public --source=. --remote=origin --push
```

如果仓库已存在，用 `git remote add origin ...` 后 `git push -u origin main`，不要重复创建。

## 2. 开启 Pages

- Settings → Pages → Build and deployment → Source → **GitHub Actions**。
- 触发 `pages.yml`；观察 **Actions → Deploy GitHub Pages** 任务结果。
- 完成后访问预期网址 `https://aipmandy.github.io/HowToMakeMoneyOnYouTube/`。
- 实测主页、任一章节独立 URL、搜索、勾选、导出 JSON、手机浏览；检查 sitemap/robots/llms 文件是否返回 200。

## 3. 改站点地址

若 fork、改名或使用自定义域名，需要：

```bash
SITE_URL='https://YOURNAME.github.io/REPO/' python3 scripts/build.py
```

另外手动更新 `docs/index.html` 中的 `canonical` 与 `og:image`。不要只改页面 title 而忘记 canonical。

## 4. 发布前证据

- 内容是否声称“已经部署、已经赚钱、超过 N 粉”？检查实际证明，不允许假证据。
- 核查 YouTube YPP 当期政策与 2027-02-01 新规；变更时更新来源日期。
- 确认所有视频案例使用官方频道 / 公开自述链接，商业自述已标注未独立验证。
- 跑测试；记录 commit SHA、测试结果、Pages URL、移动端截图与最后核验日期。

## 5. 后续 SEO/GEO

每章都有独立 HTML URL、可抓取正文、canonical、HowTo 结构化数据、sitemap 和 llms.txt。上述机制只帮助内容被正确发现和理解，**不承诺 Google 排名或 AI 引用**。公开原始证据，比堆积关键词更重要。
