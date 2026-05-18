# 每日 AI 日报

自动搜集全球 AI 领域重要动态，侧重 **AI Coding** 与 **具身智能** 方向。
筛选 3-5 条最有价值的信息，每天自动更新。

数据来源：Hacker News API + GitHub Trending（全部免费，无需 API Key）

## 部署

### 1. 推到 GitHub

```bash
cd daily-stock-briefing
git init
git add .
git commit -m "init"
git remote add origin https://github.com/你的用户名/daily-ai-briefing.git
git branch -M main
git push -u origin main
```

### 2. 部署到 Vercel

1. 打开 https://vercel.com 用 GitHub 登录
2. "Add New Project" → 选择 `daily-ai-briefing`
3. 保持默认，点击 "Deploy"
4. 访问 `https://daily-ai-briefing.vercel.app`

### 3. 开启 Actions

仓库 → Actions → "每日AI日报" → "Run workflow" 手动触发一次验证

## 本地预览

```bash
npm run dev
# 访问 http://localhost:5173
```
