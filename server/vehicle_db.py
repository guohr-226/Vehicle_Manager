import sqlite3
import hashlib
import threading
from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional

class VehicleDB:
    def __init__(self):
        self.initialized = False
        self.db_path = None
        self.lock = threading.Lock()
        self.local = threading.local()

    def initialize(self, db_path: str = "vehicle_db.db") -> bool:
        """初始化数据库，创建表并添加默认管理员"""
        with self.lock:
            if self.initialized:
                return True
            
            self.db_path = db_path
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                # 创建用户表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    name TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')

                # 创建传感器表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS sensors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    sensor_id TEXT NOT NULL UNIQUE,
                    location TEXT NOT NULL UNIQUE,
                    description TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    is_gate BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')

                # 创建车辆表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS vehicles (
                    vehicle_id TEXT PRIMARY KEY NOT NULL,
                    is_on_campus BOOLEAN DEFAULT 0,
                    registered_by INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (registered_by) REFERENCES users(id)
                )
                ''')

                # 创建通行记录表
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS passage_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    vehicle_id TEXT NOT NULL,
                    sensor_id INTEGER NOT NULL,
                    passage_time TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
                    FOREIGN KEY (sensor_id) REFERENCES sensors(id)
                )
                ''')

                # 添加默认管理员
                cursor.execute("SELECT id FROM users WHERE name = 'root'")
                if not cursor.fetchone():
                    hashed_pwd = self._hash_password("123456")
                    cursor.execute(
                        "INSERT INTO users (name, password, is_admin) VALUES (?, ?, ?)",
                        ("root", hashed_pwd, True)
                    )

                conn.commit()
                self.initialized = True
                return True
            except Exception as e:
                print(f"初始化数据库失败: {e}")
                return False
            finally:
                if 'conn' in locals():
                    conn.close()
    
    def initialize_test_data(self) -> bool:
        """添加测试数据，返回是否成功"""
        def operation():
            # 添加测试用户
            success, msg = self.add_user("test_user", "test123", False)
            if not success:
                print(f"添加测试用户失败: {msg}")
                return False

            # 添加测试传感器
            success, msg = self.add_sensor("sensor_001", "东门", "入口主传感器", True, True)
            if not success:
                print(f"添加传感器1失败: {msg}")
                return False
                
            success, msg = self.add_sensor("sensor_002", "西门", "出口主传感器", True, True)
            if not success:
                print(f"添加传感器2失败: {msg}")
                return False
                
            success, msg = self.add_sensor("sensor_003", "停车场A区", "停车区传感器", True, False)
            if not success:
                print(f"添加传感器3失败: {msg}")
                return False

            # 获取测试用户ID
            valid, user_id, _ = self.verify_user("test_user", "test123")
            if not valid or user_id == -1:
                print("验证测试用户失败，无法获取用户ID")
                return False

            # 添加测试车辆
            success, msg = self.add_vehicle("ABC123", user_id)
            if not success:
                print(f"添加车辆ABC123失败: {msg}")
                return False
                
            success, msg = self.add_vehicle("XYZ789", user_id)
            if not success:
                print(f"添加车辆XYZ789失败: {msg}")
                return False

            # 获取传感器ID
            cursor = self._get_thread_cursor()
            cursor.execute("SELECT id FROM sensors WHERE sensor_id = 'sensor_001'")
            sensor1 = cursor.fetchone()
            if not sensor1:
                print("未找到sensor_001的ID")
                return False
                
            cursor.execute("SELECT id FROM sensors WHERE sensor_id = 'sensor_002'")
            sensor2 = cursor.fetchone()
            if not sensor2:
                print("未找到sensor_002的ID")
                return False

            # 添加测试通行记录
            success, msg = self.add_passage_record("ABC123", sensor1['id'])
            if not success:
                print(f"添加ABC123通过sensor_001的记录失败: {msg}")
                return False
                
            success, msg = self.add_passage_record("ABC123", sensor2['id'])
            if not success:
                print(f"添加ABC123通过sensor_002的记录失败: {msg}")
                return False
                
            success, msg = self.add_passage_record("XYZ789", sensor1['id'])
            if not success:
                print(f"添加XYZ789通过sensor_001的记录失败: {msg}")
                return False

            return True  # 所有步骤成功

        try:
            return self._retry_operation(operation)
        except Exception as e:
            print(f"测试数据插入过程发生异常: {e}")
            return False

    def _get_thread_connection(self) -> sqlite3.Connection:
        """获取线程专属数据库连接"""
        if not hasattr(self.local, 'conn'):
            if not self.initialized:
                raise RuntimeError("数据库未初始化，请先调用initialize方法")
            self.local.conn = sqlite3.connect(self.db_path)
            self.local.conn.row_factory = sqlite3.Row
        return self.local.conn

    def _get_thread_cursor(self) -> sqlite3.Cursor:
        """获取线程专属游标"""
        return self._get_thread_connection().cursor()

    def close_thread_resources(self) -> None:
        """关闭当前线程的数据库连接"""
        if hasattr(self.local, 'conn'):
            self.local.conn.close()
            del self.local.conn

    def close(self) -> None:
        """标记数据库为未初始化状态"""
        with self.lock:
            self.initialized = False

    def _retry_operation(self, operation, max_retries: int = 3, delay: float = 0.1) -> Any:
        """带重试机制的数据库操作"""
        for i in range(max_retries):
            try:
                return operation()
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and i < max_retries - 1:
                    import time
                    time.sleep(delay * (i + 1))
                    continue
                raise
            except Exception as e:
                raise

    def _hash_password(self, password: str) -> str:
        """密码哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()

    # 用户管理函数
    def add_user(self, name: str, password: str, is_admin: bool = False) -> Tuple[bool, str]:
        """添加新用户"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("SELECT id FROM users WHERE name = ?", (name,))
                if cursor.fetchone():
                    return (False, "用户名已存在")
                
                hashed_pwd = self._hash_password(password)
                cursor.execute(
                    "INSERT INTO users (name, password, is_admin) VALUES (?, ?, ?)",
                    (name, hashed_pwd, is_admin)
                )
                self._get_thread_connection().commit()
                return (True, "用户添加成功")
            except Exception as e:
                return (False, f"添加失败: {str(e)}")

        return self._retry_operation(operation)

    def verify_user(self, name: str, password: str) -> Tuple[bool, int, bool]:
        """验证用户密码"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("SELECT id, password, is_admin FROM users WHERE name = ?", (name,))
                user = cursor.fetchone()
                if not user:
                    return (False, -1, False)
                
                hashed_pwd = self._hash_password(password)
                if hashed_pwd == user['password']:
                    return (True, user['id'], user['is_admin'])
                return (False, -1, False)
            except Exception as e:
                return (False, -1, False)

        return self._retry_operation(operation)

    def change_password(self, name: str, old_password: Optional[str], new_password: str) -> Tuple[bool, str]:
        """修改用户密码"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("SELECT id, password, is_admin FROM users WHERE name = ?", (name,))
                user = cursor.fetchone()
                if not user:
                    return (False, "用户不存在")

                # 检查是否为管理员操作（旧密码可为空）
                if old_password is not None:
                    hashed_old = self._hash_password(old_password)
                    if hashed_old != user['password']:
                        return (False, "旧密码不正确")

                hashed_new = self._hash_password(new_password)
                cursor.execute(
                    "UPDATE users SET password = ?, updated_at = CURRENT_TIMESTAMP WHERE name = ?",
                    (hashed_new, name)
                )
                self._get_thread_connection().commit()
                return (True, "密码修改成功")
            except Exception as e:
                return (False, f"修改失败: {str(e)}")

        return self._retry_operation(operation)

    def delete_user(self, name: str, password: Optional[str]) -> Tuple[bool, str]:
        """删除用户"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("SELECT id, password, is_admin FROM users WHERE name = ?", (name,))
                user = cursor.fetchone()
                if not user:
                    return (False, "用户不存在")

                # 检查权限
                if password is not None:
                    hashed_pwd = self._hash_password(password)
                    if hashed_pwd != user['password']:
                        return (False, "密码不正确，无法删除")

                # 删除用户及关联数据
                cursor.execute("DELETE FROM vehicles WHERE registered_by = ?", (user['id'],))
                cursor.execute("DELETE FROM users WHERE id = ?", (user['id'],))
                self._get_thread_connection().commit()
                return (True, "用户删除成功")
            except Exception as e:
                return (False, f"删除失败: {str(e)}")

        return self._retry_operation(operation)

    # 传感器管理函数
    def add_sensor(self, sensor_id: str, location: str, description: str = "", 
                  is_active: bool = True, is_gate: bool = False) -> Tuple[bool, str]:
        """添加传感器"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("SELECT id FROM sensors WHERE sensor_id = ?", (sensor_id,))
                if cursor.fetchone():
                    return (False, "传感器ID已存在")
                
                cursor.execute("SELECT id FROM sensors WHERE location = ?", (location,))
                if cursor.fetchone():
                    return (False, "位置已被占用")
                
                cursor.execute(
                    """INSERT INTO sensors (sensor_id, location, description, is_active, is_gate) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (sensor_id, location, description, is_active, is_gate)
                )
                self._get_thread_connection().commit()
                return (True, "传感器添加成功")
            except Exception as e:
                return (False, f"添加失败: {str(e)}")

        return self._retry_operation(operation)

    def delete_sensor(self, sensor_id: str) -> Tuple[bool, str]:
        """删除传感器"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("SELECT id FROM sensors WHERE sensor_id = ?", (sensor_id,))
                sensor = cursor.fetchone()
                if not sensor:
                    return (False, "传感器不存在")
                
                # 删除关联的通行记录
                cursor.execute("DELETE FROM passage_records WHERE sensor_id = ?", (sensor['id'],))
                # 删除传感器
                cursor.execute("DELETE FROM sensors WHERE id = ?", (sensor['id'],))
                self._get_thread_connection().commit()
                return (True, "传感器删除成功")
            except Exception as e:
                return (False, f"删除失败: {str(e)}")

        return self._retry_operation(operation)

    # 车辆管理函数
    def add_vehicle(self, vehicle_id: str, registered_by: int, is_on_campus: bool = False) -> Tuple[bool, str]:
        """添加车辆"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("SELECT vehicle_id FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
                if cursor.fetchone():
                    return (False, "车辆已注册")
                
                cursor.execute("SELECT id FROM users WHERE id = ?", (registered_by,))
                if not cursor.fetchone():
                    return (False, "注册人不存在")
                
                cursor.execute(
                    """INSERT INTO vehicles (vehicle_id, is_on_campus, registered_by) 
                       VALUES (?, ?, ?)""",
                    (vehicle_id, is_on_campus, registered_by)
                )
                self._get_thread_connection().commit()
                return (True, "车辆注册成功")
            except Exception as e:
                return (False, f"注册失败: {str(e)}")

        return self._retry_operation(operation)

    def delete_vehicle(self, vehicle_id: str) -> Tuple[bool, str]:
        """删除车辆"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("SELECT vehicle_id FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
                if not cursor.fetchone():
                    return (False, "车辆不存在")
                
                # 删除关联的通行记录
                cursor.execute("DELETE FROM passage_records WHERE vehicle_id = ?", (vehicle_id,))
                # 删除车辆
                cursor.execute("DELETE FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
                self._get_thread_connection().commit()
                return (True, "车辆删除成功")
            except Exception as e:
                return (False, f"删除失败: {str(e)}")

        return self._retry_operation(operation)

    # 通行记录管理函数
    def add_passage_record(self, vehicle_id: str, sensor_id: int) -> Tuple[bool, str]:
        """添加通行记录并根据校门传感器状态反转车辆在校状态"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                # 检查车辆是否存在
                cursor.execute("SELECT vehicle_id, is_on_campus FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
                vehicle = cursor.fetchone()
                if not vehicle:
                    return (False, "车辆不存在")
                
                # 检查传感器是否存在并获取是否为校门传感器
                cursor.execute("SELECT id, is_gate FROM sensors WHERE id = ?", (sensor_id,))
                sensor = cursor.fetchone()
                if not sensor:
                    return (False, "传感器不存在")
                
                # 添加通行记录
                passage_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute(
                    """INSERT INTO passage_records (vehicle_id, sensor_id, passage_time) 
                       VALUES (?, ?, ?)""",
                    (vehicle_id, sensor_id, passage_time)
                )
                
                # 如果是校门传感器，反转车辆在校状态
                is_on_campus = vehicle['is_on_campus']
                if sensor['is_gate']:
                    is_on_campus = not is_on_campus
                
                # 更新车辆状态
                cursor.execute(
                    """UPDATE vehicles SET is_on_campus = ?, updated_at = CURRENT_TIMESTAMP 
                       WHERE vehicle_id = ?""",
                    (is_on_campus, vehicle_id)
                )
                
                self._get_thread_connection().commit()
                return (True, "通行记录添加成功")
            except Exception as e:
                return (False, f"添加失败: {str(e)}")

        return self._retry_operation(operation)

    # 列表查询函数
    def get_users(self, limit: int = 20, offset: int = 0) -> Tuple[bool, Any, int]:
        """分页查询用户列表"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                # 查询总数
                cursor.execute("SELECT COUNT(*) as total FROM users")
                total = cursor.fetchone()['total']
                
                # 查询用户列表
                cursor.execute("""
                    SELECT id, name, is_admin, created_at 
                    FROM users 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                users = []
                for row in cursor.fetchall():
                    users.append({
                        'id': row['id'],
                        'name': row['name'],
                        'is_admin': row['is_admin'],
                        'created_at': row['created_at']
                    })
                
                return (True, users, total)
            except Exception as e:
                return (False, f"查询失败: {str(e)}", 0)

        return self._retry_operation(operation)

    def get_vehicles(self, limit: int = 20, offset: int = 0) -> Tuple[bool, Any, int]:
        """分页查询车辆列表"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                # 查询总数
                cursor.execute("SELECT COUNT(*) as total FROM vehicles")
                total = cursor.fetchone()['total']
                
                # 查询车辆列表（关联用户信息）
                cursor.execute("""
                    SELECT v.vehicle_id, v.is_on_campus, v.created_at, u.name as registered_by_name
                    FROM vehicles v
                    LEFT JOIN users u ON v.registered_by = u.id
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                vehicles = []
                for row in cursor.fetchall():
                    vehicles.append({
                        'vehicle_id': row['vehicle_id'],
                        'is_on_campus': row['is_on_campus'],
                        'registered_by_name': row['registered_by_name'],
                        'created_at': row['created_at']
                    })
                
                return (True, vehicles, total)
            except Exception as e:
                return (False, f"查询失败: {str(e)}", 0)

        return self._retry_operation(operation)

    def get_sensors(self, limit: int = 20, offset: int = 0) -> Tuple[bool, Any, int]:
        """分页查询传感器列表"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                # 查询总数
                cursor.execute("SELECT COUNT(*) as total FROM sensors")
                total = cursor.fetchone()['total']
                
                # 查询传感器列表
                cursor.execute("""
                    SELECT id, sensor_id, location, description, is_active, is_gate, created_at
                    FROM sensors
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                sensors = []
                for row in cursor.fetchall():
                    sensors.append({
                        'id': row['id'],
                        'sensor_id': row['sensor_id'],
                        'location': row['location'],
                        'description': row['description'],
                        'is_active': row['is_active'],
                        'is_gate': row['is_gate'],
                        'created_at': row['created_at']
                    })
                
                return (True, sensors, total)
            except Exception as e:
                return (False, f"查询失败: {str(e)}", 0)

        return self._retry_operation(operation)

    # 补充：车辆状态查询
    def get_vehicle_status(self, vehicle_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """查询单个车辆的详细状态"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("""
                    SELECT v.vehicle_id, v.is_on_campus, v.created_at, v.updated_at,
                           u.name as registered_by_name
                    FROM vehicles v
                    LEFT JOIN users u ON v.registered_by = u.id
                    WHERE v.vehicle_id = ?
                """, (vehicle_id,))
                row = cursor.fetchone()
                if not row:
                    return (False, None)
                
                return (True, {
                    'vehicle_id': row['vehicle_id'],
                    'is_on_campus': row['is_on_campus'],
                    'registered_by_name': row['registered_by_name'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            except Exception as e:
                return (False, f"查询失败: {str(e)}")

        return self._retry_operation(operation)

    # 补充：传感器状态查询
    def get_sensor_status(self, sensor_id: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """查询单个传感器的详细状态"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("""
                    SELECT id, sensor_id, location, description, is_active, is_gate, created_at, updated_at
                    FROM sensors
                    WHERE sensor_id = ?
                """, (sensor_id,))
                row = cursor.fetchone()
                if not row:
                    return (False, None)
                
                return (True, {
                    'id': row['id'],
                    'sensor_id': row['sensor_id'],
                    'location': row['location'],
                    'description': row['description'],
                    'is_active': row['is_active'],
                    'is_gate': row['is_gate'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at']
                })
            except Exception as e:
                return (False, f"查询失败: {str(e)}")

        return self._retry_operation(operation)

    # 补充：通行记录查询（按车辆）
    def get_passage_by_vehicle(self, vehicle_id: str, limit: int = 20, offset: int = 0) -> Tuple[bool, Any, int]:
        """查询指定车辆的通行记录"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                # 检查车辆是否存在
                cursor.execute("SELECT vehicle_id FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
                if not cursor.fetchone():
                    return (False, "车辆不存在", 0)
                
                # 查询总数
                cursor.execute("""
                    SELECT COUNT(*) as total 
                    FROM passage_records 
                    WHERE vehicle_id = ?
                """, (vehicle_id,))
                total = cursor.fetchone()['total']
                
                # 查询通行记录
                cursor.execute("""
                    SELECT pr.id, pr.vehicle_id, pr.sensor_id, s.location, pr.passage_time, pr.created_at
                    FROM passage_records pr
                    LEFT JOIN sensors s ON pr.sensor_id = s.id
                    WHERE pr.vehicle_id = ?
                    ORDER BY pr.passage_time DESC
                    LIMIT ? OFFSET ?
                """, (vehicle_id, limit, offset))
                
                records = []
                for row in cursor.fetchall():
                    records.append({
                        'id': row['id'],
                        'vehicle_id': row['vehicle_id'],
                        'sensor_id': row['sensor_id'],
                        'location': row['location'],
                        'passage_time': row['passage_time'],
                        'created_at': row['created_at']
                    })
                
                return (True, records, total)
            except Exception as e:
                return (False, f"查询失败: {str(e)}", 0)

        return self._retry_operation(operation)

    # 补充：通行记录查询（按传感器）
    def get_passage_by_sensor(self, sensor_id: int, limit: int = 20, offset: int = 0) -> Tuple[bool, Any, int]:
        """查询指定传感器的通行记录"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                # 检查传感器是否存在
                cursor.execute("SELECT id FROM sensors WHERE id = ?", (sensor_id,))
                if not cursor.fetchone():
                    return (False, "传感器不存在", 0)
                
                # 查询总数
                cursor.execute("""
                    SELECT COUNT(*) as total 
                    FROM passage_records 
                    WHERE sensor_id = ?
                """, (sensor_id,))
                total = cursor.fetchone()['total']
                
                # 查询通行记录
                cursor.execute("""
                    SELECT pr.id, pr.vehicle_id, pr.sensor_id, s.location, pr.passage_time, pr.created_at
                    FROM passage_records pr
                    LEFT JOIN sensors s ON pr.sensor_id = s.id
                    WHERE pr.sensor_id = ?
                    ORDER BY pr.passage_time DESC
                    LIMIT ? OFFSET ?
                """, (sensor_id, limit, offset))
                
                records = []
                for row in cursor.fetchall():
                    records.append({
                        'id': row['id'],
                        'vehicle_id': row['vehicle_id'],
                        'sensor_id': row['sensor_id'],
                        'location': row['location'],
                        'passage_time': row['passage_time'],
                        'created_at': row['created_at']
                    })
                
                return (True, records, total)
            except Exception as e:
                return (False, f"查询失败: {str(e)}", 0)

        return self._retry_operation(operation)

    # 补充：更新传感器状态
    def update_sensor_status(self, sensor_id: str, is_active: bool) -> Tuple[bool, str]:
        """更新传感器激活状态"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("SELECT id FROM sensors WHERE sensor_id = ?", (sensor_id,))
                sensor = cursor.fetchone()
                if not sensor:
                    return (False, "传感器不存在")
                
                cursor.execute(
                    """UPDATE sensors SET is_active = ?, updated_at = CURRENT_TIMESTAMP 
                       WHERE id = ?""",
                    (is_active, sensor['id'])
                )
                self._get_thread_connection().commit()
                return (True, "传感器状态更新成功")
            except Exception as e:
                return (False, f"更新失败: {str(e)}")

        return self._retry_operation(operation)

    # 补充：批量删除通行记录（按时间）
    def delete_passage_records_by_time(self, start_time: str, end_time: str) -> Tuple[bool, str]:
        """删除指定时间范围内的通行记录"""
        def operation():
            cursor = self._get_thread_cursor()
            try:
                cursor.execute("""
                    DELETE FROM passage_records 
                    WHERE passage_time BETWEEN ? AND ?
                """, (start_time, end_time))
                affected = cursor.rowcount
                self._get_thread_connection().commit()
                return (True, f"成功删除 {affected} 条记录")
            except Exception as e:
                return (False, f"删除失败: {str(e)}")

        return self._retry_operation(operation)

if __name__ == "__main__": 
    """初始化数据库并插入测试数据"""
    # 创建数据库实例
    db = VehicleDB()
    
    # 初始化数据库（使用默认路径或指定路径）
    db_path = "vehicle_db.db"
    if db.initialize(db_path):
        print(f"数据库初始化成功，路径：{db_path}")
    else:
        print("数据库初始化失败")
        exit(1)  # 初始化失败则退出
    
    # 插入测试数据
    if db.initialize_test_data():
        print("测试数据插入成功")
    else:
        print("测试数据插入失败")
    
    # 关闭线程资源
    db.close_thread_resources()