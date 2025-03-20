# 温度传感器实现
import time
import datetime
import random
import logging
import requests
from sensors.base_sensor import BaseSensor, SensorType, SensorStatus

logger = logging.getLogger("TemperatureSensor")

class TemperatureSensor(BaseSensor):
    """温度传感器，用于监测托辊轴承温度"""
    
    def __init__(self, config):
        super().__init__(SensorType.TEMPERATURE, config)
        self.sampling_rate = config.get('sampling_rate', 1)  # Hz
        self.temp_range = config.get('range', (-20, 150))  # 摄氏度
        self.resolution = config.get('resolution', 0.1)
        self.serial_port = None
        self.sampling_interval = 1.0 / self.sampling_rate
        
        # 单位
        self.unit = config.get('params', {}).get('unit', 'celsius')
    
    def _connect(self):
        """连接到温度传感器"""
        try:
            if self.simulate:
                logger.info("使用模拟温度传感器数据")
                return True
            
            # 实际硬件连接代码...
            
        except Exception as e:
            logger.error(f"温度传感器连接失败: {str(e)}")
            return False
    
    def _disconnect(self):
        """断开与温度传感器的连接"""
        # 实现断开连接逻辑...
        pass
    
    def _read(self):
        """读取温度传感器数据"""
        if self.simulate:
            return self._simulate_reading()
        
        # 实际硬件读取代码...
    
    def _simulate_reading(self):
        """模拟温度传感器数据"""
        # 轴承的正常工作温度
        normal_temp = 35.0  # 摄氏度
        
        # 温度随时间缓慢变化
        time_factor = time.time() / 3600  # 一小时周期
        periodic_component = 5 * (time_factor % 1)  # 5度周期变化
        
        # 随机噪声
        noise = random.uniform(-0.5, 0.5)
        
        # 每1000个样本产生一次异常高温
        anomaly = random.random() < 0.001
        
        if anomaly:
            # 异常高温
            anomaly_temp = random.uniform(15.0, 60.0)
            logger.info(f"模拟温度异常，增加: {anomaly_temp:.2f}°C")
        else:
            anomaly_temp = 0
        
        # 最终温度
        temperature = normal_temp + periodic_component + noise + anomaly_temp
        
        # 发送到主系统
        self._send_to_main_system(temperature)
        
        return {
            'temperature': temperature,
            'unit': self.unit,
            'simulated': True,
            'anomaly': anomaly
        }
    
    def _send_to_main_system(self, temperature):
        """将温度数据发送到主系统"""
        try:
            response = requests.post(
                'http://localhost:5000/api/bearing-temperature',
                json={'temperature': temperature},
                timeout=2
            )
            if response.status_code != 200:
                logger.warning(f"发送温度数据失败: {response.status_code}")
        except Exception as e:
            logger.error(f"发送温度数据异常: {str(e)}")