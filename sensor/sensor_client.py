import time
import json
import sys
import paho.mqtt.client as mqtt
from typing import Optional

class MqttVehicleSender:
    def __init__(self,
                 mqtt_broker: str = "localhost",
                 mqtt_port: int = 1883,
                 mqtt_topic: str = "vehicle/passage",
                 mqtt_username: Optional[str] = None,
                 mqtt_password: Optional[str] = None,
                 client_id: str = "vehicle_sender",
                 max_reconnect_attempts: int = 3):
        """初始化MQTT车辆消息发送器（增强版）"""
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        self.max_reconnect_attempts = max_reconnect_attempts
        
        self.client = mqtt.Client(client_id)
        if mqtt_username and mqtt_password:
            self.client.username_pw_set(mqtt_username, mqtt_password)
        
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"成功连接到MQTT服务器 {self.mqtt_broker}:{self.mqtt_port}")
        else:
            print(f"连接MQTT服务器失败，错误代码: {rc}")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        if rc != 0:
            print(f"意外断开MQTT连接，错误代码: {rc}")
        else:
            print("已断开MQTT连接")

    def connect(self) -> bool:
        """带重试机制的连接方法"""
        attempt = 0
        while attempt < self.max_reconnect_attempts and not self.connected:
            attempt += 1
            try:
                print(f"第 {attempt}/{self.max_reconnect_attempts} 次连接尝试...")
                self.client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
                self.client.loop_start()
                
                # 等待连接成功
                timeout = 5
                while not self.connected and timeout > 0:
                    time.sleep(0.5)
                    timeout -= 0.5
                
                if self.connected:
                    return True
            except Exception as e:
                print(f"第 {attempt} 次连接失败: {str(e)}")
                time.sleep(1)  # 重试前等待1秒
        
        return self.connected

    def send_message(self, vehicle_id: str, sensor_id: str) -> bool:
        """增强版消息发送，包含字段校验"""
        # 字段预处理与校验
        vehicle_id = vehicle_id.strip()
        sensor_id = sensor_id.strip()
        
        if not vehicle_id:
            print("错误：vehicle_id不能为空（去除空格后）")
            return False
        if not sensor_id:
            print("错误：sensor_id不能为空（去除空格后）")
            return False
        
        if not self.connected:
            print("未连接到MQTT服务器，尝试重新连接...")
            if not self.connect():
                print("连接失败，无法发送消息")
                return False
        
        try:
            message = {
                "vehicle_id": vehicle_id,
                "sensor_id": sensor_id,
                "timestamp": time.time()
            }
            
            try:
                json_message = json.dumps(message, ensure_ascii=False)
            except json.JSONDecodeError as e:
                print(f"JSON序列化失败: {str(e)}")
                return False
            
            result = self.client.publish(
                topic=self.mqtt_topic,
                payload=json_message,
                qos=1
            )
            
            result.wait_for_publish()
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"成功发送消息到主题 {self.mqtt_topic}: {json_message}")
                return True
            else:
                print(f"发送消息失败，错误代码: {result.rc}")
                return False
                
        except Exception as e:
            print(f"发送消息时出错: {str(e)}")
            return False

    def disconnect(self) -> None:
        if self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False


def main():
    if len(sys.argv) not in [3, 5]:
        print("使用方法1: python3 sensor_client.py <vehicle_id> <sensor_id>")
        print("使用方法2: python3 sensor_client.py <vehicle_id> <sensor_id> <broker> <port>")
        print("示例: python3 sensor_client.py CAR001 SENSOR001 127.0.0.1 1883")
        sys.exit(1)
    
    vehicle_id = sys.argv[1]
    sensor_id = sys.argv[2]
    mqtt_broker = sys.argv[3] if len(sys.argv) >=4 else "127.0.0.1"
    mqtt_port = int(sys.argv[4]) if len(sys.argv)>=5 else 1883
    
    sender = MqttVehicleSender(
        mqtt_broker=mqtt_broker,
        mqtt_port=mqtt_port,
        mqtt_topic="vehicle/passage"
    )
    
    try:
        if sender.connect():
            success = sender.send_message(vehicle_id, sensor_id)
            time.sleep(0.5)
            sys.exit(0 if success else 1)
        else:
            print("无法连接到MQTT服务器，发送失败")
            sys.exit(1)
            
    except Exception as e:
        print(f"发送过程中发生错误: {str(e)}")
        sys.exit(1)
    finally:
        sender.disconnect()


if __name__ == "__main__":
    main()