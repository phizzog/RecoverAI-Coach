from typing import List, Dict, Any
import numpy as np
from datetime import datetime
import pandas as pd

class WhoopDataProcessor:
    def __init__(self, whoop_data: List[Dict[str, Any]]):
        self.raw_data = whoop_data
        self.processed_data = None
        self.summary_stats = None
        
    def process_data(self) -> Dict[str, Any]:
        """Main processing method that coordinates all preprocessing steps."""
        # Convert to pandas DataFrame for easier analysis
        df = pd.DataFrame(self.raw_data)
        
        # Process each component
        recovery_stats = self._analyze_recovery(df)
        sleep_stats = self._analyze_sleep(df)
        strain_stats = self._analyze_strain(df)
        workout_stats = self._analyze_workouts(df)
        
        # Identify trends and patterns
        trends = self._identify_trends(df)
        
        # Compile processed data
        self.processed_data = {
            "summary_metrics": {
                "recovery": recovery_stats,
                "sleep": sleep_stats,
                "strain": strain_stats,
                "workouts": workout_stats
            },
            "trends_and_patterns": trends,
            "time_period": {
                "start_date": df['date'].min(),
                "end_date": df['date'].max(),
                "total_days": len(df)
            }
        }
        
        return self.processed_data

    def _analyze_recovery(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze recovery scores and patterns."""
        recovery_scores = [day.get('recovery_score') for day in self.raw_data]
        valid_scores = [score for score in recovery_scores if score is not None]
        
        if not valid_scores:
            return {"error": "No valid recovery data available"}
        
        return {
            "average_recovery": np.mean(valid_scores),
            "recovery_trend": self._calculate_trend(valid_scores),
            "consistency": self._calculate_consistency(valid_scores),
            "days_below_33": sum(1 for score in valid_scores if score < 33),
            "days_above_66": sum(1 for score in valid_scores if score > 66)
        }

    def _analyze_sleep(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze sleep patterns and quality."""
        sleep_data = []
        sleep_efficiency = []
        
        for day in self.raw_data:
            if day.get('sleep_data'):
                sleep_data.append(day['sleep_data'].get('duration'))
                if day['sleep_data'].get('metrics'):
                    sleep_efficiency.append(day['sleep_data']['metrics'].get('efficiency_percentage'))
        
        valid_sleep = [s for s in sleep_data if s is not None]
        valid_efficiency = [e for e in sleep_efficiency if e is not None]
        
        return {
            "average_duration": np.mean(valid_sleep) if valid_sleep else None,
            "average_efficiency": np.mean(valid_efficiency) if valid_efficiency else None,
            "sleep_consistency": self._calculate_consistency(valid_sleep),
            "sleep_debt": self._calculate_sleep_debt(valid_sleep),
            "quality_metrics": self._analyze_sleep_quality(self.raw_data)
        }

    def _analyze_strain(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze strain patterns and intensity."""
        daily_strains = []
        
        for day in self.raw_data:
            if day.get('strain_data') and day['strain_data'].get('day_strain'):
                daily_strains.append(day['strain_data']['day_strain'])
        
        valid_strains = [s for s in daily_strains if s is not None]
        
        return {
            "average_strain": np.mean(valid_strains) if valid_strains else None,
            "strain_distribution": self._calculate_strain_distribution(valid_strains) if valid_strains else None,
            "strain_variability": np.std(valid_strains) if valid_strains else None,
            "peak_strain_day": max(valid_strains) if valid_strains else None
        }

    def _analyze_workouts(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze workout patterns and intensity."""
        all_workouts = []
        workout_types = {}
        total_duration = 0
        
        for day in self.raw_data:
            if day.get('strain_data') and day['strain_data'].get('workouts'):
                workouts = day['strain_data']['workouts']
                all_workouts.extend(workouts)
                
                for workout in workouts:
                    workout_type = workout.get('sport')
                    if workout_type:
                        workout_types[workout_type] = workout_types.get(workout_type, 0) + 1
                    total_duration += workout.get('duration', 0)
        
        return {
            "total_workouts": len(all_workouts),
            "workout_frequency": len(all_workouts) / len(self.raw_data),
            "workout_types": workout_types,
            "total_duration": total_duration,
            "average_duration": total_duration / len(all_workouts) if all_workouts else 0,
            "intensity_distribution": self._analyze_workout_intensity(all_workouts)
        }

    def _identify_trends(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Identify significant trends and patterns in the data."""
        recovery_strain_correlation = self._calculate_recovery_strain_correlation()
        sleep_recovery_correlation = self._calculate_sleep_recovery_correlation()
        
        return {
            "correlations": {
                "recovery_strain": recovery_strain_correlation,
                "sleep_recovery": sleep_recovery_correlation
            },
            "patterns": self._identify_significant_patterns(),
            "recommendations": self._generate_focus_areas()
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate if a metric is trending up, down, or stable."""
        if len(values) < 2:
            return "insufficient_data"
            
        slope = np.polyfit(range(len(values)), values, 1)[0]
        if slope > 0.1:
            return "improving"
        elif slope < -0.1:
            return "declining"
        return "stable"

    def _calculate_consistency(self, values: List[float]) -> float:
        """Calculate consistency score based on day-to-day variations."""
        if len(values) < 2:
            return 0
            
        variations = np.diff(values)
        consistency = 1 - (np.std(variations) / (max(values) - min(values)))
        return max(0, min(1, consistency))

    def _calculate_sleep_debt(self, sleep_durations: List[float]) -> float:
        """Calculate accumulated sleep debt in minutes."""
        target_sleep = 480  # 8 hours in minutes
        return sum(max(0, target_sleep - duration) for duration in sleep_durations)

    def _analyze_sleep_quality(self, raw_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze detailed sleep quality metrics."""
        rem_sleep = []
        deep_sleep = []
        light_sleep = []
        
        for day in raw_data:
            if day.get('sleep_data') and day['sleep_data'].get('metrics'):
                metrics = day['sleep_data']['metrics']
                rem_sleep.append(metrics.get('rem_sleep_time'))
                deep_sleep.append(metrics.get('slow_wave_sleep_time'))
                light_sleep.append(metrics.get('light_sleep_time'))
        
        valid_rem = [x for x in rem_sleep if x is not None]
        valid_deep = [x for x in deep_sleep if x is not None]
        valid_light = [x for x in light_sleep if x is not None]
        
        return {
            "average_rem": np.mean(valid_rem) if valid_rem else None,
            "average_deep": np.mean(valid_deep) if valid_deep else None,
            "average_light": np.mean(valid_light) if valid_light else None,
            "sleep_quality_score": self._calculate_sleep_quality_score(valid_rem, valid_deep, valid_light)
        }

    def _calculate_sleep_quality_score(self, rem: List[float], deep: List[float], light: List[float]) -> float:
        """Calculate overall sleep quality score based on sleep stage distributions."""
        if not (rem and deep and light):
            return None
            
        # Ideal proportions (approximate targets)
        ideal_rem_percent = 0.25    # 25% REM
        ideal_deep_percent = 0.20   # 20% Deep
        ideal_light_percent = 0.55  # 55% Light
        
        # Calculate actual proportions
        total_sleep = sum(rem) + sum(deep) + sum(light)
        if total_sleep == 0:
            return None
            
        actual_rem_percent = sum(rem) / total_sleep
        actual_deep_percent = sum(deep) / total_sleep
        actual_light_percent = sum(light) / total_sleep
        
        # Calculate how close we are to ideal proportions
        rem_score = 1 - abs(ideal_rem_percent - actual_rem_percent)
        deep_score = 1 - abs(ideal_deep_percent - actual_deep_percent)
        light_score = 1 - abs(ideal_light_percent - actual_light_percent)
        
        # Weight the scores (you can adjust these weights)
        weighted_score = (rem_score * 0.35 + deep_score * 0.35 + light_score * 0.3) * 100
        
        return round(weighted_score, 2)

    def _calculate_strain_distribution(self, strains: List[float]) -> Dict[str, int]:
        """Calculate distribution of strain levels."""
        if not strains:
            return None
            
        return {
            "low": sum(1 for s in strains if s < 8),
            "moderate": sum(1 for s in strains if 8 <= s < 14),
            "high": sum(1 for s in strains if s >= 14)
        }

    def _analyze_workout_intensity(self, workouts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze workout intensity distribution."""
        if not workouts:
            return None
            
        intensities = {
            "low": 0,
            "moderate": 0,
            "high": 0
        }
        
        for workout in workouts:
            strain = workout.get('strain', 0)
            if strain < 8:
                intensities["low"] += 1
            elif strain < 14:
                intensities["moderate"] += 1
            else:
                intensities["high"] += 1
                
        return intensities

    def _calculate_recovery_strain_correlation(self) -> float:
        """Calculate correlation between recovery and strain."""
        recovery_scores = []
        strain_scores = []
        
        for day in self.raw_data:
            recovery = day.get('recovery_score')
            strain = day.get('strain_data', {}).get('day_strain')
            
            if recovery is not None and strain is not None:
                recovery_scores.append(recovery)
                strain_scores.append(strain)
        
        if len(recovery_scores) < 2:
            return None
            
        return float(np.corrcoef(recovery_scores, strain_scores)[0, 1])

    def _calculate_sleep_recovery_correlation(self) -> float:
        """Calculate correlation between sleep duration and recovery."""
        sleep_durations = []
        recovery_scores = []
        
        for day in self.raw_data:
            sleep = day.get('sleep_data', {}).get('duration')
            recovery = day.get('recovery_score')
            
            if sleep is not None and recovery is not None:
                sleep_durations.append(sleep)
                recovery_scores.append(recovery)
        
        if len(sleep_durations) < 2:
            return None
            
        return float(np.corrcoef(sleep_durations, recovery_scores)[0, 1])

    def _identify_significant_patterns(self) -> List[str]:
        """Identify significant patterns in the data."""
        patterns = []
        
        # Analyze recovery patterns
        recovery_scores = [day.get('recovery_score') for day in self.raw_data if day.get('recovery_score') is not None]
        if recovery_scores:
            avg_recovery = np.mean(recovery_scores)
            if avg_recovery < 33:
                patterns.append("Consistently low recovery scores indicate potential overtraining")
            elif avg_recovery > 66:
                patterns.append("Strong recovery pattern indicates good adaptation to training load")
        
        # Analyze sleep patterns
        sleep_durations = [day.get('sleep_data', {}).get('duration') for day in self.raw_data if day.get('sleep_data', {}).get('duration') is not None]
        if sleep_durations:
            avg_sleep = np.mean(sleep_durations)
            if avg_sleep < 420:  # Less than 7 hours
                patterns.append("Consistent sleep deficit may be impacting recovery")
            
        # Analyze strain patterns
        strain_scores = [day.get('strain_data', {}).get('day_strain') for day in self.raw_data if day.get('strain_data', {}).get('day_strain') is not None]
        if strain_scores:
            consecutive_high_strain = 0
            for strain in strain_scores:
                if strain > 15:
                    consecutive_high_strain += 1
                else:
                    consecutive_high_strain = 0
                if consecutive_high_strain >= 3:
                    patterns.append("Multiple consecutive days of high strain detected")
                    break
        
        return patterns

    def _generate_focus_areas(self) -> List[str]:
        """Generate recommended focus areas based on the analysis."""
        focus_areas = []
        
        # Analyze recovery scores
        recovery_scores = [day.get('recovery_score') for day in self.raw_data if day.get('recovery_score') is not None]
        if recovery_scores and np.mean(recovery_scores) < 50:
            focus_areas.append("Prioritize recovery strategies and rest")
        
        # Analyze sleep patterns
        sleep_durations = [day.get('sleep_data', {}).get('duration') for day in self.raw_data if day.get('sleep_data', {}).get('duration') is not None]
        if sleep_durations and np.mean(sleep_durations) < 420:
            focus_areas.append("Increase sleep duration to improve recovery")
        
        # Analyze strain balance
        strain_scores = [day.get('strain_data', {}).get('day_strain') for day in self.raw_data if day.get('strain_data', {}).get('day_strain') is not None]
        if strain_scores:
            high_strain_days = sum(1 for s in strain_scores if s > 15)
            if high_strain_days > len(strain_scores) / 2:
                focus_areas.append("Consider incorporating more low-intensity recovery days")
        
        return focus_areas

    def get_processed_data(self) -> Dict[str, Any]:
        """Return processed data, processing it first if necessary."""
        if self.processed_data is None:
            self.process_data()
        return self.processed_data