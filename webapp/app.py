from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import requests
from requests.exceptions import RequestException

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# 服务器配置
LOGIN_SERVER = 'http://localhost:12344'
ADMIN_SERVER = 'http://localhost:12345'
USER_SERVER = 'http://localhost:12346'

# 通用工具函数：检查管理员权限
def is_admin():
    return session.get('role') == 'admin'

# 通用工具函数：检查用户权限
def is_user():
    return session.get('role') == 'user'

# 通用工具函数：处理请求并返回结果
def handle_request(url, method='get', params=None, json=None):
    try:
        if method.lower() == 'get':
            response = requests.get(url, params=params, timeout=5)
        else:
            response = requests.post(url, json=json, timeout=5)
        
        response.raise_for_status()  # 抛出HTTP错误状态码
        return response.json()
    except RequestException as e:
        return {'success': False, 'message': f'服务请求失败: {str(e)}'}
    except ValueError:
        return {'success': False, 'message': '无效的响应格式'}

# 登录界面
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('username')
        password = request.form.get('password')
        
        if not name or not password:
            return render_template('login.html', error='用户名和密码不能为空')
            
        result = handle_request(
            f"{LOGIN_SERVER}/verify_user_and_get_role",
            method='post',
            json={'name': name, 'password': password}
        )
        
        if result.get('success'):
            session['username'] = name
            session['role'] = result.get('role')
            if result.get('role') == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('user_dashboard'))
        else:
            return render_template('login.html', error=result.get('message', '登录失败'))
    
    # 已登录用户直接跳转
    if 'username' in session:
        if session.get('role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
            
    return render_template('login.html')

# 管理员主界面
@app.route('/admin')
def admin_dashboard():
    if not is_admin():
        return redirect(url_for('login'))
    return render_template('admin_dashboard.html')

# 用户主界面
@app.route('/user')
def user_dashboard():
    if not is_user():
        return redirect(url_for('login'))
    return render_template('user_dashboard.html')

# 管理员接口
@app.route('/admin/add_user', methods=['POST'])
def admin_add_user():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    payload = {
        'name': request.form.get('name'),
        'password': request.form.get('password'),
        'is_admin': request.form.get('is_admin', 'false') == 'true'
    }
    
    # 验证必填字段
    if not payload['name'] or not payload['password']:
        return jsonify({'success': False, 'message': '用户名和密码为必填项'})
        
    result = handle_request(
        f"{ADMIN_SERVER}/add_user",
        method='post',
        json=payload
    )
    return jsonify(result)

@app.route('/admin/change_password', methods=['POST'])
def admin_change_password():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    payload = {
        'name': request.form.get('name'),
        'password': request.form.get('password')
    }
    
    if not payload['name'] or not payload['password']:
        return jsonify({'success': False, 'message': '用户名和新密码为必填项'})
        
    result = handle_request(
        f"{ADMIN_SERVER}/change_password",
        method='post',
        json=payload
    )
    return jsonify(result)

@app.route('/admin/delete_user', methods=['POST'])
def admin_delete_user():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    name = request.form.get('name')
    if not name:
        return jsonify({'success': False, 'message': '用户名为必填项'})
        
    result = handle_request(
        f"{ADMIN_SERVER}/delete_user",
        method='post',
        json={'name': name}
    )
    return jsonify(result)

@app.route('/admin/get_user_info')
def admin_get_user_info():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    name = request.args.get('name')
    if not name:
        return jsonify({'success': False, 'message': '用户名为必填项'})
        
    result = handle_request(
        f"{ADMIN_SERVER}/get_user_info",
        params={'name': name}
    )
    return jsonify(result)

@app.route('/admin/get_users')
def admin_get_users():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    params = {
        'cursor': request.args.get('cursor', 0),
        'limit': min(int(request.args.get('limit', 20)), 100)  # 限制最大条数
    }
    
    result = handle_request(
        f"{ADMIN_SERVER}/get_users",
        params=params
    )
    return jsonify(result)

@app.route('/admin/add_or_update_sensor', methods=['POST'])
def admin_add_or_update_sensor():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    payload = {
        'sensor_id': request.form.get('sensor_id'),
        'location': request.form.get('location'),
        'description': request.form.get('description', ''),
        'is_active': request.form.get('is_active', 'true') == 'true',
        'is_gate': request.form.get('is_gate', 'false') == 'true'
    }
    
    if not payload['sensor_id'] or not payload['location']:
        return jsonify({'success': False, 'message': '传感器ID和位置为必填项'})
        
    result = handle_request(
        f"{ADMIN_SERVER}/add_or_update_sensor",
        method='post',
        json=payload
    )
    return jsonify(result)

@app.route('/admin/delete_sensor', methods=['POST'])
def admin_delete_sensor():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    sensor_id = request.form.get('sensor_id')
    if not sensor_id:
        return jsonify({'success': False, 'message': '传感器ID为必填项'})
        
    result = handle_request(
        f"{ADMIN_SERVER}/delete_sensor",
        method='post',
        json={'sensor_id': sensor_id}
    )
    return jsonify(result)

@app.route('/admin/get_sensor_info')
def admin_get_sensor_info():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    sensor_id = request.args.get('sensor_id')
    if not sensor_id:
        return jsonify({'success': False, 'message': '传感器ID为必填项'})
        
    result = handle_request(
        f"{ADMIN_SERVER}/get_sensor_info",
        params={'sensor_id': sensor_id}
    )
    return jsonify(result)

@app.route('/admin/get_sensors')
def admin_get_sensors():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    params = {
        'cursor': request.args.get('cursor', 0),
        'limit': min(int(request.args.get('limit', 20)), 100)
    }
    
    result = handle_request(
        f"{ADMIN_SERVER}/get_sensors",
        params=params
    )
    return jsonify(result)

@app.route('/admin/add_vehicle', methods=['POST'])
def admin_add_vehicle():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    payload = {
        'vehicle_id': request.form.get('vehicle_id'),
        'registered_by': request.form.get('registered_by')
    }
    
    if not payload['vehicle_id'] or not payload['registered_by']:
        return jsonify({'success': False, 'message': '车辆ID和登记人ID为必填项'})
        
    result = handle_request(
        f"{ADMIN_SERVER}/add_vehicle",
        method='post',
        json=payload
    )
    return jsonify(result)

@app.route('/admin/delete_vehicle', methods=['POST'])
def admin_delete_vehicle():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    vehicle_id = request.form.get('vehicle_id')
    if not vehicle_id:
        return jsonify({'success': False, 'message': '车辆ID为必填项'})
        
    result = handle_request(
        f"{ADMIN_SERVER}/delete_vehicle",
        method='post',
        json={'vehicle_id': vehicle_id}
    )
    return jsonify(result)

@app.route('/admin/get_vehicle_info')
def admin_get_vehicle_info():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    vehicle_id = request.args.get('vehicle_id')
    if not vehicle_id:
        return jsonify({'success': False, 'message': '车辆ID为必填项'})
        
    result = handle_request(
        f"{ADMIN_SERVER}/get_vehicle_info",
        params={'vehicle_id': vehicle_id}
    )
    return jsonify(result)

@app.route('/admin/get_vehicles')
def admin_get_vehicles():
    if not is_admin():
        return jsonify({'success': False, 'message': '权限不足'})
    
    params = {
        'cursor': request.args.get('cursor', 0),
        'limit': min(int(request.args.get('limit', 20)), 100)
    }
    
    result = handle_request(
        f"{ADMIN_SERVER}/get_vehicles",
        params=params
    )
    return jsonify(result)

# 用户接口
@app.route('/user/get_current_user_info')
def user_get_current_info():
    if not is_user():
        return jsonify({'success': False, 'message': '权限不足'})
    
    result = handle_request(
        f"{USER_SERVER}/get_current_user_info",
        params={'name': session['username']}
    )
    return jsonify(result)

@app.route('/user/change_own_password', methods=['POST'])
def user_change_own_password():
    if not is_user():
        return jsonify({'success': False, 'message': '权限不足'})
    
    data = request.get_json()
    payload = {
        'name': session['username'],
        'old_password': data.get('old_password'),
        'password': data.get('password') 
    }
    print("change_own_password", payload)
    
    if not payload['old_password'] or not payload['password']:
        return jsonify({'success': False, 'message': '旧密码和新密码为必填项'})
        
    result = handle_request(
        f"{USER_SERVER}/change_own_password",
        method='post',
        json=payload
    )
    return jsonify(result)

@app.route('/user/get_user_vehicles')
def user_get_user_vehicles():
    if not is_user():
        return jsonify({'success': False, 'message': '权限不足'})
    
    # 构建分页参数，限制最大条数为100
    params = {
        'name': session['username'],  # 从会话中获取当前用户名
        'cursor': request.args.get('cursor', 0),  # 分页游标，默认0
        'limit': min(int(request.args.get('limit', 10)), 100)  # 每页数量，默认10，最大100
    }
    
    result = handle_request(
        f"{USER_SERVER}/get_user_vehicles",
        method='get',
        params=params
    )
    return jsonify(result)

@app.route('/user/get_user_vehicle_info')
def user_get_user_vehicle_info():
    if not is_user():
        return jsonify({'success': False, 'message': '权限不足'})
    
    vehicle_id = request.args.get('vehicle_id')
    if not vehicle_id:
        return jsonify({'success': False, 'message': '车辆ID为必填项'})
        
    result = handle_request(
        f"{USER_SERVER}/get_user_vehicle_info",
        params={'name': session['username'], 'vehicle_id': vehicle_id}
    )
    return jsonify(result)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7000, debug=True)