### 1. 用户表（users）
| 字段名        | 数据类型         | 主键/外键 | 约束规则                | 字段含义                  | 默认值                  |
|---------------|------------------|-----------|-------------------------|---------------------------|-------------------------|
| id            | INTEGER          | 主键（PK）| AUTOINCREMENT、非空     | 用户唯一标识（自增ID）    | 自动递增                |
| name          | TEXT             | -         | NOT NULL                | 用户名（人名）            | -                       |
| password      | TEXT             | -         | NOT NULL                | 用户密码（建议实际场景加密存储） | -                       |
|is_admin       | BOOLEAN          | -         | NOT NULL                | 管理员标识               | FALSE                         |
| created_at    | TIMESTAMP        | -         | -                       | 记录创建时间              | CURRENT_TIMESTAMP（当前时间） |
| updated_at    | TIMESTAMP        | -         | -                       | 记录最后更新时间          | CURRENT_TIMESTAMP（当前时间） |


### 2. 传感器表（sensors）
| 字段名        | 数据类型         | 主键/外键 | 约束规则                | 字段含义                  | 默认值                  |
|---------------|------------------|-----------|-------------------------|---------------------------|-------------------------|
| id            | INTEGER          | 主键（PK）| AUTOINCREMENT、非空     | 传感器表自增ID（关联用）  | 自动递增                |
| sensor_id     | TEXT             | -         | UNIQUE、NOT NULL        | 传感器自身唯一标识（如硬件ID） | -                       |
| location      | TEXT             | -         | UNIQUE、NOT NULL        | 传感器安装位置            | -                       |
| description   | TEXT             | -         | -                       | 传感器功能描述（可选）    | -                       |
| is_active     | BOOLEAN          | -         | -                       | 传感器是否激活（0=未激活，1=激活） | 1（默认激活）           |
| is_gate       | BOOLEAN          | -         | -                       | 传感器是否位于校门（0=否，1=是） | 0（默认非校门）         |
| created_at    | TIMESTAMP        | -         | -                       | 记录创建时间              | CURRENT_TIMESTAMP（当前时间） |
| updated_at    | TIMESTAMP        | -         | -                       | 记录最后更新时间          | CURRENT_TIMESTAMP（当前时间） |


### 3. 车辆表（vehicles）
| 字段名        | 数据类型         | 主键/外键 | 约束规则                | 字段含义                  | 默认值                  |
|---------------|------------------|-----------|-------------------------|---------------------------|-------------------------|
| vehicle_id    | TEXT             | 主键（PK）| NOT NULL                | 车辆唯一标识（如车牌、设备ID） | -                       |
| is_on_campus  | BOOLEAN          | -         | -                       | 车辆是否在校内（0=校外，1=校内） | 0（默认校外）           |
| registered_by | INTEGER          | 外键（FK）| -                       | 车辆登记人（关联用户表ID） | -                       |
| created_at    | TIMESTAMP        | -         | -                       | 记录创建时间（车辆登记时间） | CURRENT_TIMESTAMP（当前时间） |
| updated_at    | TIMESTAMP        | -         | -                       | 记录最后更新时间（如校内状态变更） | CURRENT_TIMESTAMP（当前时间） |
| **关联说明**  | -                | -         | FOREIGN KEY (registered_by) REFERENCES users(id) | 确保登记人必须是用户表中存在的用户 | -                       |


### 4. 车辆通行记录表（passage_records）
| 字段名        | 数据类型         | 主键/外键 | 约束规则                | 字段含义                  | 默认值                  |
|---------------|------------------|-----------|-------------------------|---------------------------|-------------------------|
| id            | INTEGER          | 主键（PK）| AUTOINCREMENT、非空     | 通行记录唯一标识（自增ID） | 自动递增                |
| vehicle_id    | TEXT             | 外键（FK）| NOT NULL                | 通行车辆标识（关联车辆表） | -                       |
| sensor_id     | INTEGER          | 外键（FK）| NOT NULL                | 触发通行的传感器ID（关联传感器表自增ID） | -                       |
| passage_time  | TIMESTAMP        | -         | NOT NULL                | 车辆经过传感器的时间      | -                       |
| created_at    | TIMESTAMP        | -         | -                       | 记录创建时间（与passage_time一致或接近） | CURRENT_TIMESTAMP（当前时间） |
| **关联说明**  | -                | -         | 1. FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)<br>2. FOREIGN KEY (sensor_id) REFERENCES sensors(id) | 1. 确保通行车辆是车辆表中存在的车辆<br>2. 确保触发传感器是传感器表中存在的传感器 | -                       |


### 表间关联关系总结
1. **用户表 ↔ 车辆表**：通过 `vehicles.registered_by` 关联 `users.id`，表示“某用户登记了某车辆”。  
2. **传感器表 ↔ 通行记录表**：通过 `passage_records.sensor_id` 关联 `sensors.id`，表示“某传感器触发了某条通行记录”。  
3. **车辆表 ↔ 通行记录表**：通过 `passage_records.vehicle_id` 关联 `vehicles.vehicle_id`，表示“某车辆产生了某条通行记录”。

默认管理员name:root password:123456
需要支持多线程读写

### 支持函数

