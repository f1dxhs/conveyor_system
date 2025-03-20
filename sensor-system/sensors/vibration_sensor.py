# 振动传感器实现
import time
import datetime
import random
import numpy as np
import logging
import json
import os
import serial
import requests
from .base_sensor import BaseSensor, SensorType, SensorStatus

logger = logging.getLogger("VibrationSensor")

class VibrationSensor(BaseSensor):
    """振动传感器，用于检测托辊振动情况"""
    
    def __init__(self, config):
        super().__init__(SensorType.VIBRATION, config)
        self.sampling_rate = config.get('sampling_rate', 1000)  # Hz
        self.sensitivity = config.get('sensitivity', 100)
        self.axis = config.get('axis', 3)  # 轴数(1-3)
        self.serial_port = None
        self.sampling_interval = 1.0 / self.sampling_rate
        
        # 串口参数
        self.baud_rate = config.get('params', {}).get('baud_rate', 9600)
        self.data_bits = config.get('params', {}).get('data_bits', 8)
        self.stop_bits = config.get('params', {}).get('stop_bits', 1)
        
        # FFT分析参数
        self.fft_size = 1024
        self.fft_history = []
        self.max_fft_history = 10
        
        # 故障特征频率(Hz) - 不同故障类型的特征频率
        self.fault_frequencies = {
            'bearing_outer': [85.4, 103.6, 128.9],  # 轴承外圈故障
            'bearing_inner': [142.8, 165.2, 189.7], # 轴承内圈故障
            'roller_defect': [46.3, 68.7, 93.5],    # 滚动体故障
            'cage_defect': [11.2, 17.5, 24.8],      # 保持架故障
            'unbalance': [23.3, 35.7, 47.1],        # 不平衡
            'misalignment': [117.6, 134.2, 151.8]   # 不对中
        }
    
    def _connect(self):
        """连接到振动传感器"""
        try:
            if self.simulate:
                logger.info("使用模拟振动传感器数据")
                return True
                
            # 连接到实际振动传感器(通过串口)
            self.serial_port = serial.Serial(
                port=self.device_id,
                baudrate=self.baud_rate,
                bytesize=self.data_bits,
                stopbits=self.stop_bits,
                timeout=1
            )
            
            # 发送初始化命令
            self.serial_port.write(b'INIT\r\n')
            response = self.serial_port.readline().decode('ascii').strip()
            
            if response != 'OK':
                logger.error(f"振动传感器初始化失败，响应: {response}")
                return False
            
            # 设置采样率
            self.serial_port.write(f'RATE {self.sampling_rate}\r\n'.encode('ascii'))
            response = self.serial_port.readline().decode('ascii').strip()
            
            if response != 'OK':
                logger.warning(f"设置采样率失败，响应: {response}")
            
            logger.info(f"振动传感器连接成功: {self.device_id}")
            return True
            
        except Exception as e:
            logger.error(f"振动传感器连接失败: {str(e)}")
            return False
    
    def _disconnect(self):
        """断开与振动传感器的连接"""
        if self.serial_port and not self.simulate:
            try:
                # 发送关闭命令
                self.serial_port.write(b'CLOSE\r\n')
                # 等待响应
                time.sleep(0.2)
                # 关闭串口
                self.serial_port.close()
                self.serial_port = None
                logger.info("振动传感器已断开连接")
            except Exception as e:
                logger.error(f"断开振动传感器连接时出错: {str(e)}")
    
    def _read(self):
        """读取振动传感器数据"""
        if self.simulate:
            return self._simulate_reading()
            
        if not self.serial_port:
            raise Exception("振动传感器未连接")
        
        # 发送读取命令
        self.serial_port.write(b'READ\r\n')
        
        # 读取响应
        response = self.serial_port.readline().decode('ascii').strip()
        
        # 解析响应
        # 假设响应格式为: "X:0.123,Y:0.456,Z:0.789"
        values = {}
        parts = response.split(',')
        
        for part in parts:
            if ':' in part:
                axis, value = part.split(':')
                values[axis.strip()] = float(value.strip())
        
        # 计算合成振动值
        composite = 0
        for axis_value in values.values():
            composite += axis_value ** 2
        composite = composite ** 0.5
        
        # 进行FFT分析
        fft_result = self._perform_fft(values)
        
        # 检测故障模式
        fault_detection = self._detect_faults(fft_result)
        
        return {
            'axis_values': values,
            'composite': composite,
            'unit': 'g',
            'sampling_rate': self.sampling_rate,
            'fft_peaks': fft_result['peaks'],
            'fault_detection': fault_detection
        }
    
    def _simulate_reading(self):
        """模拟振动传感器数据"""
        # 生成随机振动数据
        values = {}
        
        # 基线振动值 + 随机噪声
        baseline = 0.1  # 正常运行时的基线振动
        
        # 周期性组件，模拟轴承或其他部件旋转
        rotation_freq = 30.0  # 假设30Hz的旋转频率
        phase = time.time() * rotation_freq
        
        # 每500个样本产生一次异常
        anomaly = random.random() < 0.002
        
        # 选择异常类型
        if anomaly:
            fault_type = random.choice(list(self.fault_frequencies.keys()))
            fault_freqs = self.fault_frequencies[fault_type]
            anomaly_factor = random.uniform(3.0, 10.0)
            logger.info(f"模拟振动异常，类型: {fault_type}, 放大系数: {anomaly_factor:.2f}")
        else:
            fault_type = None
            anomaly_factor = 1.0
        
        # 生成各轴振动数据
        axes = ['X', 'Y', 'Z']
        for i in range(min(self.axis, 3)):
            axis = axes[i]
            # 不同轴的振动特性略有不同
            axis_factor = 1.0 if axis == 'Y' else (0.8 if axis == 'X' else 1.2)
            
            # 正弦波模拟旋转部件 + 噪声
            sine_component = 0.05 * np.sin(phase * axis_factor)
            noise_component = random.uniform(-0.03, 0.03)
            
            # 如果存在故障，添加故障频率的振动分量
            fault_component = 0
            if anomaly and fault_type:
                for freq in fault_freqs:
                    fault_component += 0.08 * np.sin(time.time() * freq * 2 * np.pi)
                fault_component *= anomaly_factor
            
            values[axis] = (baseline + sine_component + noise_component + fault_component) * axis_factor
        
        # 计算合成振动值
        composite = 0
        for axis_value in values.values():
            composite += axis_value ** 2
        composite = composite ** 0.5
        
        # 模拟FFT结果
        fft_result = self._simulate_fft(values, fault_type if anomaly else None)
        
        # 检测故障模式
        fault_detection = self._detect_faults(fft_result)
        
        # 发送到异常检测系统
        if anomaly:
            self._send_vibration_alert(composite, fault_type, fault_detection)
        
        return {
            'axis_values': values,
            'composite': composite,
            'unit': 'g',
            'sampling_rate': self.sampling_rate,
            'simulated': True,
            'anomaly': anomaly,
            'fault_type': fault_type if anomaly else 'none',
            'fft_peaks': fft_result['peaks'],
            'fault_detection': fault_detection
        }
    
    def _perform_fft(self, values):
        """执行FFT分析"""
        # 在实际实现中，我们需要收集一段时间的数据，然后进行FFT
        # 这里简化处理
        
        # 模拟一些频率峰值
        peaks = []
        for axis, value in values.items():
            # 随机生成一些峰值频率
            for _ in range(3):
                freq = random.uniform(10, 200)
                amplitude = abs(value) * random.uniform(0.5, 1.0)
                peaks.append({
                    'frequency': freq,
                    'amplitude': amplitude,
                    'axis': axis
                })
        
        # 按幅值降序排序
        peaks.sort(key=lambda x: x['amplitude'], reverse=True)
        
        return {
            'peaks': peaks[:5],  # 只返回最大的5个峰值
            'time': time.time()
        }
    
    def _simulate_fft(self, values, fault_type=None):
        """模拟FFT分析结果"""
        peaks = []
        
        # 添加基本旋转频率
        base_freq = 30.0  # 基础旋转频率
        for axis, value in values.items():
            amplitude = abs(value) * random.uniform(0.7, 1.0)
            peaks.append({
                'frequency': base_freq,
                'amplitude': amplitude,
                'axis': axis
            })
            
            # 添加谐波
            for harmonic in [2, 3]:
                peaks.append({
                    'frequency': base_freq * harmonic,
                    'amplitude': amplitude * (1.0 / harmonic) * random.uniform(0.8, 1.2),
                    'axis': axis
                })
        
        # 添加噪声频率
        for _ in range(5):
            freq = random.uniform(5, 300)
            amplitude = random.uniform(0.01, 0.05)
            axis = random.choice(['X', 'Y', 'Z'])
            peaks.append({
                'frequency': freq,
                'amplitude': amplitude,
                'axis': axis
            })
        
        # 如果有故障，添加故障频率
        if fault_type and fault_type in self.fault_frequencies:
            fault_freqs = self.fault_frequencies[fault_type]
            for freq in fault_freqs:
                amplitude = random.uniform(0.1, 0.3)
                axis = random.choice(['X', 'Y', 'Z'])
                peaks.append({
                    'frequency': freq,
                    'amplitude': amplitude,
                    'axis': axis
                })
        
        # 按幅值降序排序
        peaks.sort(key=lambda x: x['amplitude'], reverse=True)
        
        return {
            'peaks': peaks[:8],  # 取前8个最大的峰值
            'time': time.time()
        }
    
    def _detect_faults(self, fft_result):
        """根据FFT结果检测可能的故障"""
        fault_scores = {fault_type: 0 for fault_type in self.fault_frequencies}
        
        for peak in fft_result['peaks']:
            freq = peak['frequency']
            amp = peak['amplitude']
            
            # 检查每个频率是否接近故障特征频率
            for fault_type, freqs in self.fault_frequencies.items():
                for fault_freq in freqs:
                    # 如果频率接近故障特征频率
                    if abs(freq - fault_freq) < 3.0:  # 允许3Hz误差
                        # 计算分数(幅值越大分数越高)
                        fault_scores[fault_type] += amp * 10
        
        # 找出得分最高的故障类型
        max_fault = max(fault_scores.items(), key=lambda x: x[1])
        
        # 如果分数超过阈值，认为存在故障
        if max_fault[1] > 0.2:
            confidence = min(max_fault[1], 1.0)  # 限制置信度在0-1之间
            return {
                'detected': True,
                'fault_type': max_fault[0],
                'confidence': confidence,
                'all_scores': fault_scores
            }
        else:
            return {
                'detected': False,
                'all_scores': fault_scores
            }
    
    def _send_vibration_alert(self, magnitude, fault_type, detection_result):
        """发送振动异常警报到主系统"""
        try:
            # 构建警报数据
            alert_data = {
                'sensor_type': 'vibration',
                'timestamp': datetime.datetime.now().isoformat(),
                'magnitude': magnitude,
                'fault_type': fault_type,
                'detection_result': detection_result,
                'severity': 'high' if magnitude > 1.0 else 'medium'
            }
            
            # 发送到主系统
            response = requests.post(
                'http://localhost:5000/api/alerts',
                json=alert_data,
                timeout=2
            )
            
            if response.status_code != 200:
                logger.warning(f"发送振动警报失败: {response.status_code}")
                
        except Exception as e:
            logger.error(f"发送振动警报异常: {str(e)}")