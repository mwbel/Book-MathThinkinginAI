// Continue 配置调试脚本
// 在 VS Code 开发者控制台中运行

console.log("=== Continue 配置调试 ===");

// 检查配置文件位置
const fs = require('fs');
const path = require('path');

const userConfigPath = path.expandUserHome('~/.continue/config.json');
const projectConfigPath = path.join(vscode.workspace.rootPath || '', '.continue/config.json');

console.log("用户配置路径:", userConfigPath);
console.log("项目配置路径:", projectConfigPath);

// 检查文件是否存在
try {
    const userConfig = JSON.parse(fs.readFileSync(userConfigPath, 'utf8'));
    console.log("用户配置存在，slashCommands:", userConfig.slashCommands?.length || 0);
} catch (e) {
    console.log("用户配置不存在或格式错误:", e.message);
}

try {
    const projectConfig = JSON.parse(fs.readFileSync(projectConfigPath, 'utf8'));
    console.log("项目配置存在，slashCommands:", projectConfig.slashCommands?.length || 0);
} catch (e) {
    console.log("项目配置不存在或格式错误:", e.message);
}

console.log("=== 调试完成 ===");