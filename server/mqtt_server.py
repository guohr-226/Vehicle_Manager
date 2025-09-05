import time
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from vehicle_db import VehicleDB  # 导入数据库操作类

class MqttJsonVehicleWriter:
    def __init__(self, 
             db_path=None,
             mqtt_broker="localhost",
             mqtt_port=1883,
             mqtt_topic="vehicle/passage",
             mqtt_username=None,
             mqtt_password=None,
             client_id="vehicle_json_db_writer"):
        """初始化MQTT JSON车辆数据写入器（无方向版）"""
        # 初始化数据库连接
        self.db = VehicleDB()
        if db_path:
            self.db.initialize(db_path)
        else:
            self.db.initialize()  # 使用默认路径
        
        # MQTT配置
        self.mqtt_broker = mqtt_broker
        self.mqtt_port = mqtt_port
        self.mqtt_topic = mqtt_topic
        
        # 创建MQTT客户端
        self.client = mqtt.Client(client_id)
        
        # 设置认证信息
        if mqtt_username and mqtt_password:
            self.client.username_pw_set(mqtt_username, mqtt_password)
        
        # 绑定回调函数
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # 状态标记
        self.connected = False

    def on_connect(self, client, userdata, flags, rc):
        """MQTT连接成功回调"""
        if rc == 0:
            self.connected = True
            print(f"成功连接到MQTT服务器 {self.mqtt_broker}:{self.mqtt_port}")
            # 订阅主题
            client.subscribe(self.mqtt_topic)
            print(f"已订阅主题: {self.mqtt_topic}")
        else:
            print(f"连接MQTT服务器失败，错误代码: {rc}")

    def on_message(self, client, userdata, msg):
        """收到MQTT消息回调"""
        try:
            # 解码消息
            payload = msg.payload.decode('utf-8').strip()
            print(f"收到消息: {payload} 来自主题: {msg.topic}")
            
            # 解析JSON格式
            try:
                data = json.loads(payload)
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {str(e)}，消息: {payload}")
                return
            
            # 验证必要字段（移除方向字段）
            required_fields = ['vehicle_id', 'sensor_id']
            if not all(field in data for field in required_fields):
                print(f"消息缺少必要字段，需要: {required_fields}，收到: {list(data.keys())}")
                return
            
            vehicle_id = data['vehicle_id'].strip()
            sensor_id_str = data['sensor_id'].strip()
            
            # 验证传感器是否存在
            sensor_id = self.get_sensor_id_by_sensor_id(sensor_id_str)
            if sensor_id is None:
                print(f"警告: 传感器ID {sensor_id_str} 不存在，忽略该消息")
                return
            
            # 验证传感器是否激活
            if not self.is_sensor_active(sensor_id_str):
                print(f"警告: 传感器ID {sensor_id_str} 未激活，忽略该消息")
                return
            
            # 验证车辆是否存在
            if not self.check_vehicle_exists(vehicle_id):
                print(f"警告: 车辆ID {vehicle_id} 不存在，忽略该消息")
                return
            
            # 添加通行记录
            success, message = self.db.add_passage_record(vehicle_id, sensor_id)
            
            if success:
                print(f"成功添加通行记录: {message}")
            else:
                print(f"添加通行记录失败: {message}")
                
        except Exception as e:
            print(f"处理消息时出错: {str(e)}")

    def on_disconnect(self, client, userdata, rc):
        """MQTT断开连接回调"""
        self.connected = False
        if rc != 0:
            print(f"意外断开MQTT连接，错误代码: {rc}")
        else:
            print("已断开MQTT连接")
        # 关闭线程数据库资源
        self.db.close_thread_resources()

    def get_sensor_id_by_sensor_id(self, sensor_id_str: str) -> int:
        """通过传感器ID字符串获取数据库中的传感器ID"""
        try:
            # 获取传感器详情
            success, sensor_data = self.db.get_sensor_status(sensor_id_str)
            if success and sensor_data:
                return sensor_data['id']
            return None
        except Exception as e:
            print(f"查询传感器ID时出错: {str(e)}")
            return None

    def is_sensor_active(self, sensor_id_str: str) -> bool:
        """检查传感器是否处于激活状态"""
        try:
            success, sensor_data = self.db.get_sensor_status(sensor_id_str)
            return success and sensor_data and sensor_data['is_active']
        except Exception as e:
            print(f"检查传感器状态时出错: {str(e)}")
            return False

    def check_vehicle_exists(self, vehicle_id: str) -> bool:
        """检查车辆是否存在于数据库中"""
        try:
            # 查询车辆状态
            success, vehicle_data = self.db.get_vehicle_status(vehicle_id)
            return success and vehicle_data is not None
        except Exception as e:
            print(f"检查车辆是否存在时出错: {str(e)}")
            return False

    def connect(self) -> bool:
        """连接到MQTT服务器"""
        try:
            self.client.connect(self.mqtt_broker, self.mqtt_port, keepalive=60)
            return True
        except Exception as e:
            print(f"连接MQTT服务器失败: {str(e)}")
            return False

    def start(self) -> None:
        """开始运行MQTT客户端"""
        if not self.connected:
            if not self.connect():
                return
        
        try:
            # 开始循环处理
            self.client.loop_start()
            print("MQTT客户端已启动，开始接收消息...")
            
            # 保持运行
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n用户中断，正在停止...")
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            self.db.close()

if __name__ == "__main__":
    # 配置参数
    MQTT_BROKER = "127.0.0.1"  # 替换为你的MQTT服务器地址
    MQTT_PORT = 1883
    MQTT_TOPIC = "vehicle/passage"  # 订阅的主题
    
    # 创建并启动写入器
    writer = MqttJsonVehicleWriter(
        mqtt_broker=MQTT_BROKER,
        mqtt_port=MQTT_PORT,
        mqtt_topic=MQTT_TOPIC
        # 如果需要认证，添加以下参数
        # mqtt_username="your_username",
        # mqtt_password="your_password"
    )
    
    writer.start()