| **功能模块**       | **函数名**               | **参数说明**                                                                 | **返回值**                                                                 | **功能描述**                                                                 |
|--------------------|--------------------------|------------------------------------------------------------------------------|----------------------------------------------------------------------------|------------------------------------------------------------------------------|
| **初始化与资源管理** | `__init__`               | 无                                                                           | 无                                                                         | 初始化线程本地存储、数据库锁，设置初始状态（未初始化）                        |
|                    | `initialize`             | `db_path`：数据库文件路径（默认`vehicle_db.db`）                             | `bool`：初始化是否成功                                                     | 创建数据库表（用户、传感器、车辆、通行记录），添加默认管理员用户`root`       |
|                    | `_get_thread_connection` | 无                                                                           | 线程专属的数据库连接对象                                                   | 为当前线程创建或获取数据库连接（线程安全）                                   |
|                    | `_get_thread_cursor`     | 无                                                                           | 线程专属的数据库游标对象                                                   | 获取当前线程连接的游标                                                       |
|                    | `close_thread_resources` | 无                                                                           | 无                                                                         | 关闭当前线程的数据库连接                                                     |
|                    | `close`                  | 无                                                                           | 无                                                                         | 标记数据库为未初始化，用于程序退出时清理资源                                 |
|                    | `_retry_operation`       | `operation`：待执行的数据库操作函数；`max_retries`：最大重试次数；`delay`：重试延迟 | 操作函数的返回结果                                                         | 带重试机制的数据库操作，处理临时锁定问题（如`database locked`错误）           |
| **用户管理**       | `add_user`               | `name`：用户名；`password`：密码；`is_admin`：是否为管理员（默认`False`）     | `(bool, str)`：(操作是否成功, 结果信息)                                    | 添加新用户，检查用户名唯一性，存储密码哈希                                   |
|                    | `verify_user`            | `name`：用户名；`password`：密码                                             | `(bool, int, bool)`：(验证是否成功, 用户ID, 是否为管理员)                   | 验证用户密码是否正确，返回用户ID和管理员状态                                 |
|                    | `change_password`        | `name`：用户名；`old_password`：旧密码（管理员操作可传空）；`new_password`：新密码 | `(bool, str)`：(操作是否成功, 结果信息)                                    | 修改用户密码，支持管理员直接修改（无需旧密码）                               |
|                    | `delete_user`            | `name`：用户名；`password`：密码（管理员操作可传空）                          | `(bool, str)`：(操作是否成功, 结果信息)                                    | 删除用户及关联的车辆数据，支持管理员强制删除                                 |
| **传感器管理**     | `add_sensor`             | `sensor_id`：传感器标识；`location`：位置；`description`：描述；`is_active`：是否激活；`is_gate`：是否为大门 | `(bool, str)`：(操作是否成功, 结果信息)                                    | 添加新传感器，检查传感器标识唯一性                                           |
|                    | `delete_sensor`          | `sensor_id`：传感器标识                                                       | `(bool, str)`：(操作是否成功, 结果信息)                                    | 删除传感器及关联的通行记录                                                   |
| **车辆管理**       | `add_vehicle`            | `vehicle_id`：车辆标识；`registered_by`：注册人ID；`is_on_campus`：是否在校（默认`False`） | `(bool, str)`：(操作是否成功, 结果信息)                                    | 注册新车辆，关联注册人，检查车辆标识唯一性                                   |
|                    | `delete_vehicle`         | `vehicle_id`：车辆标识                                                       | `(bool, str)`：(操作是否成功, 结果信息)                                    | 删除车辆及关联的通行记录                                                     |
| **通行记录管理**   | `add_passage_record`     | `vehicle_id`：车辆标识；`sensor_id`：传感器ID；                                | `(bool, str)`：(操作是否成功, 结果信息)                                   | 添加车辆通行记录，自动更新车辆在校状态         |
| **列表查询（分页）** | `get_users`              | `limit`：每页数量（默认20）；`offset`：起始偏移量（默认0）                    | `(bool, list/dict, int)`：(查询是否成功, 用户列表/错误信息, 总记录数)       | 分页查询用户列表，包含ID、用户名、管理员状态、创建时间                       |
|                    | `get_vehicles`           | `limit`：每页数量（默认20）；`offset`：起始偏移量（默认0）                    | `(bool, list/dict, int)`：(查询是否成功, 车辆列表/错误信息, 总记录数)       | 分页查询车辆列表，关联注册人信息，包含在校状态、注册时间                     |
|                    | `get_sensors`            | `limit`：每页数量（默认20）；`offset`：起始偏移量（默认0）                    | `(bool, list/dict, int)`：(查询是否成功, 传感器列表/错误信息, 总记录数)     | 分页查询传感器列表，包含位置、激活状态、是否为大门等信息                     |
| **测试数据初始化** | `initialize_test_data`   | 无                                                                           | 无                                                                         | 添加测试用户、传感器、车辆和通行记录（用于功能测试）                           |

### 补充说明：
- 所有数据库操作均通过`_retry_operation`包装，确保线程安全并处理临时锁定问题。
- 密码存储采用`SHA-256`哈希算法（`_hash_password`函数），避免明文存储。
- 表设计中使用外键约束关联相关数据（如车辆关联注册人、通行记录关联车辆和传感器），并通过索引优化查询性能。