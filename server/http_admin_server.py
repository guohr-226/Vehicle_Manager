import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from vehicle_db import VehicleDB

class AdminHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db = VehicleDB()
        # 初始化数据库
        if not self.db.initialize():
            raise RuntimeError("数据库初始化失败")
        super().__init__(*args, **kwargs)

    def _set_response(self, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()

    def _parse_post_data(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        try:
            return json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            return None

    def do_POST(self):
        path = self.path
        data = self._parse_post_data() or {}
        
        if path == '/add_user':
            name = data.get('name')
            password = data.get('password')
            is_admin = data.get('is_admin', False)
            
            if not name or not password:
                response = {"success": False, "message": "用户名和密码为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            success, message = self.db.add_user(name, password, is_admin)
            response = {"success": success, "message": message}
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/change_password':
            name = data.get('name')
            new_password = data.get('password')
            
            if not name or not new_password:
                response = {"success": False, "message": "用户名和新密码为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # 管理员接口无需旧密码
            success, message = self.db.change_password(name, None, new_password)
            response = {"success": success, "message": message}
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/delete_user':
            name = data.get('name')
            
            if not name:
                response = {"success": False, "message": "用户名为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            success, message = self.db.delete_user(name, None)
            response = {"success": success, "message": message}
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/add_or_update_sensor':
            sensor_id = data.get('sensor_id')
            location = data.get('location')
            
            if not sensor_id or not location:
                response = {"success": False, "message": "传感器ID和位置为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # 检查传感器是否存在
            exists, _ = self.db.get_sensor_status(sensor_id)
            description = data.get('description', '')
            is_active = data.get('is_active', True)
            is_gate = data.get('is_gate', False)
            
            if exists:
                # 更新传感器
                success, message = self.db.update_sensor_status(sensor_id, is_active)
                # 这里简化处理，实际应实现完整更新逻辑
            else:
                # 添加新传感器
                success, message = self.db.add_sensor(sensor_id, location, description, is_active, is_gate)
                
            response = {"success": success, "message": message}
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/delete_sensor':
            sensor_id = data.get('sensor_id')
            
            if not sensor_id:
                response = {"success": False, "message": "传感器ID为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            success, message = self.db.delete_sensor(sensor_id)
            response = {"success": success, "message": message}
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/add_vehicle':
            vehicle_id = data.get('vehicle_id')
            registered_by = data.get('registered_by')
            
            if not vehicle_id or not registered_by:
                response = {"success": False, "message": "车辆ID和登记人ID为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            success, message = self.db.add_vehicle(vehicle_id, registered_by)
            response = {"success": success, "message": message}
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/delete_vehicle':
            vehicle_id = data.get('vehicle_id')
            
            if not vehicle_id:
                response = {"success": False, "message": "车辆ID为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            success, message = self.db.delete_vehicle(vehicle_id)
            response = {"success": success, "message": message}
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"success": False, "message": "接口不存在"}).encode('utf-8'))

    def do_GET(self):
        path = self.path
        params = {}
        
        # 解析查询参数
        if '?' in path:
            path, query = path.split('?', 1)
            for param in query.split('&'):
                if '=' in param:
                    k, v = param.split('=', 1)
                    params[k] = v
        
        if path == '/get_user_info':
            name = params.get('name')
            if not name:
                response = {"success": False, "message": "用户名为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            # 从用户列表中查找指定用户
            success, users, _ = self.db.get_users(limit=1000)
            if not success:
                response = {"success": False, "message": users}
                self._set_response(500)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            user_info = next((u for u in users if u['name'] == name), None)
            if user_info:
                response = {"success": True, "data": user_info}
            else:
                response = {"success": False, "message": "用户不存在"}
                
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/get_users':
            cursor = int(params.get('cursor', 0))
            limit = min(int(params.get('limit', 20)), 100)
            
            success, users, total = self.db.get_users(limit, cursor)
            if success:
                next_cursor = cursor + limit if cursor + limit < total else None
                response = {
                    "success": True,
                    "data": users,
                    "total": total,
                    "next_cursor": next_cursor,
                    "limit": limit
                }
            else:
                response = {"success": False, "message": users}
                
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/get_sensor_info':
            sensor_id = params.get('sensor_id')
            if not sensor_id:
                response = {"success": False, "message": "传感器ID为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            success, sensor_info = self.db.get_sensor_status(sensor_id)
            if success:
                if sensor_info:
                    response = {"success": True, "data": sensor_info}
                else:
                    response = {"success": False, "message": "传感器不存在"}
            else:
                response = {"success": False, "message": sensor_info}
                
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/get_sensors':
            cursor = int(params.get('cursor', 0))
            limit = min(int(params.get('limit', 20)), 100)
            
            success, sensors, total = self.db.get_sensors(limit, cursor)
            if success:
                next_cursor = cursor + limit if cursor + limit < total else None
                response = {
                    "success": True,
                    "data": sensors,
                    "total": total,
                    "next_cursor": next_cursor,
                    "limit": limit
                }
            else:
                response = {"success": False, "message": sensors}
                
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/get_vehicle_info':
            vehicle_id = params.get('vehicle_id')
            if not vehicle_id:
                response = {"success": False, "message": "车辆ID为必填项"}
                self._set_response(400)
                self.wfile.write(json.dumps(response).encode('utf-8'))
                return
                
            success, vehicle_info = self.db.get_vehicle_status(vehicle_id)
            if success:
                if vehicle_info:
                    response = {"success": True, "data": vehicle_info}
                else:
                    response = {"success": False, "message": "车辆不存在"}
            else:
                response = {"success": False, "message": vehicle_info}
                
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/get_vehicles':
            cursor = int(params.get('cursor', 0))
            limit = min(int(params.get('limit', 20)), 100)
            
            success, vehicles, total = self.db.get_vehicles(limit, cursor)
            if success:
                next_cursor = cursor + limit if cursor + limit < total else None
                response = {
                    "success": True,
                    "data": vehicles,
                    "total": total,
                    "next_cursor": next_cursor,
                    "limit": limit
                }
            else:
                response = {"success": False, "message": vehicles}
                
            self._set_response()
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"success": False, "message": "接口不存在"}).encode('utf-8'))

def run_admin_server():
    server_address = ('', 12345)
    httpd = HTTPServer(server_address, AdminHTTPHandler)
    print('管理员服务器启动，监听端口 12345...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print('管理员服务器已关闭')

if __name__ == '__main__':
    run_admin_server()