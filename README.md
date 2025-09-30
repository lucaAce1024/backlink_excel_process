# 外链Excel合并工具 - Web版

这是一个基于Flask的Web应用程序，用于合并从Semrush导出的两种外链Excel文件。用户可以通过网页上传两个文件，系统会自动处理并返回合并后的Excel文件。

## 功能特性

- 🌐 **网页界面** - 简洁美观的用户界面
- 📁 **文件上传** - 支持拖拽或点击上传Excel文件
- 🔧 **自动处理** - 自动提取域名、合并数据
- 📊 **智能排序** - 按域名评分降序、域名升序排列
- 🚀 **实时下载** - 处理完成后自动下载合并文件
- 📱 **响应式设计** - 支持桌面和移动设备

## 本地运行

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

**方法一：直接运行（开发模式）**
```bash
python3 app.py
```

**方法二：使用Gunicorn（生产环境）**
```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

**方法三：后台运行**
```bash
nohup python3 app.py > app.log 2>&1 &
```

**方法四：使用screen/tmux保持会话**
```bash
# 使用screen
screen -S backlink-app
python3 app.py
# 按 Ctrl+A+D 分离会话

# 使用tmux
tmux new -s backlink-app
python3 app.py
# 按 Ctrl+B+D 分离会话
```

### 3. 访问应用

打开浏览器访问: http://127.0.0.1:5000

### 4. 停止应用

**如果使用直接运行：**
- 按 `Ctrl+C` 停止服务器

**如果使用后台运行：**
```bash
ps aux | grep "python3 app.py"
kill <进程ID>
```

**如果使用screen/tmux：**
```bash
# screen
screen -r backlink-app
# 然后按 Ctrl+C

# tmux
tmux attach -t backlink-app
# 然后按 Ctrl+C
```

## 部署到Vercel

### 1. 推送到GitHub

```bash
git add .
git commit -m "Add web application for backlink merging"
git push origin main
```

### 2. 部署到Vercel

1. 登录 [Vercel](https://vercel.com)
2. 点击 "New Project"
3. 选择您的GitHub仓库
4. 由于Vercel不能自动检测Flask，需要手动配置：

**Framework Preset**: 选择 `Other`
**Build Command**: 留空
**Output Directory**: 留空
**Install Command**: `pip install -r requirements.txt`

5. 点击 "Deploy"

### 3. 环境变量配置

在Vercel项目设置中添加以下环境变量：

```bash
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
MAX_CONTENT_LENGTH=52428800  # 50MB in bytes
```

### 4. Vercel特定配置说明

由于Vercel是无服务器平台，需要注意以下几点：

- **文件处理**：临时文件存储在 `/tmp` 目录
- **内存限制**：默认函数超时时间为10秒，已配置为30秒
- **文件大小限制**：最大50MB，超过需要升级Vercel计划
- **并发处理**：支持多个用户同时上传

### 5. 故障排除

**部署后遇到问题：**
1. 检查Vercel函数日志
2. 确认所有依赖包在requirements.txt中
3. 验证环境变量配置正确
4. 检查文件大小是否超过限制

## 使用说明

### 输入文件要求

1. **backlinks.xlsx** - 包含域名评分和域名信息
   - 必须包含列：`Domain ascore`, `Domain`

2. **backlinks_refdomains.xlsx** - 包含来源标题和URL信息
   - 必须包含列：`Source title`, `Source url`

### 使用步骤

1. 打开网页应用
2. 点击"选择backlinks.xlsx文件"按钮，上传第一个文件
3. 点击"选择backlinks_refdomains.xlsx文件"按钮，上传第二个文件
4. 点击"合并文件并下载"按钮
5. 等待处理完成，自动下载合并后的文件

### 输出文件格式

合并后的文件包含以下列：

| 列名 | 说明 |
|------|------|
| Domain ascore | 域名评分 |
| Domain | 域名 |
| Source title | 来源页面标题 |
| Source url | 来源页面URL |

## 文件结构

```
web_app/
├── app.py              # Flask应用主文件
├── requirements.txt    # Python依赖包
├── vercel.json        # Vercel配置文件
├── vercel_app.py      # Vercel入口文件
├── templates/
│   └── index.html     # 主页模板
├── static/            # 静态文件目录
└── uploads/          # 临时上传目录
```

## API接口

### POST /upload

上传并合并文件

**请求参数:**
- `backlinks_file`: backlinks.xlsx文件
- `refdomains_file`: backlinks_refdomains.xlsx文件

**响应:** 
- 成功: 返回合并后的Excel文件
- 失败: 返回错误信息并重定向到首页

### POST /api/merge

API接口，返回JSON格式的合并结果

**响应示例:**
```json
{
  "success": true,
  "records_count": 15000,
  "columns": ["Domain ascore", "Domain", "Source title", "Source url"],
  "sample_data": [...]
}
```

## 技术栈

- **后端**: Flask, Pandas, OpenPyXL
- **前端**: HTML5, CSS3, JavaScript
- **部署**: Vercel, Gunicorn

## 限制说明

- 最大文件大小: 50MB
- 支持的文件格式: .xlsx, .xls
- 处理超时时间: 30秒

## 故障排除

### 常见问题

1. **文件上传失败**
   - 检查文件格式是否为.xlsx或.xls
   - 确保文件大小不超过50MB
   - 验证文件包含必需的列

2. **合并结果为空**
   - 确保两个文件包含匹配的域名
   - 检查URL格式是否正确

3. **部署问题**
   - 确保所有依赖包都在requirements.txt中
   - 检查Vercel配置文件是否正确

### 开发模式调试

```bash
export FLASK_ENV=development
python3 app.py
```

## 许可证

MIT License