import threading
import time
from http_user_server import run_user_server
from http_login_server import run_login_server
from http_admin_server import run_admin_server
from mqtt_server import MqttJsonVehicleWriter

def start_http_user_server():
    """启动用户HTTP服务器"""
    print("准备启动用户服务器...")
    run_user_server()

def start_http_login_server():
    """启动登录HTTP服务器"""
    print("准备启动登录服务器...")
    run_login_server()

def start_http_admin_server():
    """启动管理员HTTP服务器"""
    print("准备启动管理员服务器...")
    run_admin_server()

def start_mqtt_server():
    """启动MQTT服务器"""
    print("准备启动MQTT服务器...")
    try:
        # 配置MQTT服务器参数
        mqtt_broker = "127.0.0.1"
        mqtt_port = 1883
        mqtt_topic = "vehicle/passage"
        
        # 创建并启动MQTT写入器
        mqtt_writer = MqttJsonVehicleWriter(
            mqtt_broker=mqtt_broker,
            mqtt_port=mqtt_port,
            mqtt_topic=mqtt_topic
            # 如需认证，添加用户名和密码参数
            # mqtt_username="your_username",
            # mqtt_password="your_password"
        )
        mqtt_writer.start()
    except Exception as e:
        print(f"MQTT服务器启动失败: {str(e)}")

if __name__ == "__main__":
    try:
        # 创建线程分别启动四个服务
        threads = [
            threading.Thread(target=start_http_user_server, daemon=True),
            threading.Thread(target=start_http_login_server, daemon=True),
            threading.Thread(target=start_http_admin_server, daemon=True),
            threading.Thread(target=start_mqtt_server, daemon=True)
        ]
        
        # 启动所有线程
        for thread in threads:
            thread.start()
            # 稍微延迟避免同时启动的资源竞争
            time.sleep(0.5)
        
        print("所有服务已启动，按Ctrl+C停止...")
        
        # 主线程保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在停止所有服务...")
        print("所有服务已停止")