from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import pandas as pd
from whoop import WhoopClient
import logging
import traceback
import numpy as np
import pytz
import concurrent.futures
import json
from backend.llm_backend import perform_combined_vector_searches, process_rag_response

load_dotenv()

app = Flask(__name__)

# Configure CORS to allow requests from your React frontend
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class WhoopService:
    def __init__(self):
        username = os.getenv("WHOOP_USERNAME")
        password = os.getenv("WHOOP_PASSWORD")
        
        if not username or not password:
            raise ValueError("WHOOP_USERNAME and WHOOP_PASSWORD must be set in .env file")
        
        self.client = WhoopClient(username, password)
        self.sport_names = self.get_sport_names()

    def get_sport_names(self):
        return {
            -1: "Activity", 0: "Running", 1: "Cycling", 16: "Baseball", 17: "Basketball",
            18: "Rowing", 19: "Fencing", 20: "Field Hockey", 21: "Football", 22: "Golf",
            24: "Ice Hockey", 25: "Lacrosse", 27: "Rugby", 28: "Sailing", 29: "Skiing",
            30: "Soccer", 31: "Softball", 32: "Squash", 33: "Swimming", 34: "Tennis",
            35: "Track & Field", 36: "Volleyball", 37: "Water Polo", 38: "Wrestling",
            39: "Boxing", 42: "Dance", 43: "Pilates", 44: "Yoga", 45: "Weightlifting",
            47: "Cross Country Skiing", 48: "Functional Fitness", 49: "Duathlon",
            51: "Gymnastics", 52: "Hiking/Rucking", 53: "Horseback Riding", 55: "Kayaking",
            56: "Martial Arts", 57: "Mountain Biking", 59: "Powerlifting", 60: "Rock Climbing",
            61: "Paddleboarding", 62: "Triathlon", 63: "Walking", 64: "Surfing",
            65: "Elliptical", 66: "Stairmaster", 70: "Meditation", 71: "Other",
            73: "Diving", 74: "Operations - Tactical", 75: "Operations - Medical",
            76: "Operations - Flying", 77: "Operations - Water", 82: "Ultimate",
            83: "Climber", 84: "Jumping Rope", 85: "Australian Football", 86: "Skateboarding",
            87: "Coaching", 88: "Ice Bath", 89: "Commuting", 90: "Gaming",
            91: "Snowboarding", 92: "Motocross", 93: "Caddying", 94: "Obstacle Course Racing",
            95: "Motor Racing", 96: "HIIT", 97: "Spin", 98: "Jiu Jitsu", 99: "Manual Labor",
            100: "Cricket", 101: "Pickleball", 102: "Inline Skating", 103: "Box Fitness",
            104: "Spikeball", 105: "Wheelchair Pushing", 106: "Paddle Tennis", 107: "Barre",
            108: "Stage Performance", 109: "High Stress Work", 110: "Parkour",
            111: "Gaelic Football", 112: "Hurling/Camogie", 113: "Circus Arts",
            121: "Massage Therapy", 123: "Strength Trainer", 125: "Watching Sports",
            126: "Assault Bike", 127: "Kickboxing", 128: "Stretching", 230: "Table Tennis",
            231: "Badminton", 232: "Netball", 233: "Sauna", 234: "Disc Golf",
            235: "Yard Work", 236: "Air Compression", 237: "Percussive Massage",
            238: "Paintball", 239: "Ice Skating", 240: "Handball"
        }

    def get_last_7_days_summary(self, start_date=None, end_date=None):
        # Use UTC timezone for consistent calculations
        tz = pytz.timezone('UTC')
        local_tz = pytz.timezone('America/New_York')
        
        if start_date:
            end_date = start_date + timedelta(days=7)
        else:
            # Use default last 7 days
            end_date = datetime.now(tz).date()
            start_date = end_date - timedelta(days=7)
        
        app.logger.debug(f"Start date: {start_date}, End date: {end_date} (UTC)")
        
        # Fetch data from Whoop API
        recovery_data = self.client.get_recovery_collection(start_date.isoformat(), end_date.isoformat())
        sleep_data = self.client.get_sleep_collection(start_date.isoformat(), end_date.isoformat())
        cycle_data = self.client.get_cycle_collection(start_date.isoformat(), end_date.isoformat())
        workout_data = self.client.get_workout_collection(start_date.isoformat(), end_date.isoformat())
        
        # Normalize and process data
        recovery_df = pd.json_normalize(recovery_data)
        sleep_df = pd.json_normalize(sleep_data)
        cycle_df = pd.json_normalize(cycle_data)
        workout_df = pd.json_normalize(workout_data)
        
        # Process dates for each metric, handling missing fields and timezones
        def safe_convert_timezone(dt_series, target_tz):
            return pd.to_datetime(dt_series).apply(
                lambda dt: dt.tz_convert(target_tz) if dt.tzinfo else dt.tz_localize('UTC').tz_convert(target_tz)
            )

        recovery_df['timestamp'] = safe_convert_timezone(recovery_df.get('created_at'), local_tz)
        sleep_df['start_time'] = safe_convert_timezone(sleep_df.get('start'), local_tz)
        sleep_df['end_time'] = safe_convert_timezone(sleep_df.get('end'), local_tz)
        cycle_df['timestamp'] = safe_convert_timezone(cycle_df.get('start'), local_tz)
        
        # Handle workout data if available
        if not workout_df.empty and 'start' in workout_df.columns:
            workout_df['start_time'] = safe_convert_timezone(workout_df['start'], local_tz)
            workout_df['end_time'] = safe_convert_timezone(workout_df['end'], local_tz)
            workout_df['date'] = workout_df['start_time'].dt.date
            workout_summary = workout_df.groupby('date').apply(self.aggregate_workouts).reset_index()
        else:
            app.logger.warning("No workout data or 'start' column missing in workout data")
            workout_summary = pd.DataFrame(columns=['date', 'workouts'])
        
        # Assign dates based on local timezone
        recovery_df['date'] = recovery_df['timestamp'].dt.date
        sleep_df['date'] = sleep_df['start_time'].dt.date
        cycle_df['date'] = cycle_df['timestamp'].dt.date
        
        # Calculate sleep duration in minutes, considering overlaps and cross-midnight sleeps
        def calculate_daily_sleep(sleep_df):
            sleep_data = []
            for date, group in sleep_df.groupby('date'):
                sorted_sleeps = group.sort_values('start_time')
                total_sleep = 0
                last_end = None
                sleep_metrics = {
                    'disturbance_count': 0,
                    'efficiency_percentage': 0,
                    'awake_time': 0,
                    'light_sleep_time': 0,
                    'slow_wave_sleep_time': 0,
                    'rem_sleep_time': 0,
                    'sleep_cycle_count': 0
                }
                for _, sleep in sorted_sleeps.iterrows():
                    start = sleep['start_time']
                    end = sleep['end_time']
                    if last_end is None or start > last_end:
                        total_sleep += (end - start).total_seconds() / 60
                    elif end > last_end:
                        total_sleep += (end - last_end).total_seconds() / 60
                    last_end = max(end, last_end) if last_end else end
                    
                    # Aggregate sleep metrics
                    sleep_metrics['disturbance_count'] += sleep.get('score.stage_summary.disturbance_count', 0)
                    sleep_metrics['efficiency_percentage'] = max(sleep_metrics['efficiency_percentage'], sleep.get('score.sleep_efficiency_percentage', 0))
                    sleep_metrics['awake_time'] += sleep.get('score.stage_summary.total_awake_time_milli', 0) / 60000  # Convert to minutes
                    sleep_metrics['light_sleep_time'] += sleep.get('score.stage_summary.total_light_sleep_time_milli', 0) / 60000
                    sleep_metrics['slow_wave_sleep_time'] += sleep.get('score.stage_summary.total_slow_wave_sleep_time_milli', 0) / 60000
                    sleep_metrics['rem_sleep_time'] += sleep.get('score.stage_summary.total_rem_sleep_time_milli', 0) / 60000
                    sleep_metrics['sleep_cycle_count'] += sleep.get('score.stage_summary.sleep_cycle_count', 0)
                
                # Check for sleep that started the previous day
                previous_day = date - timedelta(days=1)
                previous_sleeps = sleep_df[sleep_df['date'] == previous_day]
                for _, sleep in previous_sleeps.iterrows():
                    if sleep['end_time'].date() == date:
                        sleep_in_this_day = (sleep['end_time'] - sleep['end_time'].replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 60
                        total_sleep += sleep_in_this_day

                sleep_data.append({
                    'date': date,
                    'sleep_duration': total_sleep,
                    **sleep_metrics
                })
            return pd.DataFrame(sleep_data)

        sleep_summary = calculate_daily_sleep(sleep_df)
        sleep_summary.columns = ['date', 'sleep_duration', 'disturbance_count', 'efficiency_percentage', 'awake_time', 'light_sleep_time', 'slow_wave_sleep_time', 'rem_sleep_time', 'sleep_cycle_count']
        
        # Aggregate data by date
        recovery_summary = recovery_df.groupby('date')['score.recovery_score'].last().reset_index()
        strain_summary = cycle_df.groupby('date')['score.strain'].last().reset_index()
        
        # Create a base date range for the specified 7 days
        date_range = pd.date_range(start=start_date, end=end_date - timedelta(days=1), freq='D').date
        
        # Base DataFrame to ensure all days are included
        base_df = pd.DataFrame({'date': date_range})
        
        # Merge all summaries to base DataFrame
        summary = base_df.merge(recovery_summary, on='date', how='left')
        summary = summary.merge(sleep_summary, on='date', how='left')
        summary = summary.merge(strain_summary, on='date', how='left')
        summary = summary.merge(workout_summary, on='date', how='left')
        
        # Ensure that missing columns are added
        for col in ['score.recovery_score', 'sleep_duration', 'score.strain', 'workouts']:
            if col not in summary.columns:
                summary[col] = None
        
        # Now fill NaN values with appropriate defaults
        summary['score.recovery_score'] = summary['score.recovery_score'].where(pd.notnull, None)
        summary['sleep_duration'] = summary['sleep_duration'].where(pd.notnull, None)
        summary['score.strain'] = summary['score.strain'].where(pd.notnull, None)
        summary['workouts'] = summary['workouts'].apply(lambda x: x if isinstance(x, list) else [])
        
        # Format and finalize summary
        formatted_summary = []
        for day in summary.to_dict('records'):
            formatted_summary.append({
                'date': day['date'].isoformat(),
                'recovery_score': round(day['score.recovery_score'], 2) if pd.notnull(day['score.recovery_score']) else None,
                'sleep_data': {
                    'duration': round(day['sleep_duration']) if pd.notnull(day['sleep_duration']) else None,
                    'metrics': {
                        'disturbance_count': round(day['disturbance_count']) if pd.notnull(day['disturbance_count']) else None,
                        'efficiency_percentage': round(day['efficiency_percentage'], 2) if pd.notnull(day['efficiency_percentage']) else None,
                        'awake_time': round(day['awake_time']) if pd.notnull(day['awake_time']) else None,
                        'light_sleep_time': round(day['light_sleep_time']) if pd.notnull(day['light_sleep_time']) else None,
                        'slow_wave_sleep_time': round(day['slow_wave_sleep_time']) if pd.notnull(day['slow_wave_sleep_time']) else None,
                        'rem_sleep_time': round(day['rem_sleep_time']) if pd.notnull(day['rem_sleep_time']) else None,
                        'sleep_cycle_count': round(day['sleep_cycle_count']) if pd.notnull(day['sleep_cycle_count']) else None
                    }
                },
                'strain_data': {
                    'day_strain': round(day['score.strain'], 2) if pd.notnull(day['score.strain']) else None,
                    'workouts': day['workouts'] if isinstance(day['workouts'], list) else []
                }
            })
        
        # Sort the formatted_summary in descending order by date (22nd to 16th)
        formatted_summary.sort(key=lambda x: x['date'], reverse=True)
        
        app.logger.debug(f"Formatted summary (sorted): {formatted_summary}")
        return formatted_summary

    def aggregate_workouts(self, group):
        workouts = []
        for _, workout in group.iterrows():
            if pd.notnull(workout.get('start_time')) and pd.notnull(workout.get('end_time')):
                duration_minutes = (workout['end_time'] - workout['start_time']).total_seconds() / 60
            else:
                duration_minutes = None
            workout_info = {
                'sport': self.sport_names.get(workout.get('sport_id', -1), 'Unknown'),
                'strain': round(workout['score.strain'], 2) if pd.notnull(workout.get('score.strain')) else None,
                'average_hr': workout['score.average_heart_rate'] if pd.notnull(workout.get('score.average_heart_rate')) else None,
                'max_hr': workout['score.max_heart_rate'] if pd.notnull(workout.get('score.max_heart_rate')) else None,
                'duration': round(duration_minutes) if duration_minutes is not None else None,
                'zone_duration': {
                    'zone_zero_milli': workout.get('score.zone_duration.zone_zero_milli'),
                    'zone_one_milli': workout.get('score.zone_duration.zone_one_milli'),
                    'zone_two_milli': workout.get('score.zone_duration.zone_two_milli'),
                    'zone_three_milli': workout.get('score.zone_duration.zone_three_milli'),
                    'zone_four_milli': workout.get('score.zone_duration.zone_four_milli'),
                    'zone_five_milli': workout.get('score.zone_duration.zone_five_milli'),
                }
            }
            workouts.append(workout_info)
        return pd.Series({'workouts': workouts})

whoop_service = WhoopService()

@app.route('/api/whoop/summary', methods=['GET'])
def get_whoop_summary():
    logging.debug("Received request for /api/whoop/summary")
    try:
        start_date = request.args.get('start_date')
        today = datetime.now(pytz.UTC).date()
        
        if start_date:
            # Parse the provided start date
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            # Ensure we're not requesting future data
            if start_date > today:
                start_date = today - timedelta(days=6)  # Default to last 7 days
        else:
            # Default to last 7 days
            start_date = today - timedelta(days=6)
        
        end_date = start_date + timedelta(days=7)
        if end_date > today:
            end_date = today
            start_date = end_date - timedelta(days=6)  # Adjust start date to maintain 7-day window
            
        app.logger.debug(f"Adjusted Start date: {start_date}, End date: {end_date} (UTC)")
        summary = whoop_service.get_last_7_days_summary(start_date, end_date)
        logging.debug("Successfully generated summary")
        return jsonify(summary)
    except Exception as e:
        logging.error(f"Error in get_whoop_summary: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_query = data.get('query')
        whoop_data = data.get('whoopData')
        conversation_history = data.get('conversationHistory', [])
        
        logging.info(f"Received chat request with query: {user_query}")
        
        # Format conversation history
        formatted_history = ""
        if conversation_history:
            formatted_history = "Previous conversation:\n"
            for msg in conversation_history[:-1]:
                if msg.get('type') == 'user':
                    formatted_history += f"User: {msg.get('text', '')}\n"
                elif msg.get('type') == 'ai':
                    formatted_history += f"Assistant: {msg.get('response', '')}\n"
            formatted_history += "\nCurrent question:\n"
        
        # Get combined context from vector searches
        combined_context = perform_combined_vector_searches(user_query)
        
        # Simply pass the raw Whoop data as JSON
        whoop_context = ""
        if whoop_data:
            whoop_context = f"User's Whoop Data (JSON format):\n{json.dumps(whoop_data, indent=2)}\n"
        
        # Combine contexts
        full_context = f"{formatted_history}\n{combined_context}\n\n{whoop_context}"
        response = process_rag_response(user_query, full_context)
        
        return jsonify({'response': response})
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        logging.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
