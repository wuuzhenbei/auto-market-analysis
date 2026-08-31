# 部署说明

## 访问地址

**https://autocar.050311.xyz**

## 本地部署步骤

### 方法一：一键部署（推荐）

双击运行 `deploy.bat`

### 方法二：手动部署

**步骤1：启动Streamlit**
```bash
pip install -r streamlit_app/requirements.txt
streamlit run streamlit_app/app.py --server.port 8501
```

**步骤2：启动Cloudflare Tunnel**（新窗口）
```bash
cloudflared tunnel --config "C:\Users\DELL\.cloudflared\config-autocar.yml" run autocar
```

## 配置信息

| 项目 | 值 |
|------|-----|
| 隧道ID | 33fb9955-813d-4e6c-9411-36cd0f73d3ce |
| 隧道名称 | autocar |
| 域名 | autocar.050311.xyz |
| 本地端口 | 8501 |

## 管理命令

```bash
# 查看隧道列表
cloudflared tunnel list

# 查看隧道信息
cloudflared tunnel info autocar

# 删除隧道（如需要）
cloudflared tunnel delete autocar
```

## 故障排查

1. **无法访问**：检查Streamlit是否在运行
2. **502错误**：检查本地端口8501是否正常
3. **DNS问题**：等待几分钟让DNS生效
