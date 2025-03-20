# 轴承温度监测服务
import datetime

class BearingTemperatureMonitor:
    """轴承温度监测器，用于分析温度数据并确定告警级别"""
    
    def __init__(self):
        # 定义温度阈值（摄氏度）
        self.normal_threshold = 60.0    # 正常温度的上限
        self.warning_threshold = 80.0   # 警告温度的上限
        
        # 告警状态
        self.NORMAL = "normal"      # 绿灯
        self.WARNING = "warning"    # 黄灯
        self.DANGER = "danger"      # 红灯
        
        # 状态历史记录
        self.status_history = []
        self.max_history_size = 100
        self.current_status = self.NORMAL
        
        # 统计信息
        self.stats = {
            "max_temperature": 0.0,
            "min_temperature": float('inf'),
            "avg_temperature": 0.0,
            "total_readings": 0,
            "normal_count":.0,
            "warning_count": 0,
            "danger_count": 0,
            "last_danger_time": None
        }
    
    def evaluate_temperature(self, temperature):
        """评估温度并返回状态"""
        # 更新统计信息
        self._update_stats(temperature)
        
        # 确定状态
        status = self.NORMAL
        if temperature >= self.warning_threshold:
            status = self.DANGER
        elif temperature >= self.normal_threshold:
            status = self.WARNING
        
        # 更新当前状态和历史记录
        self.current_status = status
        self.status_history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "temperature": temperature,
            "status": status
        })
        
        # 限制历史记录大小
        if len(self.status_history) > self.max_history_size:
            self.status_history.pop(0)
        
        return status
    
    def _update_stats(self, temperature):
        """更新温度统计信息"""
        # 实现统计逻辑...
        pass
    
    def get_current_status(self):
        """获取当前状态和相关统计信息"""
        return {
            "status": self.current_status,
            "stats": self.stats,
            "last_readings": self.status_history[-10:] if self.status_history else []
        }