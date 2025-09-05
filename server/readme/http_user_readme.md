| 接口路径 | 请求方法 | 参数 | 说明 | 响应 |
|----------|----------|------|------|------|
| `/get_current_user_info` | GET/POST | `name`（必填）：用户名 | 获取当前用户信息（不含敏感字段） | 成功（200）：<br>`{"success": true, "data": {用户信息}}`<br>失败：<br>- 401：`{"success": false, "message": "用户不存在"}`<br>- 500：`{"success": false, "message": "查询失败"}` |
| `/change_own_password` | GET/POST | `name`（必填）：用户名<br>`old_password`（必填）：旧密码<br>`password`（必填）：新密码 | 修改当前用户密码 | 成功（200）：<br>`{"success": true, "message": "修改成功"}`<br>失败（200）：<br>`{"success": false, "message": "错误信息"}`（旧密码错误等） |
| `/get_user_vehicles` | GET/POST | `name`（必填）：用户名<br>`cursor`（可选）：分页游标，默认0<br>`limit`（可选）：每页数量，默认10（最大100） | 获取用户名下的车辆列表（分页） | 成功（200）：<br>`{"success": true, "data": [车辆列表], "total": 总数, "next_cursor": 下一页游标, "limit": 每页数量}`<br>失败：<br>- 401：`{"success": false, "message": "用户不存在"}`<br>- 500：`{"success": false, "message": "查询失败信息"}` |
| `/get_next_vehicle_info` | GET/POST | `name`（必填）：用户名<br>`vehicle_id`（必填）：车辆ID | 获取指定车辆的详细信息（含最后通行记录） | 成功（200）：<br>`{"success": true, "data": {车辆信息（含last_location等扩展字段）}}`<br>失败：<br>- 400：`{"success": false, "message": "车辆ID为必填项"}`<br>- 403：`{"success": false, "message": "无权访问该车辆信息"}`<br>- 404：`{"success": false, "message": "车辆不存在"}` |

> 注：所有接口的请求参数，GET方法从查询字符串获取，POST方法从JSON请求体获取；响应格式均为JSON，Content-Type为`application/json; charset=utf-8`。未匹配的路径返回404错误。

1. **用户身份验证**：所有接口都会先验证用户是否存在
2. **权限控制**：查询车辆信息时会验证车辆是否属于当前用户
3. **数据安全**：用户信息查询不返回密码或密码哈希
4. **分页机制**：车辆列表查询支持分段获取，避免数据量过大
5. **关联数据查询**：车辆最后出现位置会关联查询通行记录和传感器信息
