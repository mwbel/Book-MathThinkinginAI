# 如何添加你的 Gemini API Keys

## 🎯 最简单的方法

### 1. 打开配置文件
在 VS Code 中，按 `Cmd+Shift+P`，然后选择 **"Open User Settings (JSON)"**，或者直接运行：
```bash
code gemini_config.json
```

### 2. 找到需要替换的内容
找到这几行：
```json
{
  "api_keys": [
    {
      "key": "your_first_api_key_here",    ← 替换这里
      "name": "Gemini-1",
      "daily_limit": 1000,
      "active": true
    },
    {
      "key": "your_second_api_key_here",   ← 替换这里
      "name": "Gemini-2",
      "daily_limit": 1000,
      "active": true
    },
    {
      "key": "your_third_api_key_here",    ← 替换这里
      "name": "Gemini-3",
      "daily_limit": 1000,
      "active": true
    }
  ]
}
```

### 3. 替换为你的真实 API Keys
例如：
```json
{
  "api_keys": [
    {
      "key": "AIzaSyDabc123def456ghi789jkl012mno345pqr",
      "name": "Gemini-1",
      "daily_limit": 1000,
      "active": true
    },
    {
      "key": "AIzaSyDstu678vwx901yz234abc567def890ghi",
      "name": "Gemini-2",
      "daily_limit": 1000,
      "active": true
    },
    {
      "key": "AIzaSyJkl234mno567pqr890stu123vwx456yz",
      "name": "Gemini-3",
      "daily_limit": 1000,
      "active": true
    }
  ]
}
```

### 4. 保存文件
按 `Cmd+S` 保存。

## ✅ 验证配置

配置完成后，运行以下命令测试：

```bash
cd "/Users/Min369/Desktop/书/书稿打磨"

# 测试所有 API keys
python3 gemini_api_manager.py test

# 查看配置状态
python3 gemini_api_manager.py report
```

## 💡 注意事项

- **API Key 格式**：通常以 `AIzaSyD` 开头，长度约 39 个字符
- **日限额**：根据你的免费额度设置，通常每个 key 每天 1000 次请求
- **只有 2-3 个 keys？**：可以只填写有的，其他的保持 `"active": false`
- **只有 1 个 key？**：也正常工作，只是没有轮换功能

## 🔄 如果你只有 2 个 API keys

可以这样配置：
```json
{
  "api_keys": [
    {
      "key": "AIzaSyD你的第一个key",
      "name": "Gemini-1",
      "daily_limit": 1000,
      "active": true
    },
    {
      "key": "AIzaSyD你的第二个key",
      "name": "Gemini-2",
      "daily_limit": 1000,
      "active": true
    },
    {
      "key": "your_third_api_key_here",
      "name": "Gemini-3",
      "daily_limit": 1000,
      "active": false    ← 禁用第三个
    }
  ]
}

```