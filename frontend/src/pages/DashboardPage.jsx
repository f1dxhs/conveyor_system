import React from 'react';
import BearingTemperatureMonitor from '../components/BearingTemperatureMonitor';
// 导入其他组件...

const DashboardPage = () => {
  return (
    <div className="dashboard">
      <h1>系统监控仪表盘</h1>
      
      <div className="dashboard-grid">
        {/* 轴承温度监测模块 */}
        <div className="dashboard-card">
          <BearingTemperatureMonitor />
        </div>
        
        {/* 其他监测模块... */}
      </div>
    </div>
  );
};

export default DashboardPage;