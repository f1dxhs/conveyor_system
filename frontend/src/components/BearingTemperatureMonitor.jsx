import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import axios from 'axios';

const BearingTemperatureMonitor = () => {
  const [temperatureData, setTemperatureData] = useState({
    status: 'normal',
    stats: {
      max_temperature: 0,
      min_temperature: 0,
      avg_temperature: 0
    },
    last_readings: []
  });
  
  // 定义警报颜色
  const statusColors = {
    normal: '#4caf50',    // 绿色
    warning: '#ff9800',   // 黄色
    danger: '#f44336'     // 红色
  };
  
  // 轮询获取温度数据
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get('/api/bearing-temperature/status');
        if (response.data.success) {
          setTemperatureData(response.data.data);
        }
      } catch (error) {
        console.error('获取轴承温度数据失败:', error);
      }
    };
    
    // 每5秒获取一次数据
    const intervalId = setInterval(fetchData, 5000);
    fetchData(); // 立即获取一次
    
    return () => clearInterval(intervalId);
  }, []);
  
  // JSX UI渲染代码，包含状态指示灯、温度统计信息、图表等
  return (
    <div className="bearing-temperature-monitor">
      <h2>轴承温度监测</h2>
      
      {/* 状态指示灯 */}
      <div className="status-indicator" 
           style={{backgroundColor: statusColors[temperatureData.status]}}>
        <h3>当前状态: {temperatureData.status === 'normal' ? '正常' : 
                    (temperatureData.status === 'warning' ? '警告' : '危险')}</h3>
      </div>
      
      {/* 温度图表和其他UI元素... */}
    </div>
  );
};

export default BearingTemperatureMonitor;