# 温度控制器 - 处理温度相关API请求
from flask import request, jsonify, current_app

def update_bearing_temperature():
    """接收并处理轴承温度数据"""
    try:
        data = request.json
        temperature = data.get('temperature')
        
        if temperature is None:
            return jsonify({"success": False, "message": "未提供温度数据"}), 400
        
        # 获取全局InspectionSystem实例
        inspection_system = current_app.inspection_system
        
        # 评估温度
        status = inspection_system.temp_monitor.evaluate_temperature(temperature)
        
        return jsonify({
            "success": True,
            "temperature": temperature,
            "status": status
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"错误: {str(e)}"}), 500

def get_bearing_temperature_status():
    """获取轴承温度监测状态"""
    try:
        # 获取全局InspectionSystem实例
        inspection_system = current_app.inspection_system
        
        status_data = inspection_system.temp_monitor.get_current_status()
        
        return jsonify({
            "success": True,
            "data": status_data
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"错误: {str(e)}"}), 500