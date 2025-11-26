# Gemini API 轮换系统使用说明

## 🚀 快速开始

### 1. 配置 API Keys

编辑 `gemini_config.json` 文件，将 `your_xxx_api_key_here` 替换为你的真实 API keys：

```json
{
  "api_keys": [
    {
      "key": "AIzaSyDxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
      "name": "Gemini-1",
      "daily_limit": 1000,
      "active": true
    },
    {
      "key": "AIzaSyDyyyyyyyyyyyyyyyyyyyyyyyyyyy",
      "name": "Gemini-2",
      "daily_limit": 1000,
      "active": true
    }
  ]
}
```

### 2. 启动系统

```bash
# 一键启动（首次使用）
python3 start_gemini_system.py

# 测试配置
python3 gemini_api_manager.py test

# 运行演示
python3 quick_gemini_demo.py
```

## 📋 主要功能

### ✨ 自动轮换
- 自动检测 API key 额度
- 额度用完自动切换到下一个
- 支持冷却时间机制
- 智能重试和错误处理

### 📊 使用监控
- 实时跟踪每个 API key 使用量
- 生成每日使用报告
- 自动清理过期数据
- 监控服务状态

### 🛠️ 灵活管理
- 启用/禁用指定 API key
- 自定义日限额
- 调整冷却时间
- 设置重试次数

## 🎯 常用命令

### API Key 管理
```bash
# 查看当前可用的 API key
python3 gemini_api_manager.py current

# 查看详细使用报告
python3 gemini_api_manager.py report

# 测试所有 API keys
python3 gemini_api_manager.py test

# 启用/禁用指定的 API key
python3 gemini_api_manager.py enable --key-name Gemini-1
python3 gemini_api_manager.py disable --key-name Gemini-2
```

### 监控和报告
```bash
# 启动监控服务（持续运行）
python3 gemini_monitor.py monitor

# 一次性检查状态
python3 gemini_monitor.py check

# 生成每日报告
python3 gemini_monitor.py report

# 清理过期数据
python3 gemini_monitor.py reset
```

### 代码使用
```python
# 快速生成文本
from gemini_wrapper import quick_generate
result = quick_generate("请写一首诗")

# 聊天会话
from gemini_wrapper import quick_chat
chat = quick_chat()
response = chat.send_message("你好")
```

## 📊 配置说明

### API Key 配置
- `key`: 你的 Gemini API key
- `name`: 便于识别的名称
- `daily_limit`: 每日请求限制（根据你的额度设置）
- `active`: 是否启用此 key

### 系统设置
- `cooldown_minutes`: 额度用完后的冷却时间（分钟）
- `retry_on_quota_exceeded`: 额度超限时是否自动重试
- `max_retries`: 最大重试次数

## 🔧 VS Code 集成

系统已自动配置 VS Code 使用动态 API key。重启 VS Code 后即可使用。

### 手动配置 VS Code
如果需要手动配置，在 VS Code 设置中添加：

```json
{
  "gemini.apiKeyCommand": "python3 /path/to/get_current_gemini_key.py",
  "gemini.model": "gemini-2.5-pro",
  "gemini.maxTokens": 8192,
  "gemini.temperature": 0.7
}
```

## 📈 监控建议

### 日常使用
1. 每日运行一次 `python3 gemini_monitor.py report` 查看使用情况
2. 定期检查 API key 状态
3. 根据使用情况调整日限额

### 长期监控
1. 启动监控服务：`python3 gemini_monitor.py monitor`
2. 系统会自动：
   - 每小时检查 API keys 状态
   - 每天 08:00 生成使用报告
   - 自动清理过期数据
   - 智能切换 API key

## 🛡️ 安全提醒

1. **不要提交 API keys 到版本控制**
2. **定期轮换 API keys**
3. **监控异常使用情况**
4. **及时禁用异常的 API key**

## 🆘 故障排除

### 常见问题

**Q: 没有可用的 API key**
A: 检查配置文件中的 API keys 是否正确，是否有额度

**Q: API key 频繁切换**
A: 可能是限额设置过低，或网络问题导致请求失败

**Q: 监控服务停止**
A: 检查日志，可能是权限问题或依赖缺失

### 调试模式
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📝 日志文件

- 使用数据：`gemini_usage.json`
- 每日报告：`gemini_daily_report_YYYY-MM-DD.txt`
- 系统日志：控制台输出

## 🚀 性能优化

1. **合理设置日限额**：根据实际使用量设置
2. **调整冷却时间**：避免频繁切换
3. **启用缓存**：减少重复请求
4. **监控网络状况**：确保稳定连接

## 🔄 更新和维护

系统会自动处理大部分维护任务：
- 清理过期数据
- 生成使用报告
- 检测 API key 状态
- 自动切换和重试

建议定期：
1. 更新 API keys
2. 检查使用情况
3. 调整配置参数
4. 备份重要数据

---

💡 **提示**: 首次使用请运行 `python3 start_gemini_system.py` 进行初始化配置！