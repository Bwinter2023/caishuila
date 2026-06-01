# 财税法资讯站

企业主和财务工作者的财税法律风险雷达。

## 本地预览

双击 `index.html` 即可在浏览器中打开查看。

## 部署到 GitHub Pages（让别人能访问）

### 前置条件

1. 注册一个 GitHub 账号：https://github.com/signup
2. 安装 Git：https://git-scm.com/downloads（已安装）

### 部署步骤

```bash
# 1. 进入站点目录
cd D:\22、open code\财税法资讯站

# 2. 初始化为 Git 仓库
git init
git add .
git commit -m "首次提交：财税法资讯站"

# 3. 在 GitHub 上创建一个新仓库
#    打开 https://github.com/new
#    仓库名填写：caishuila（或你喜欢的名字）
#    选择 Public（公开），不要勾选任何初始化选项
#    点击"Create repository"

# 4. 将本地代码推送到 GitHub（用第3步页面显示的命令）
git remote add origin https://github.com/你的用户名/caishuila.git
git branch -M main
git push -u origin main

# 5. 开启 GitHub Pages
#    打开仓库 → Settings → Pages
#    Source 选 "Deploy from a branch"
#    Branch 选 "main"，文件夹选 "/ (root)"
#    点 Save
#    等待 2 分钟，你的网站就会出现在：
#    https://你的用户名.github.io/caishuila/
```

### 绑定自定义域名（可选，如 want ai-hot style）

在 GitHub Pages 设置页面的 "Custom domain" 输入你的域名（如 `caishui.yourdomain.com`），并在域名 DNS 管理处添加 CNAME 记录指向 `你的用户名.github.io`。

### 如何发布新文章

1. 用 文中子财税写作 skill 写好文章，生成 HTML
2. 把 HTML 文件保存到 `articles/` 文件夹，以日期命名（如 `20260615.html`）
3. 编辑 `articles.js`，在 `articles` 数组末尾添加一条记录：

```javascript
{
  id: "20260615",           // 与 HTML 文件名一致（不含 .html）
  title: "文章标题",
  date: "2026-06-15",       // 格式 YYYY-MM-DD
  category: "税务",          // 税务 / 法律 / 政策 / 案例 / 实务
  tags: ["标签1", "标签2"],  // 搜索用的关键词
  summary: "文章摘要，显示在卡片上，60-120字",
  reason: "推荐理由，显示在卡片底部，40-80字"
}
```

4. 在网站目录下运行：
```bash
git add .
git commit -m "新增文章：xxx"
git push
```

5. 等待 1-2 分钟，网站自动更新。

### 注意事项

- 不要在文章中出现真实公司名、股票代码（参考 文中子财税写作 skill 的匿名化规范）
- 文章仅作学习参考，不构成税务或法律建议
- 所有 HTML 文件请用 utf-8 编码
