# 温度相关路由定义
from flask import Blueprint
from app.controllers.temperature_controller import update_bearing_temperature, get_bearing_temperature_status

# 创建蓝图
temperature_bp = Blueprint('temperature', __name__)

# 注册路由
temperature_bp.route('/bearing-temperature', methods=['POST'])(update_bearing_temperature)
temperature_bp.route('/bearing-temperature/status', methods=['GET'])(get_bearing_temperature_status)