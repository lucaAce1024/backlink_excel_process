# Backlink Excel 合并工具

这个Python脚本用于合并从Semrush导出的两种外链Excel文件，生成包含域名评分、域名、来源标题和来源URL的合并文件。

## 文件说明

### 输入文件格式

脚本处理以下两种文件：

1. **`{SITE_DOMAIN}-backlinks.xlsx`**
   - 包含网站的反向链接域名信息
   - 关键字段：`Domain ascore`、`Domain`

2. **`{SITE_DOMAIN}-backlinks_refdomains.xlsx`**
   - 包含网站的反向链接实际URL信息
   - 关键字段：`Source title`、`Source url`

### 输出文件格式

合并后的文件格式为：`{SITE_DOMAIN}-merged.xlsx`

包含以下字段：
- **Domain ascore**: 域名评分
- **Domain**: 域名
- **Source title**: 来源页面标题
- **Source url**: 来源页面URL

## 安装要求

```bash
pip install pandas openpyxl
```

## 使用方法

### 1. 准备文件

将您的Semrush导出文件放入 `backlink_resouce` 文件夹中：

```
backlink_resouce/
├── example.com-backlinks.xlsx
├── example.com-backlinks_refdomains.xlsx
├── site2.org-backlinks.xlsx
├── site2.org-backlinks_refdomains.xlsx
└── ...
```

### 2. 运行脚本

```bash
python3 merge_backlinks.py
```

### 3. 查看结果

合并后的文件将保存在 `merged_backlinks` 文件夹中：

```
merged_backlinks/
├── example.com-merged.xlsx
├── site2.org-merged.xlsx
└── ...
```

## 功能特性

- **自动域名提取**：从完整的URL中提取域名进行匹配
- **批量处理**：自动处理文件夹中所有匹配的文件对
- **智能排序**：结果按 `Domain ascore` 降序、`Domain` 升序排列
- **错误处理**：自动跳过缺失对应文件的域名

## 示例输出

| Domain ascore | Domain | Source title | Source url |
|---------------|---------|--------------|------------|
| 59 | velog.io | 게시글 작성 | https://velog.io/@user/post |
| 55 | goldderby.com | Rivals Hulu Discussion | https://www.goldderby.com/forum/tv/rivals-hulu |
| 52 | example.com | Example Page | https://example.com/page |

## 注意事项

1. 确保 `backlink_resouce` 文件夹中包含完整的文件对
2. 脚本会自动创建 `merged_backlinks` 输出文件夹
3. 只有两个文件都存在的域名才会被处理和合并
4. URL域名提取支持各种格式（http/https、带www或不带www等）

## 自定义配置

如果需要修改输入或输出文件夹路径，可以修改脚本中的以下参数：

```python
# 默认配置
input_dir='backlink_resouce'
output_dir='merged_backlinks'
```