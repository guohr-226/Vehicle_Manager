# 车辆管理系统 - 程序设计与安装说明文档

## 一、程序设计概述

### 1. 系统架构

车辆管理系统采用分层架构设计，主要包含以下组件：

- **Web应用层**：基于Flask框架的Web管理界面，提供用户登录、数据展示和管理功能
- **数据处理层**：MQTT消息接收服务，处理车辆通行记录
- **数据存储层**：SQLite数据库，存储用户、车辆、传感器和通行记录信息

各组件间通过接口和数据库进行数据交互，形成完整的车辆管理闭环。

### 2. 核心功能模块

#### 2.1 用户认证与权限管理
- 支持管理员和普通用户两种角色
- 基于会话(session)的身份验证机制
- 权限控制：管理员可进行全量操作，普通用户仅能查看自身相关车辆信息

#### 2.2 车辆管理
- 车辆注册与信息维护
- 车辆在校状态自动更新
- 车辆通行记录查询

#### 2.3 传感器管理
- 传感器信息配置（位置、描述、是否为大门等）
- 传感器激活/禁用状态管理
- 传感器关联通行记录

#### 2.4 通行记录管理
- 接收MQTT消息记录车辆通行事件
- 自动更新车辆在校状态（通过大门传感器时）
- 通行记录查询与统计

### 3. 数据库设计

系统采用SQLite数据库，主要包含以下表结构：

1. **用户表(users)**：存储用户信息，包括ID、用户名、密码(哈希存储)、管理员标识等
2. **车辆表(vehicles)**：存储车辆信息，包括车辆ID、登记人、在校状态等
3. **传感器表(sensors)**：存储传感器信息，包括传感器ID、位置、是否激活、是否为大门等
4. **通行记录表(passage_records)**：存储车辆通行记录，关联车辆和传感器信息

表间关联关系：
- 用户表 ↔ 车辆表：通过`vehicles.registered_by`关联`users.id`
- 传感器表 ↔ 通行记录表：通过`passage_records.sensor_id`关联`sensors.id`
- 车辆表 ↔ 通行记录表：通过`passage_records.vehicle_id`关联`vehicles.vehicle_id`

### 4. 接口设计

#### 4.1 Web应用接口
| 接口路径 | 请求方法 | 功能描述 | 权限要求 |
|---------|---------|---------|---------|
| `/` | GET/POST | 登录界面及处理登录请求 | 无 |
| `/admin` | GET | 管理员主界面 | 管理员 |
| `/user` | GET | 用户主界面 | 普通用户 |
| `/admin/add_user` | POST | 添加用户 | 管理员 |
| `/admin/change_password` | POST | 修改用户密码 | 管理员 |
| `/admin/delete_user` | POST | 删除用户 | 管理员 |
| `/admin/add_vehicle` | POST | 添加车辆 | 管理员 |
| `/admin/delete_vehicle` | POST | 删除车辆 | 管理员 |
| `/admin/add_or_update_sensor` | POST | 添加或更新传感器 | 管理员 |
| `/admin/delete_sensor` | POST | 删除传感器 | 管理员 |
| `/logout` | GET | 退出登录 | 已登录用户 |

#### 4.2 MQTT消息接口
- **服务器地址**：默认`localhost`
- **端口**：默认`1883`
- **订阅主题**：默认`vehicle/passage`
- **消息格式**：JSON格式，包含`vehicle_id`(车辆ID)和`sensor_id`(传感器ID)

## 二、安装说明

### 1. 环境要求

- Python 3.7及以上版本
- 依赖库：Flask、paho-mqtt、sqlite3等

### 2. 安装步骤

#### 2.1 获取源代码

```bash
# 克隆代码仓库（示例命令）
git clone https://github.com/guohr-226/Vehicle_Manager.git
cd Vehicle_Manager
```

#### 2.2 安装依赖包

```bash
# 创建并激活虚拟环境（可选）
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install flask paho-mqtt sqlite3
```

#### 2.3 启动服务器

系统启动时会自动初始化数据库，默认路径为`server/vehicle_db.db`。也可通过以下方式手动初始化测试数据：

```bash
cd server
python start_server.py
```

默认管理员账号：
- 用户名：root
- 密码：123456

#### 2.4 启动Web应用

```bash
cd webapp
export FLASK_APP=app.py  # Linux/Mac
set FLASK_APP=app.py     # Windows
flask run --host=0.0.0.0 --port=5000
```

Web应用将在`http://localhost:5000`上运行。

#### 2.5 启动MQTT服务

```bash
cd server
python mqtt_server.py
```

MQTT服务将连接到默认的MQTT broker并开始监听`vehicle/passage`主题的消息。

### 3. 配置说明

#### 3.1 Web应用配置

可在`webapp/app.py`中修改以下配置：
- 登录服务器地址
- 端口号
- 会话配置等

#### 3.2 MQTT服务配置

可在初始化`MqttJsonVehicleWriter`类时修改以下参数：
- `mqtt_broker`：MQTT服务器地址
- `mqtt_port`：MQTT端口
- `mqtt_topic`：订阅主题
- `mqtt_username`和`mqtt_password`：MQTT认证信息
- `db_path`：数据库路径

示例：
```python
# 自定义配置示例
writer = MqttJsonVehicleWriter(
    db_path="/path/to/vehicle_db.db",
    mqtt_broker="mqtt.example.com",
    mqtt_port=1883,
    mqtt_topic="custom/vehicle/passage",
    mqtt_username="user",
    mqtt_password="pass"
)
writer.start()
```

### 4. 验证安装

1. 访问`http://localhost:5000`，使用默认管理员账号登录
2. 确认管理员界面可正常访问
3. 添加测试传感器、用户和车辆
4. 发送MQTT测试消息到指定主题，验证通行记录是否被正确记录

示例MQTT测试消息：
```json
{"vehicle_id": "TEST001", "sensor_id": "GATE001"}
```

## 三、常见问题解决

1. **数据库连接失败**：检查数据库路径是否正确，文件权限是否足够
2. **MQTT连接失败**：检查MQTT服务器地址和端口是否正确，网络是否通畅
3. **登录失败**：确认使用正确的用户名和密码，默认管理员账号为root/123456
4. **权限错误**：普通用户无法访问管理员功能，需使用管理员账号登录

## 四、维护与更新

1. 定期备份数据库文件(`vehicle_db.db`)
2. 更新代码后需重启Web应用和MQTT服务
3. 重要更新前建议先备份数据
