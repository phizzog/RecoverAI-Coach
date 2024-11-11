import React from 'react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const WhoopData = ({ data, onWeekChange, currentWeekStart }) => {
  if (!data || data.length === 0) {
    return <div>Loading Whoop data...</div>;
  }

  // Add week navigation controls
  const handleWeekChange = (direction) => {
    const currentDate = new Date(currentWeekStart);
    const newDate = new Date(currentDate);
    
    if (direction === 'prev') {
      // Move back 7 days
      newDate.setDate(currentDate.getDate() - 7);
      onWeekChange(newDate.toISOString().split('T')[0]);
    } else if (direction === 'next') {
      // Move forward 7 days, but not beyond today - 6 days
      const today = new Date();
      const sixDaysAgo = new Date(today);
      sixDaysAgo.setDate(today.getDate() - 6);
      
      newDate.setDate(currentDate.getDate() + 7);
      if (newDate <= sixDaysAgo) {
        onWeekChange(newDate.toISOString().split('T')[0]);
      }
    }
  };

  // Calculate and format date range
  const startDate = new Date(currentWeekStart);
  const endDate = new Date(startDate);
  endDate.setDate(startDate.getDate() + 6);
  
  const formatDate = (date) => {
    return date.toLocaleDateString('en-US', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  const dateRangeString = `${formatDate(startDate)} - ${formatDate(endDate)}`;

  // Disable next button if we're at the current week
  const today = new Date();
  const sixDaysAgo = new Date(today);
  sixDaysAgo.setDate(today.getDate() - 6);
  const isCurrentWeek = new Date(currentWeekStart) >= sixDaysAgo;

  // Prepare data for charts (reverse to show chronological order)
  const chartData = [...data].reverse().map(day => ({
    date: new Date(day.date).getDate(), // Convert to day number
    recovery: day.recovery_score,
    sleep: day.sleep_data?.duration,
    strain: day.strain_data?.day_strain,
    efficiency: day.sleep_data?.metrics?.efficiency_percentage
  }));

  // Calculate weekly totals
  const weeklyTotals = data.reduce((acc, day) => {
    // Sleep totals
    acc.totalSleep += day.sleep_data?.duration || 0;
    acc.avgRecovery += day.recovery_score || 0;
    acc.avgStrain += day.strain_data?.day_strain || 0;
    
    // Workout totals
    const workouts = day.strain_data?.workouts || [];
    workouts.forEach(workout => {
      acc.totalWorkoutTime += workout.duration || 0;
      acc.workoutCount++;
      
      // Sum up zone durations
      Object.entries(workout.zone_duration || {}).forEach(([zone, duration]) => {
        acc.zoneData[zone] = (acc.zoneData[zone] || 0) + (duration / 60000); // Convert to minutes
      });
    });
    
    return acc;
  }, {
    totalSleep: 0,
    avgRecovery: 0,
    avgStrain: 0,
    totalWorkoutTime: 0,
    workoutCount: 0,
    zoneData: {}
  });

  // Calculate averages
  weeklyTotals.avgRecovery = weeklyTotals.avgRecovery / data.length;
  weeklyTotals.avgStrain = weeklyTotals.avgStrain / data.length;

  // Prepare zone data for pie chart
  const zoneColors = {
    zone_zero_milli: '#gray',
    zone_one_milli: '#43b581',
    zone_two_milli: '#7289da',
    zone_three_milli: '#faa61a',
    zone_four_milli: '#f04747',
    zone_five_milli: '#purple'
  };

  const zoneLabels = {
    zone_zero_milli: 'Zone 0 (Rest)',
    zone_one_milli: 'Zone 1 (Easy)',
    zone_two_milli: 'Zone 2 (Moderate)',
    zone_three_milli: 'Zone 3 (Hard)',
    zone_four_milli: 'Zone 4 (Very Hard)',
    zone_five_milli: 'Zone 5 (Peak)'
  };

  const zonePieData = Object.entries(weeklyTotals.zoneData)
    .filter(([_, value]) => value > 0)
    .map(([zone, value]) => ({
      name: zoneLabels[zone],
      value: Math.round(value),
      color: zoneColors[zone]
    }));

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-chart-tooltip">
          <p>Date: {label}</p>
          {payload.map((entry, index) => (
            <p key={index} style={{ color: entry.color }}>
              {entry.name}: {entry.value?.toFixed(2)}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="whoop-summary">
      <div className="week-navigation">
        <button 
          className="nav-button prev"
          onClick={() => handleWeekChange('prev')}
        >
          ←
        </button>
        <div className="week-info">
          <h2>Whoop Data Summary</h2>
          <div className="date-range">{dateRangeString}</div>
        </div>
        <button 
          className="nav-button next"
          onClick={() => handleWeekChange('next')}
          disabled={isCurrentWeek}
        >
          →
        </button>
      </div>
      
      {/* Weekly Overview Section */}
      <div className="weekly-overview">
        <h3>Weekly Overview</h3>
        <div className="metrics-grid">
          <div className="metric-box overview">
            <span className="label">Total Sleep</span>
            <span className="value">{Math.round(weeklyTotals.totalSleep)} min</span>
            <span className="sub-value">({Math.round(weeklyTotals.totalSleep / 60)} hours)</span>
          </div>
          <div className="metric-box overview">
            <span className="label">Avg Recovery</span>
            <span className="value">{weeklyTotals.avgRecovery.toFixed(1)}%</span>
          </div>
          <div className="metric-box overview">
            <span className="label">Avg Strain</span>
            <span className="value">{weeklyTotals.avgStrain.toFixed(1)}</span>
          </div>
          <div className="metric-box overview">
            <span className="label">Total Workout Time</span>
            <span className="value">{Math.round(weeklyTotals.totalWorkoutTime)} min</span>
            <span className="sub-value">({weeklyTotals.workoutCount} workouts)</span>
          </div>
        </div>
      </div>

      {/* Heart Rate Zones Chart */}
      <div className="charts-section">
        <div className="chart-container">
          <h3>Weekly Heart Rate Zones</h3>
          <div className="zone-chart-container">
            <ResponsiveContainer width="50%" height={200}>
              <PieChart>
                <Pie
                  data={zonePieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, value }) => `${name}: ${value}min`}
                >
                  {zonePieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <div className="zone-legend">
              {zonePieData.map((zone, index) => (
                <div key={index} className="zone-legend-item">
                  <span className="zone-color" style={{ backgroundColor: zone.color }}></span>
                  <span className="zone-name">{zone.name}</span>
                  <span className="zone-value">{zone.value} min</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Existing Charts */}
        <div className="chart-container">
          <h3>Recovery & Strain</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <XAxis dataKey="date" stroke="#dcddde" />
              <YAxis stroke="#dcddde" />
              <Tooltip content={<CustomTooltip />} />
              <Line type="monotone" dataKey="recovery" stroke="#43b581" name="Recovery" />
              <Line type="monotone" dataKey="strain" stroke="#faa61a" name="Strain" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-container">
          <h3>Sleep Duration</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={chartData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
              <XAxis dataKey="date" stroke="#dcddde" />
              <YAxis stroke="#dcddde" />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="sleep" fill="#7289da" name="Sleep Duration" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Daily Cards */}
      <div className="whoop-cards">
        {data.map((day, index) => (
          <div key={index} className="whoop-card">
            <h3 className="date">{day.date}</h3>
            
            <div className="metrics-grid">
              <div className="metric-box recovery">
                <span className="label">Recovery Score</span>
                <span className="value">{day.recovery_score || 'N/A'}</span>
              </div>
              
              <div className="metric-box sleep">
                <span className="label">Sleep Duration</span>
                <span className="value">{day.sleep_data?.duration || 'N/A'} min</span>
              </div>
              
              <div className="metric-box strain">
                <span className="label">Day Strain</span>
                <span className="value">{day.strain_data?.day_strain || 'N/A'}</span>
              </div>
            </div>

            {/* Sleep Metrics Section */}
            <div className="sleep-metrics">
              <h4>Sleep Metrics</h4>
              <div className="metrics-grid">
                <div className="metric">
                  <span className="label">Efficiency</span>
                  <span className="value">
                    {day.sleep_data?.metrics?.efficiency_percentage 
                      ? `${day.sleep_data.metrics.efficiency_percentage.toFixed(2)}%`
                      : 'N/A'}
                  </span>
                </div>
                <div className="metric">
                  <span className="label">Light Sleep</span>
                  <span className="value">{day.sleep_data?.metrics?.light_sleep_time || 'N/A'} min</span>
                </div>
                <div className="metric">
                  <span className="label">Deep Sleep</span>
                  <span className="value">{day.sleep_data?.metrics?.slow_wave_sleep_time || 'N/A'} min</span>
                </div>
                <div className="metric">
                  <span className="label">REM Sleep</span>
                  <span className="value">{day.sleep_data?.metrics?.rem_sleep_time || 'N/A'} min</span>
                </div>
              </div>
            </div>

            {/* Workouts Section */}
            {day.strain_data?.workouts && day.strain_data.workouts.length > 0 && (
              <div className="workouts">
                <h4>Workouts</h4>
                {day.strain_data.workouts.map((workout, wIndex) => {
                  // Calculate zone percentages for this workout
                  const totalTime = Object.values(workout.zone_duration || {}).reduce((a, b) => a + b, 0) / 60000; // Convert to minutes
                  const zoneData = Object.entries(workout.zone_duration || {}).map(([zone, duration]) => ({
                    name: zoneLabels[zone],
                    value: (duration / 60000), // Convert to minutes
                    color: zoneColors[zone]
                  })).filter(zone => zone.value > 0);

                  return (
                    <div key={wIndex} className="workout">
                      <div className="workout-header">
                        <span className="sport">{workout.sport}</span>
                        <span className="duration">{workout.duration} min</span>
                      </div>
                      <div className="workout-metrics">
                        <div className="metric">
                          <span className="label">Strain</span>
                          <span className="value">{workout.strain}</span>
                        </div>
                        <div className="metric">
                          <span className="label">Avg HR</span>
                          <span className="value">{workout.average_hr || 'N/A'} bpm</span>
                        </div>
                        <div className="metric">
                          <span className="label">Max HR</span>
                          <span className="value">{workout.max_hr || 'N/A'} bpm</span>
                        </div>
                      </div>
                      {/* Workout Zone Chart */}
                      <div className="workout-zones">
                        <h5>Heart Rate Zones</h5>
                        <div className="zone-bars">
                          {zoneData.map((zone, zIndex) => (
                            <div key={zIndex} className="zone-bar-container">
                              <div 
                                className="zone-bar" 
                                style={{ 
                                  width: `${(zone.value / totalTime) * 100}%`,
                                  backgroundColor: zone.color 
                                }}
                              />
                              <span className="zone-label">{zone.name}</span>
                              <span className="zone-time">{Math.round(zone.value)}min</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default WhoopData;
