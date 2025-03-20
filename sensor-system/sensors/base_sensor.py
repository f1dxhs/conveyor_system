# 传感器基类和公共定义
import os
import time
import datetime
import logging
import queue
import threading
from abc import ABC, abstractmethod
from enum import Enum

# 传感器类型枚举
class SensorType(Enum):
    CAMERA = 1         # 摄像头
    VIBRATION = 2      # 振动传感器
    TEMPERATURE = 3    # 温度传感器
    ACOUSTIC = 4       # 声学传感器
    SPEED = 5          # 速度传感器
    CURRENT = 6        # 电流传感器

# 传感器状态枚举
class SensorStatus(Enum):
    OFFLINE = 0        # 离线
    ONLINE = 1         # 在线
    ERROR = 2          # 错误
    CALIBRATING = 3    # 校准中
    WARMING_UP = 4     # 预热中

class BaseSensor(ABC):
    """传感器基类，定义所有传感器的通用接口"""
    
    def __init__(self, sensor_type, config):
        """
        初始化传感器
        
        参数:
            sensor_type: 传感器类型(SensorType枚举)
            config: 传感器配置字典
        """
        self.sensor_type = sensor_type
        self.config = config
        self.status = SensorStatus.OFFLINE
        self.last_reading_time = None
        self.error_count = 0
        self.max_errors = 5
        self.device_id = config.get('device_id')
        self.simulate = config.get('simulate', False)
        self.data_queue = queue.Queue()
        self.running = False
        self.thread = None
        
        # 创建传感器存储目录
        self.data_dir = os.path.join('sensor_data', self.sensor_type.name.lower())
        os.makedirs(self.data_dir, exist_ok=True)
        
        logging.info(f"初始化 {self.sensor_type.name} 传感器, ID: {self.device_id}")
    
    def start(self):
        """启动传感器数据采集"""
        if self.running:
            logging.warning(f"{self.sensor_type.name} 传感器已在运行")
            return False
        
        self.running = True
        self.thread = threading.Thread(target=self._acquisition_loop)
        self.thread.daemon = True
        self.thread.start()
        
        logging.info(f"{self.sensor_type.name} 传感器启动成功")
        return True
    
    def stop(self):
        """停止传感器数据采集"""
        if not self.running:
            return False
            
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        
        self._disconnect()
        self.status = SensorStatus.OFFLINE
        
        logging.info(f"{self.sensor_type.name} 传感器已停止")
        return True
    
    def get_data(self, blocking=False, timeout=1.0):
        """
        获取传感器数据
        
        参数:
            blocking: 是否阻塞等待
            timeout: 超时时间(秒)
            
        返回:
            传感器数据字典或None(如果没有数据)
        """
        try:
            return self.data_queue.get(block=blocking, timeout=timeout)
        except queue.Empty:
            return None
    
    def _acquisition_loop(self):
        """数据采集循环"""
        try:
            if not self._connect():
                logging.error(f"{self.sensor_type.name} 传感器连接失败")
                self.running = False
                self.status = SensorStatus.ERROR
                return
            
            # 设置为online状态
            self.status = SensorStatus.ONLINE
            
            while self.running:
                try:
                    # 读取传感器数据
                    if self.simulate:
                        data = self._simulate_reading()
                    else:
                        data = self._read()
                    
                    if data is not None:
                        # 添加元数据
                        timestamp = datetime.datetime.now().isoformat()
                        self.last_reading_time = timestamp
                        
                        reading = {
                            'sensor_type': self.sensor_type.name,
                            'device_id': self.device_id,
                            'timestamp': timestamp,
                            'data': data,
                            'status': self.status.name
                        }
                        
                        # 将数据放入队列
                        self.data_queue.put(reading)
                        
                        # 可选: 保存到本地
                        self._save_reading(reading)
                    
                    # 重置错误计数
                    self.error_count = 0
                    
                except Exception as e:
                    self.error_count += 1
                    logging.error(f"{self.sensor_type.name} 传感器读取错误: {str(e)}")
                    
                    if self.error_count >= self.max_errors:
                        self.status = SensorStatus.ERROR
                        logging.error(f"{self.sensor_type.name} 传感器错误次数过多，将重新连接")
                        self._disconnect()
                        time.sleep(2)
                        self._connect()
                
                # 根据采样率休眠
                if hasattr(self, 'sampling_interval'):
                    time.sleep(self.sampling_interval)
        
        except Exception as e:
            logging.error(f"{self.sensor_type.name} 传感器采集循环异常: {str(e)}")
            self.status = SensorStatus.ERROR
        
        finally:
            self._disconnect()
            self.status = SensorStatus.OFFLINE
    
    def _save_reading(self, reading):
        """保存传感器数据到本地"""
        # 实现本地存储逻辑...
        pass
    
    @abstractmethod
    def _connect(self):
        """连接到传感器设备"""
        pass
    
    @abstractmethod
    def _disconnect(self):
        """断开与传感器设备的连接"""
        pass
    
    @abstractmethod
    def _read(self):
        """读取传感器数据"""
        pass
    
    @abstractmethod
    def _simulate_reading(self):
        """模拟传感器读数(用于测试)"""
        pass