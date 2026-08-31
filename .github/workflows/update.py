#!/usr/bin/env python3
"""
GitHub Actions 数据同步脚本
用于将网页提交的数据更新到 index.html 的 EMBEDDED_DATA 中
"""

import json
import re
import sys
import os
from datetime import datetime

def log(msg, level='INFO'):
    """打印日志"""
    print(f"[{level}] {msg}")

def load_data(file_path='data.json'):
    """加载从网页传来的数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        log(f"成功加载数据文件: {file_path}")
        return data
    except FileNotFoundError:
        log(f"数据文件不存在: {file_path}", 'ERROR')
        return None
    except json.JSONDecodeError as e:
        log(f"JSON 解析失败: {e}", 'ERROR')
        return None

def update_index_html(data, html_path='index.html'):
    """更新 index.html 中的 EMBEDDED_DATA"""
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
        log(f"成功读取 HTML 文件: {html_path}")
    except FileNotFoundError:
        log(f"HTML 文件不存在: {html_path}", 'ERROR')
        return False

    # 将数据转为格式化的 JSON 字符串
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    
    # 方法1：精确匹配 EMBEDDED_DATA = { ... };
    # 使用非贪婪匹配，匹配到第一个 }; 结束
    pattern = r'(const EMBEDDED_DATA\s*=\s*)\{[\s\S]*?\};'
    replacement = f'\\1{json_str};'
    
    new_content = re.sub(pattern, replacement, content)
    
    # 检查是否替换成功
    if new_content == content:
        log("警告: 未找到 EMBEDDED_DATA，尝试备用匹配方式", 'WARN')
        
        # 方法2：更宽松的匹配（允许换行和空格变化）
        pattern2 = r'(const EMBEDDED_DATA\s*=\s*)\{[\s\S]*?\}'
        replacement2 = f'\\1{json_str}'
        new_content = re.sub(pattern2, replacement2, content)
        
        if new_content == content:
            log("错误: 无法找到 EMBEDDED_DATA 定义", 'ERROR')
            return False

    # 写回文件
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        log(f"成功更新 HTML 文件: {html_path}")
        return True
    except Exception as e:
        log(f"写入文件失败: {e}", 'ERROR')
        return False

def validate_data(data):
    """验证数据格式是否正确"""
    required_keys = ['rules', 'cards', 'keywordLibrary', 'editableContent']
    missing_keys = [k for k in required_keys if k not in data]
    
    if missing_keys:
        log(f"数据缺少必要字段: {missing_keys}", 'WARN')
        return False
    
    # 检查卡片数据格式
    if 'cards' in data and isinstance(data['cards'], list):
        for card in data['cards']:
            if not isinstance(card, dict):
                log("警告: 卡片数据格式不正确", 'WARN')
                break
            if 'name' not in card or 'type' not in card:
                log("警告: 卡片缺少 name 或 type 字段", 'WARN')
                break
    
    log("数据验证通过")
    return True

def main():
    """主函数"""
    log("=" * 50)
    log("GitHub Actions 数据同步脚本启动")
    log(f"时间: {datetime.now().isoformat()}")
    log("=" * 50)
    
    # 加载数据
    data = load_data()
    if data is None:
        log("无法加载数据，退出", 'ERROR')
        sys.exit(1)
    
    # 验证数据
    if not validate_data(data):
        log("数据验证失败，但继续执行", 'WARN')
    
    # 更新 HTML
    success = update_index_html(data)
    
    if success:
        log("✅ 同步成功！")
        sys.exit(0)
    else:
        log("❌ 同步失败！", 'ERROR')
        sys.exit(1)

if __name__ == "__main__":
    main()
