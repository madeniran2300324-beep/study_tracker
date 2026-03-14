import json
from pathlib import Path
from datetime import datetime

# ============================================
# BASIC DATA OPERATIONS
# ============================================

def load_data():
    """Load data from JSON file"""
    data_file = Path("data.json")
    
    if not data_file.exists():
        return get_empty_schema()
    
    try:
        with open(data_file, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("Error: Corrupted data file. Creating backup...")
        # Backup corrupted file
        data_file.rename("data_corrupted.json")
        return get_empty_schema()

def get_empty_schema():
    """Return empty schema structure"""
    return {
        "courses": [],
        "study_sessions": [],
        "weekly_schedule": [],
        "exam_confidence": [],
        "metadata": {
            "version": "1.0",
            "last_updated": datetime.now().isoformat().replace('+00:00', 'Z')
        }
    }

def save_data(data):
    """Save data with atomic write to prevent corruption"""
    data_file = Path("data.json")
    temp_file = data_file.with_suffix(".tmp")
    
    # Update metadata timestamp
    data["metadata"]["last_updated"] = datetime.now().isoformat().replace('+00:00', 'Z')
    
    # Write to temporary file first
    with open(temp_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    # Atomic rename (prevents corruption if program crashes)
    temp_file.replace(data_file)
    print("✓ Data saved successfully")

def generate_id(prefix, existing_ids):
    """Generate unique ID with given prefix"""
    counter = 1
    while f"{prefix}_{counter}" in existing_ids:
        counter += 1
    return f"{prefix}_{counter}"

def reset_database():
    """Clear all data and start fresh"""
    data_file = Path("data.json")
    if data_file.exists():
        # Backup old data
        backup_name = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data_file.rename(backup_name)
        print(f"✓ Backed up old data to {backup_name}")
    
    # Create fresh schema
    save_data(get_empty_schema())
    print("✓ Database reset complete\n")

# ============================================
# COURSE MANAGER
# ============================================

class CourseManager:
    """Manage course operations"""
    
    @staticmethod
    def add_course(name, units, schedule, color="#4CAF50"):
        """Add a new course"""
        data = load_data()
        
        # Generate unique ID
        existing_ids = [c["id"] for c in data["courses"]]
        course_id = generate_id("course", existing_ids)
        
        # Validate inputs
        if not name or not name.strip():
            raise ValueError("Course name cannot be empty")
        if units <= 0:
            raise ValueError("Units must be positive")
        
        # Create course object
        new_course = {
            "id": course_id,
            "name": name.strip(),
            "units": units,
            "schedule": schedule,
            "color": color,
            "created_at": datetime.now().isoformat().replace('+00:00', 'Z')
        }
        
        # Add and save
        data["courses"].append(new_course)
        save_data(data)
        
        print(f"✓ Added course: {name} (ID: {course_id})")
        return course_id
    
    @staticmethod
    def get_course(course_id):
        """Get a specific course by ID"""
        data = load_data()
        for course in data["courses"]:
            if course["id"] == course_id:
                return course
        return None
    
    @staticmethod
    def list_courses():
        """Get all courses"""
        data = load_data()
        return data["courses"]
    
    @staticmethod
    def update_course(course_id, **updates):
        """Update course fields"""
        data = load_data()
        
        for course in data["courses"]:
            if course["id"] == course_id:
                # Update allowed fields
                for key, value in updates.items():
                    if key in ["name", "units", "schedule", "color"]:
                        course[key] = value
                
                save_data(data)
                print(f"✓ Updated course: {course_id}")
                return True
        
        print(f"✗ Course not found: {course_id}")
        return False
    
    @staticmethod
    def delete_course(course_id):
        """Delete a course"""
        data = load_data()
        
        # Find and remove course
        original_count = len(data["courses"])
        data["courses"] = [c for c in data["courses"] if c["id"] != course_id]
        
        if len(data["courses"]) < original_count:
            # Also delete related study sessions
            data["study_sessions"] = [
                s for s in data["study_sessions"] 
                if s["course_id"] != course_id
            ]
            
            save_data(data)
            print(f"✓ Deleted course: {course_id}")
            return True
        
        print(f"✗ Course not found: {course_id}")
        return False

# ============================================
# STUDY LOGGER
# ============================================

class StudyLogger:
    """Log and manage study sessions"""
    
    @staticmethod
    def log_session(course_id, date, duration_minutes, notes=""):
        """Log a study session"""
        data = load_data()
        
        # Validate course exists
        course_exists = any(c["id"] == course_id for c in data["courses"])
        if not course_exists:
            raise ValueError(f"Course {course_id} does not exist")
        
        # Validate duration
        if duration_minutes <= 0:
            raise ValueError("Duration must be positive")
        
        # Generate ID
        existing_ids = [s["id"] for s in data["study_sessions"]]
        session_id = generate_id("session", existing_ids)
        
        # Create session
        new_session = {
            "id": session_id,
            "course_id": course_id,
            "date": date,
            "duration_minutes": duration_minutes,
            "notes": notes.strip(),
            "created_at": datetime.now().isoformat().replace('+00:00', 'Z')

        }
        
        # Add and save
        data["study_sessions"].append(new_session)
        save_data(data)
        
        print(f"✓ Logged {duration_minutes} minutes for {course_id}")
        return session_id
    
    @staticmethod
    def get_sessions_by_course(course_id):
        """Get all sessions for a specific course"""
        data = load_data()
        return [s for s in data["study_sessions"] if s["course_id"] == course_id]
    
    @staticmethod
    def get_sessions_by_date(date):
        """Get all sessions for a specific date"""
        data = load_data()
        return [s for s in data["study_sessions"] if s["date"] == date]

# ============================================
# ANALYTICS ENGINE
# ============================================
class AnalyticsEngine:
    """Calculate statistics and auto-generate confidence levels"""
    
    @staticmethod
    def get_total_study_hours():
        """Get total study time across all courses"""
        data = load_data()
        total_minutes = sum(s["duration_minutes"] for s in data["study_sessions"])
        return round(total_minutes / 60, 2)
    
    @staticmethod
    def get_hours_by_course(course_id):
        """Get total study hours for a specific course"""
        data = load_data()
        sessions = [s for s in data["study_sessions"] if s["course_id"] == course_id]
        total_minutes = sum(s["duration_minutes"] for s in sessions)
        return round(total_minutes / 60, 2)
    
    @staticmethod
    def get_study_consistency(course_id, days=30):
        """Calculate how consistently a course has been studied"""
        from datetime import datetime, timedelta
        
        data = load_data()
        sessions = [s for s in data["study_sessions"] if s["course_id"] == course_id]
        
        if not sessions:
            return 0.0
        
        # Get unique study dates
        study_dates = set(s["date"] for s in sessions)
        
        # Calculate consistency: (days studied / days available)
        consistency = len(study_dates) / days
        return min(consistency, 1.0)  # Cap at 1.0 (100%)
    
    @staticmethod
    def calculate_confidence_level(course_id):
        """
        Auto-generate confidence level based on study patterns
        Returns a score from 1.0 to 5.0
        
        Algorithm:
        - 40% weight: Hours studied vs expected hours
        - 40% weight: Study consistency (frequency)
        - 20% weight: Recency (recent sessions weighted higher)
        """
        from datetime import datetime, timedelta
        
        data = load_data()
        
        # Get course and sessions
        course = CourseManager.get_course(course_id)
        if not course:
            return 1.0
        
        sessions = [s for s in data["study_sessions"] if s["course_id"] == course_id]
        
        if not sessions:
            return 1.0  # Minimum confidence if no study
        
        # METRIC 1: Hours Ratio (40% weight)
        # Expected: 2-3 hours per unit per week
        expected_hours_per_week = course["units"] * 2.5
        actual_hours = AnalyticsEngine.get_hours_by_course(course_id)
        # Assume 4 weeks of data for now
        hours_ratio = min(actual_hours / (expected_hours_per_week * 4), 1.0)
        
        # METRIC 2: Consistency (40% weight)
        consistency = AnalyticsEngine.get_study_consistency(course_id, days=30)
        
        # METRIC 3: Recency (20% weight)
        # Check if studied in last 7 days
        today = datetime.now().date()
        recent_sessions = [
            s for s in sessions 
            if (today - datetime.fromisoformat(s["date"]).date()).days <= 7
        ]
        recency = 1.0 if recent_sessions else 0.3
        
        # Calculate weighted score
        raw_score = (hours_ratio * 0.4) + (consistency * 0.4) + (recency * 0.2)
        
        # Scale to 1-5 range
        confidence = 1.0 + (raw_score * 4.0)
        
        return round(confidence, 2)
    
    @staticmethod
    def update_all_confidence_levels():
        """Recalculate and save confidence levels for all courses"""
        data = load_data()
        
        # Clear existing confidence data
        data["exam_confidence"] = []
        
        # Calculate for each course
        for course in data["courses"]:
            confidence = AnalyticsEngine.calculate_confidence_level(course["id"])
            
            data["exam_confidence"].append({
                "course_id": course["id"],
                "confidence_level": confidence,
                "updated_at": datetime.now().isoformat().replace('+00:00', 'Z')
            })
        
        save_data(data)
        print("✓ Updated confidence levels for all courses")
    
    @staticmethod
    def get_underperforming_courses(threshold=0.75):
        """
        Identify courses receiving insufficient attention
        Returns courses where actual study < 75% of expected
        """
        data = load_data()
        underperforming = []
        
        for course in data["courses"]:
            expected_hours = course["units"] * 2.5 * 4  # 4 weeks
            actual_hours = AnalyticsEngine.get_hours_by_course(course["id"])
            
            if actual_hours < (expected_hours * threshold):
                underperforming.append({
                    "course": course["name"],
                    "course_id": course["id"],
                    "expected_hours": round(expected_hours, 2),
                    "actual_hours": actual_hours,
                    "deficit": round(expected_hours - actual_hours, 2)
                })
        
        return underperforming
    
    @staticmethod
    def get_course_summary(course_id):
        """Get complete analytics summary for a course"""
        course = CourseManager.get_course(course_id)
        if not course:
            return None
        
        sessions = StudyLogger.get_sessions_by_course(course_id)
        
        return {
            "name": course["name"],
            "units": course["units"],
            "total_hours": AnalyticsEngine.get_hours_by_course(course_id),
            "total_sessions": len(sessions),
            "consistency": round(AnalyticsEngine.get_study_consistency(course_id) * 100, 1),
            "confidence_level": AnalyticsEngine.calculate_confidence_level(course_id)
        }
    
# ============================================
# SCHEDULE GENERATOR - Complete Implementation
# ============================================

from datetime import datetime, time

class ScheduleGenerator:
    """
    Generate weekly study schedules based on course weights
    
    This class creates an optimal study timetable that:
    - Allocates time proportionally to course units
    - Avoids conflicts with class times
    - Distributes study sessions across the week
    - Creates 2-hour study blocks for effectiveness
    """
    
    @staticmethod
    def generate_weekly_schedule(total_study_hours=20, session_duration=2):
        """
        Create a complete weekly study schedule
        
        Args:
            total_study_hours: Total hours available for study per week (default: 20)
            session_duration: Length of each study session in hours (default: 2)
            
        Returns:
            List of schedule entries ready to be saved to data.json
            
        Example:
            schedule = ScheduleGenerator.generate_weekly_schedule(20, 2)
            # Returns: [
            #   {"id": "sched_1", "day": "Monday", "time_slot": "14:00-16:00", 
            #    "course_id": "course_1", "type": "study"},
            #   ...
            # ]
        """
        data = load_data()
        courses = data["courses"]
        
        if not courses:
            print("No courses found. Add courses first.")
            return []
        
        # Step 1: Calculate total units across all courses
        total_units = sum(c["units"] for c in courses)
        print(f"\n📊 Total units across all courses: {total_units}")
        
        # Step 2: Calculate how many hours each course should get
        course_allocations = []
        for course in courses:
            # Weighted allocation: course gets (its units / total units) × total hours
            allocated_hours = (course["units"] / total_units) * total_study_hours
            num_sessions = int(allocated_hours / session_duration)  # Round down
            
            course_allocations.append({
                "course": course,
                "allocated_hours": allocated_hours,
                "num_sessions": num_sessions
            })
            
            print(f"  {course['name']}: {allocated_hours:.1f} hours ({num_sessions} sessions)")
        
        # Step 3: Create schedule entries
        schedule_entries = []
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", 
                       "Friday", "Saturday", "Sunday"]
        
        # Start time for study sessions (2 PM = 14:00)
        base_start_hour = 14
        
        # Distribute sessions across the week
        for allocation in course_allocations:
            course = allocation["course"]
            sessions_needed = allocation["num_sessions"]
            sessions_created = 0
            day_index = 0
            
            # Try to create sessions for this course
            while sessions_created < sessions_needed and day_index < len(days_of_week):
                day = days_of_week[day_index]
                
                # Calculate time slot for this session
                # Space out sessions: first course gets 14:00, next gets 16:00, etc.
                hour_offset = sessions_created * session_duration
                start_hour = base_start_hour + hour_offset
                end_hour = start_hour + session_duration
                
                # Make sure we don't go past 10 PM (22:00)
                if end_hour > 22:
                    day_index += 1
                    sessions_created = 0
                    continue
                
                # Check if this time conflicts with class schedule
                time_slot = f"{start_hour:02d}:00-{end_hour:02d}:00"
                
                if not ScheduleGenerator._has_class_conflict(course, day, start_hour, end_hour):
                    # No conflict - create the study session
                    entry_id = f"sched_{len(schedule_entries) + 1}"
                    
                    schedule_entries.append({
                        "id": entry_id,
                        "day": day,
                        "time_slot": time_slot,
                        "course_id": course["id"],
                        "type": "study"
                    })
                    
                    sessions_created += 1
                    print(f"    ✓ Created: {course['name']} on {day} at {time_slot}")
                
                # Move to next potential time slot
                if sessions_created < sessions_needed:
                    day_index += 1
        
        print(f"\n✓ Generated {len(schedule_entries)} study sessions")
        return schedule_entries
    
    @staticmethod
    def _has_class_conflict(course, day, start_hour, end_hour):
        """
        Check if a proposed study time conflicts with class time
        
        Args:
            course: The course dict
            day: Day of week (e.g., "Monday")
            start_hour: Start hour (24-hour format, e.g., 14)
            end_hour: End hour (24-hour format, e.g., 16)
            
        Returns:
            True if there's a conflict, False otherwise
        """
        for class_time in course.get("schedule", []):
            # Check if this class is on the same day
            if class_time["day"] == day:
                # Parse class start and end times
                class_start = int(class_time["start"].split(":")[0])
                class_end = int(class_time["end"].split(":")[0])
                
                # Check for overlap
                # Overlap if: study_start < class_end AND study_end > class_start
                if start_hour < class_end and end_hour > class_start:
                    return True
        
        return False
    
    @staticmethod
    def save_schedule_to_db(schedule_entries):
        """
        Save generated schedule to data.json
        
        Args:
            schedule_entries: List of schedule dicts from generate_weekly_schedule()
        """
        data = load_data()
        
        # Clear old schedule
        data["weekly_schedule"] = []
        
        # Add class times to schedule first
        for course in data["courses"]:
            for class_time in course.get("schedule", []):
                entry_id = f"class_{course['id']}_{class_time['day']}"
                data["weekly_schedule"].append({
                    "id": entry_id,
                    "day": class_time["day"],
                    "time_slot": f"{class_time['start']}-{class_time['end']}",
                    "course_id": course["id"],
                    "type": "class"
                })
        
        # Add generated study sessions
        data["weekly_schedule"].extend(schedule_entries)
        
        save_data(data)
        print(f"✓ Saved {len(schedule_entries)} study sessions + class times to database")
    
    @staticmethod
    def regenerate_full_schedule(total_study_hours=20):
        """
        Convenience method to generate and save schedule in one call
        
        Args:
            total_study_hours: Hours available for study per week
        """
        print("🔄 Generating new weekly schedule...")
        schedule = ScheduleGenerator.generate_weekly_schedule(total_study_hours)
        
        if schedule:
            ScheduleGenerator.save_schedule_to_db(schedule)
            return True
        else:
            print("✗ Failed to generate schedule")
            return False
    
if __name__ == "__main__":
    print("\n" + "="*50)
    print("TESTING STUDY TRACKER DATA LAYER")
    print("="*50 + "\n")
    
    # Reset database before testing
    reset_database()
    
    # Test 1: Add courses
    print("TEST 1: Adding courses...")
    course1 = CourseManager.add_course(
        "Linear Algebra",
        3,
        [
            {"day": "Monday", "start": "09:00", "end": "10:30"},
            {"day": "Wednesday", "start": "09:00", "end": "10:30"}
        ],
        "#4CAF50"
    )
    
    course2 = CourseManager.add_course(
        "Data Structures",
        4,
        [
            {"day": "Tuesday", "start": "14:00", "end": "16:00"},
            {"day": "Thursday", "start": "14:00", "end": "16:00"}
        ],
        "#2196F3"
    )
    
    # Test 2: List courses
    print("\nTEST 2: Listing courses...")
    courses = CourseManager.list_courses()
    for course in courses:
        print(f"  - {course['name']} ({course['units']} units)")
    
    # Test 3: Log study sessions (MORE DATA FOR BETTER ANALYTICS)
    print("\nTEST 3: Logging study sessions...")
    # Linear Algebra - good study pattern
    StudyLogger.log_session(course1, "2026-03-08", 90, "Chapter 1")
    StudyLogger.log_session(course1, "2026-03-10", 120, "Chapter 2")
    StudyLogger.log_session(course1, "2026-03-12", 90, "Practice problems")
    StudyLogger.log_session(course1, "2026-03-14", 90, "Eigenvalues review")
    
    # Data Structures - less consistent
    StudyLogger.log_session(course2, "2026-03-09", 60, "Binary trees intro")
    StudyLogger.log_session(course2, "2026-03-14", 120, "BST implementation")
    
    # Test 4: Get sessions by course
    print("\nTEST 4: Getting sessions...")
    sessions = StudyLogger.get_sessions_by_course(course1)
    print(f"  Found {len(sessions)} session(s) for Linear Algebra")
    
    # Test 5: Update course
    print("\nTEST 5: Updating course...")
    CourseManager.update_course(course1, name="Advanced Linear Algebra")
    
    # NEW TEST 6: Analytics - Total Hours
    print("\nTEST 6: Analytics - Total Study Hours...")
    total_hours = AnalyticsEngine.get_total_study_hours()
    print(f"  Total study time: {total_hours} hours")
    
    # NEW TEST 7: Analytics - Hours by Course
    print("\nTEST 7: Analytics - Hours by Course...")
    for course_id in [course1, course2]:
        course = CourseManager.get_course(course_id)
        hours = AnalyticsEngine.get_hours_by_course(course_id)
        print(f"  {course['name']}: {hours} hours")
    
    # NEW TEST 8: Auto-Generate Confidence Levels
    print("\nTEST 8: Auto-Generating Confidence Levels...")
    AnalyticsEngine.update_all_confidence_levels()
    
    data = load_data()
    for conf in data["exam_confidence"]:
        course = CourseManager.get_course(conf["course_id"])
        print(f"  {course['name']}: {conf['confidence_level']}/5.0")
    
    # NEW TEST 9: Course Summary
    print("\nTEST 9: Complete Course Summary...")
    summary = AnalyticsEngine.get_course_summary(course1)
    print(f"  Course: {summary['name']}")
    print(f"  Total Hours: {summary['total_hours']}")
    print(f"  Sessions: {summary['total_sessions']}")
    print(f"  Consistency: {summary['consistency']}%")
    print(f"  Confidence: {summary['confidence_level']}/5.0")
    
    # NEW TEST 10: Underperforming Courses
    print("\nTEST 10: Detecting Underperforming Courses...")
    underperforming = AnalyticsEngine.get_underperforming_courses()
    if underperforming:
        for course in underperforming:
            print(f"  ⚠️  {course['course']}: {course['actual_hours']}h / {course['expected_hours']}h expected")
    else:
        print("  ✓ All courses on track!")

     # NEW TEST 11: Generate Weekly Schedule
    print("\nTEST 11: Generating Weekly Schedule...")
    success = ScheduleGenerator.regenerate_full_schedule(total_study_hours=20)
    
    if success:
        data = load_data()
        study_sessions = [s for s in data["weekly_schedule"] if s["type"] == "study"]
        class_times = [s for s in data["weekly_schedule"] if s["type"] == "class"]
        print(f"  ✓ Created {len(study_sessions)} study sessions")
        print(f"  ✓ Added {len(class_times)} class times")
        
        # Show a sample
        if study_sessions:
            sample = study_sessions[0]
            course = CourseManager.get_course(sample["course_id"])
            print(f"  Example: {course['name']} on {sample['day']} at {sample['time_slot']}")
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETED!")
    print("="*50)
    print("\nCheck your data.json file to see the results.")

   