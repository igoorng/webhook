#!/usr/bin/env python3
"""
测试自动刷新功能
"""

import requests
import time

def test_auto_refresh_default_state():
    """测试自动刷新默认开启状态"""
    
    print("🔄 测试自动刷新默认开启功能")
    print("=" * 50)
    
    # 检查服务状态
    try:
        response = requests.get("http://localhost:5000")
        print("✅ 服务正常运行")
    except Exception as e:
        print(f"❌ 服务连接失败: {e}")
        return
    
    # 登录获取session
    session = requests.Session()
    try:
        login_response = session.post("http://localhost:5000/login", data={
            "username": "admin",
            "password": "admin123"
        })
        print("✅ 登录成功")
    except Exception as e:
        print(f"❌ 登录失败: {e}")
        return
    
    # 检查Dashboard页面
    try:
        dashboard_response = session.get("http://localhost:5000/dashboard")
        
        if dashboard_response.status_code == 200:
            content = dashboard_response.text
            
            # 检查自动刷新相关的元素
            checks = [
                ("isAutoRefresh = true", "自动刷新默认状态"),
                ("⏹️ 停止刷新", "按钮初始文本"),
                ("background-color: #e74c3c", "按钮初始样式"),
                ("autoRefreshInterval = setInterval", "自动启动刷新"),
                ("auto-refresh-btn", "自动刷新按钮ID")
            ]
            
            print(f"\n🔍 检查Dashboard页面元素:")
            for element, name in checks:
                if element in content:
                    print(f"  ✅ {name}: 存在")
                else:
                    print(f"  ❌ {name}: 缺失")
            
            # 检查JavaScript变量初始化
            if "let isAutoRefresh = true" in content:
                print(f"\n✅ 自动刷新变量已正确设置为默认开启")
            else:
                print(f"\n❌ 自动刷新变量未正确设置")
            
            # 检查按钮初始状态
            if '⏹️ 停止刷新' in content:
                print(f"✅ 按钮初始文本正确（显示为停止刷新状态）")
            else:
                print(f"❌ 按钮初始文本不正确")
                
        else:
            print(f"❌ Dashboard页面访问失败: {dashboard_response.status_code}")
            
    except Exception as e:
        print(f"❌ 检查Dashboard页面时出错: {e}")
    
    print(f"\n💡 验证步骤:")
    print("1. 在浏览器中打开 http://localhost:5000")
    print("2. 使用 admin / admin123 登录")
    print("3. 观察右侧的自动刷新按钮应该显示为 '⏹️ 停止刷新'（红色背景）")
    print("4. 按钮应该已经在自动刷新状态，每5秒刷新一次")
    print("5. 点击按钮应该可以切换到 '⏱️ 自动刷新'（蓝色背景）")

def send_test_message():
    """发送测试消息验证自动刷新"""
    
    print(f"\n📤 发送测试消息验证自动刷新...")
    
    test_data = {
        "event": "auto_refresh_test",
        "message": "测试自动刷新功能",
        "timestamp": int(time.time())
    }
    
    try:
        response = requests.post(
            "http://localhost:5000/webhook",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 测试消息发送成功，ID: {result.get('id')}")
            print("📱 如果自动刷新正常工作，应该在5秒内看到新消息出现在页面上")
        else:
            print(f"❌ 测试消息发送失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 发送测试消息异常: {e}")

def main():
    """主函数"""
    print("自动刷新功能测试工具")
    print("=" * 40)
    
    # 检查服务
    try:
        response = requests.get("http://localhost:5000")
        if response.status_code not in [200, 302]:
            print("❌ Webhook服务未正常响应")
            return
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Webhook服务，请确保服务已启动")
        return
    
    test_auto_refresh_default_state()
    send_test_message()
    
    print(f"\n🎉 测试完成!")
    print(f"请在浏览器中验证自动刷新功能是否默认开启")

if __name__ == "__main__":
    main()