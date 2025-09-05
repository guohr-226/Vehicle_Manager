import threading
import socketserver
import time
from vehicle_db import VehicleDB
# from http_user_server import UserRequestHandler
# from http_admin_server import AdminRequestHandler
# from http_logic_server import UserRoleLogic, LoginRequestHandler

class ServerThread(threading.Thread):
    """服务器线程类，封装服务器启动逻辑"""
    def __init__(self, handler_class, host="localhost", port=0, **kwargs):
        super().__init__()
        self.handler_class = handler_class  # 请求处理器类
        self.host = host
        self.port = port
        self.kwargs = kwargs  # 传递给处理器的额外参数（如 role_logic、db）
        self.server = None
        self.daemon = True
        
    def run(self):
        """启动服务器：用工厂函数传递额外参数给处理器"""
        try:
            # 工厂函数——适配 socketserver 对处理器参数的要求
            def handler_factory(request, client_address, server):
                # 向处理器构造函数传递额外参数（self.kwargs）
                return self.handler_class(request, client_address, server,** self.kwargs)
            
            # 绑定工厂函数
            self.server = socketserver.TCPServer(
                (self.host, self.port), 
                handler_factory
            )
            self.server.allow_reuse_address = True
            host, port = self.server.socket.getsockname()
            print(f"\n服务器启动成功 - 监听 {host}:{port}")
            self.server.serve_forever()
        except Exception as e:
            print(f"服务器启动失败: {str(e)}")
            
    def stop(self):
        """停止服务器"""
        if self.server:
            print(f"\n正在关闭服务器 {self.host}:{self.port}...")
            self.server.shutdown()
            self.server.server_close()
            print(f"服务器 {self.host}:{self.port} 已关闭")

# ---------------------- 接口路由打印函数 ----------------------
def print_admin_server_routes():
    print("支持的管理员接口:")
    routes = [
        "/add_user - 添加用户 (name, password)",
        "/change_password - 更改密码 (name, password)",
        "/delete_user - 删除用户 (name)",
        "/add_or_update_sensor - 添加/更改传感器 (sensor_id, location, ...)",
        "/delete_sensor - 删除传感器 (sensor_id)",
        "/add_vehicle - 添加车辆 (vehicle_id, registered_by)",
        "/delete_vehicle - 删除车辆 (vehicle_id)",
        "/get_users - 分段拉取用户列表 (cursor, limit)",
        "/get_vehicles - 分段拉取车辆列表 (cursor, limit)",
        "/get_sensors - 分段拉取传感器列表 (cursor, limit)",
        "/get_user_info - 查询用户信息 (name)",
        "/get_vehicle_info - 查询车辆信息 (vehicle_id)",
        "/get_sensor_info - 查询传感器信息 (sensor_id)"
    ]
    for route in routes:
        print(f"  {route}")

def print_user_server_routes():
    print("支持的用户接口 (所有请求必须包含name参数):")
    routes = [
        "/get_current_user_info - 查询当前用户信息",
        "/change_own_password - 修改当前用户密码（需提供old_password和password）",
        "/get_user_vehicles - 分段查询当前用户车辆列表（cursor, limit）",
        "/get_next_vehicle_info - 查询当前用户指定车辆信息及最后出现位置（vehicle_id）"
    ]
    for route in routes:
        print(f"  {route}")

def print_login_server_routes():
    print("支持的登录接口:")
    routes = [
        "/api/user/login - 用户登录 (username, password)"
    ]
    for route in routes:
        print(f"  {route}")

# ---------------------- 主函数 ----------------------
def main():
    # 初始化数据库
    try:
        print("正在初始化数据库...")
        db = VehicleDB()
        db.initialize()
        db.initialize_test_data()
        print("数据库初始化完成")
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
        return
    
    # # 创建业务逻辑实例
    # role_logic = UserRoleLogic(db)
    
    # # 启动登录服务器
    # login_server = ServerThread(
    #     handler_class=LoginRequestHandler,
    #     host="localhost",
    #     port=12344,
    #     role_logic=role_logic
    # )
    # login_server.start()
    # print_login_server_routes()
    
    # # 启动管理员服务器
    # admin_server = ServerThread(
    #     AdminRequestHandler, 
    #     "localhost", 
    #     12345, 
    #     db=db
    # )
    # admin_server.start()
    # print_admin_server_routes()
    
    # # 启动用户服务器
    # user_server = ServerThread(
    #     UserRequestHandler, 
    #     "localhost", 
    #     12346, 
    #     db=db
    # )
    # user_server.start()
    # print_user_server_routes()
    
    # time.sleep(1)
    # print("\n所有服务器已启动，按 Ctrl+C 关闭所有服务")
    
    # # 保持主线程运行
    # try:
    #     while True:
    #         threading.Event().wait(1)
    # except KeyboardInterrupt:
    #     print("\n接收到关闭信号...")
    #     admin_server.stop()
    #     user_server.stop()
    #     login_server.stop()
    #     admin_server.join()
    #     user_server.join()
    #     login_server.join()
    db.close()
    #     print("所有服务已关闭")

if __name__ == "__main__":
    main()