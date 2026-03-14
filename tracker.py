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
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }
    }

def save_data(data):
    """Save data with atomic write to prevent corruption"""
    data_file = Path("data.json")
    temp_file = data_file.with_suffix(".tmp")
    
    # Update metadata timestamp
    data["metadata"]["last_updated"] = datetime.utcnow().isoformat() + "Z"
    
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
            "created_at": datetime.utcnow().isoformat() + "Z"
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
            "created_at": datetime.utcnow().isoformat() + "Z"
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
# TESTING CODE
# ============================================

if __name__ == "__main__":
    print("\n" + "="*50)
    print("TESTING STUDY TRACKER DATA LAYER")
    print("="*50 + "\n")
    
    #Reset database before testing
    reset_database()

    # Test 1: Add courses
    print("TEST 1: Adding courses...")
    course1 = CourseManager.add_course(
        "Computer Organisation and Architecture",
        2,
        [
            {"day": "Monday", "start": "12:00", "end": "14:00"},
        ],
        "#4CAF50"
    )
    
    course2 = CourseManager.add_course(
        "Electric Circuit Theory 1",
        2,
        [
            {"day": "Monday", "start": "08:00", "end": "09:00"},
            {"day": "Monday", "start": "10:00", "end": "12:00"}
        ],
        "#2196F3"
    )
    
    # Test 2: List courses
    print("\nTEST 2: Listing courses...")
    courses = CourseManager.list_courses()
    for course in courses:
        print(f"  - {course['name']} ({course['units']} units)")
    
    # Test 3: Log study sessions
    print("\nTEST 3: Logging study sessions...")
    StudyLogger.log_session(course1, "2025-03-07", 90, "Reviewed Von Neumann architecture")
    StudyLogger.log_session(course2, "2025-03-07", 120, "Practice RL AND RC circuit problems")
    
    # Test 4: Get sessions by course
    print("\nTEST 4: Getting sessions...")
    sessions = StudyLogger.get_sessions_by_course(course1)
    print(f"  Found {len(sessions)} session(s) for Computer Organisation and Architecture 2")
    
    # Test 5: Update course
    print("\nTEST 5: Updating course...")
    CourseManager.update_course(course1, name="Advanced Linear Algebra")
    
    print("\n" + "="*50)
    print("ALL TESTS COMPLETED!")
    print("="*50)
    print("\nCheck your data.json file to see the results.")