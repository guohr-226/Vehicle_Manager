| 接口路径 | 请求方法 | 功能描述 | 请求参数 | 权限要求 | 返回格式 |
|----------|----------|----------|----------|----------|----------|
| `/` | GET/POST | 登录界面及处理登录请求 | POST：`username`（用户名）、`password`（密码） | 无 | 登录成功跳转对应角色界面，失败返回错误信息 |
| `/admin` | GET | 管理员主界面 | 无 | 管理员 | 管理员主界面HTML |
| `/user` | GET | 用户主界面 | 无 | 普通用户 | 用户主界面HTML |
| `/admin/add_user_page` | GET | 管理员添加用户页面 | 无 | 管理员 | 添加用户页面HTML |
| `/admin/add_user` | POST | 管理员添加用户 | `name`（用户名）、`password`（密码）、`is_admin`（是否为管理员，布尔值） | 管理员 | JSON：`{'success': 布尔值, 'message': 信息}` |
| `/admin/change_paseeword_page` | GET | 管理员修改密码页面（注：路径存在拼写错误，应为`change_password_page`） | 无 | 管理员 | 修改密码页面HTML |
| `/admin/change_password` | POST | 管理员修改用户密码 | `name`（用户名）、`password`（新密码） | 管理员 | JSON：`{'success': 布尔值, 'message': 信息}` |
| `/admin/delete_user_page` | GET | 管理员删除用户页面 | 无 | 管理员 | 删除用户页面HTML |
| `/admin/delete_user` | POST | 管理员删除用户 | `name`（用户名） | 管理员 | JSON：`{'success': 布尔值, 'message': 信息}` |
| `/admin/get_user_page` | GET | 管理员获取用户信息页面 | 无 | 管理员 | 获取用户信息页面HTML |
| `/admin/get_user_info` | GET | 管理员获取指定用户信息 | `name`（用户名） | 管理员 | JSON：用户信息及`success`、`message`字段 |
| `/admin/get_users` | GET | 管理员分页获取用户列表 | `cursor`（游标，默认0）、`limit`（每页条数，默认20，最大100） | 管理员 | JSON：用户列表及分页信息、`success`、`message`字段 |
| `/admin/add_cursor_page` | GET | 管理员添加传感器页面（注：路径命名可能有误，推测为添加传感器） | 无 | 管理员 | 添加添加传感器页面HTML |
| `/admin/add_or_update_sensor` | POST | 管理员添加或更新传感器 | `sensor_id`（传感器ID）、`location`（位置）、`description`（描述，可选）、`is_active`（是否激活，默认true）、`is_gate`（是否为闸门，默认false） | 管理员 | JSON：`{'success': 布尔值, 'message': 信息}` |
| `/admin/delete_cursor_page` | GET | 管理员删除传感器页面（注：路径命名可能有误，推测为删除传感器） | 无 | 管理员 | 删除传感器页面HTML |
| `/admin/delete_sensor` | POST | 管理员删除传感器 | `sensor_id`（传感器ID） | 管理员 | JSON：`{'success': 布尔值, 'message': 信息}` |
| `/admin/get_cursor_page` | GET | 管理员获取传感器信息页面（注：路径命名可能有误，推测为获取传感器） | 无 | 管理员 | 获取传感器信息页面HTML |
| `/admin/get_sensor_info` | GET | 管理员获取指定传感器信息 | `sensor_id`（传感器ID） | 管理员 | JSON：传感器信息及`success`、`message`字段 |
| `/admin/get_sensors` | GET | 管理员分页获取传感器列表 | `cursor`（游标，默认0）、`limit`（每页条数，默认20，最大100） | 管理员 | JSON：传感器列表及分页信息、`success`、`message`字段 |
| `/admin/add_vehicle_page` | GET | 管理员添加车辆页面 | 无 | 管理员 | 添加车辆页面HTML |
| `/admin/add_vehicle` | POST | 管理员添加车辆 | `vehicle_id`（车辆ID）、`registered_by`（登记人ID） | 管理员 | JSON：`{'success': 布尔值, 'message': 信息}` |
| `/admin/delete_vehicle_page` | GET | 管理员删除车辆页面 | 无 | 管理员 | 删除车辆页面HTML |
| `/admin/delete_vehicle` | POST | 管理员删除车辆 | `vehicle_id`（车辆ID） | 管理员 | JSON：`{'success': 布尔值, 'message': 信息}` |
| `/admin/get_vehicle_page` | GET | 管理员获取车辆信息页面 | 无 | 管理员 | 获取车辆信息页面HTML |
| `/admin/get_vehicle_info` | GET | 管理员获取指定车辆信息 | `vehicle_id`（车辆ID） | 管理员 | JSON：车辆信息及`success`、`message`字段 |
| `/admin/get_vehicles` | GET | 管理员分页获取车辆列表 | `cursor`（游标，默认0）、`limit`（每页条数，默认20，最大100） | 管理员 | JSON：车辆列表及分页信息、`success`、`message`字段 |
| `/user/get_current_user_info` | GET | 用户获取自身信息 | 无（从会话获取用户名） | 普通用户 | JSON：当前用户信息及`success`、`message`字段 |
| `/user/change_own_password` | POST | 用户修改自身密码 | JSON格式：`old_password`（旧密码）、`password`（新密码） | 普通用户 | JSON：`{'success': 布尔值, 'message': 信息}` |
| `/user/get_user_vehicles` | GET | 用户分页获取自身车辆列表 | `cursor`（游标，默认0）、`limit`（每页条数，默认10，最大100） | 普通用户 | JSON：车辆列表及分页信息、`success`、`message`字段 |
| `/user/get_user_vehicle_info` | GET | 用户获取自身指定车辆信息 | `vehicle_id`（车辆ID） | 普通用户 | JSON：车辆信息及`success`、`message`字段 |
| `/logout` | GET | 退出登录 | 无 | 已登录用户 | 重定向到登录页 |
| `/404` | - | 404错误页面 | 无 | 无 | 404错误页面HTML |
| `/500` | - | 500错误页面 | 无 | 无 | 500错误页面HTML |
