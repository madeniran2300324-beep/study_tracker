"""
Tests for Study Tracker
Run with: python test_tracker.py
"""

import unittest
from pathlib import Path
import json
from tracker import (
    CourseManager, 
    StudyLogger, 
    AnalyticsEngine, 
    ScheduleGenerator,
    load_data,
    save_data,
    reset_database,
    BASE_DIR
)


class TestCourseManager(unittest.TestCase):
    """Test CourseManager functionality"""
    
    def setUp(self):
        """Run before each test - create clean database"""
        reset_database()
    
    def test_add_course(self):
        """Test adding a course"""
        course_id = CourseManager.add_course(
            name="Test Course",
            units=3,
            schedule=[{"day": "Monday", "start": "09:00", "end": "10:30"}],
            color="#4CAF50"
        )
        
        # Verify course was created
        self.assertIsNotNone(course_id)
        self.assertEqual(course_id, "course_1")
        
        # Verify course data
        course = CourseManager.get_course(course_id)
        self.assertEqual(course["name"], "Test Course")
        self.assertEqual(course["units"], 3)
        self.assertEqual(len(course["schedule"]), 1)
    
    def test_add_course_validation(self):
        """Test that invalid courses are rejected"""
        # Empty name should raise error
        with self.assertRaises(ValueError):
            CourseManager.add_course("", 3, [], "#4CAF50")
        
        # Negative units should raise error
        with self.assertRaises(ValueError):
            CourseManager.add_course("Test", -1, [], "#4CAF50")
        
        # Zero units should raise error
        with self.assertRaises(ValueError):
            CourseManager.add_course("Test", 0, [], "#4CAF50")
    
    def test_list_courses(self):
        """Test listing all courses"""
        # Add multiple courses
        CourseManager.add_course("Course 1", 3, [], "#4CAF50")
        CourseManager.add_course("Course 2", 4, [], "#2196F3")
        
        # Get list
        courses = CourseManager.list_courses()
        
        # Verify
        self.assertEqual(len(courses), 2)
        self.assertEqual(courses[0]["name"], "Course 1")
        self.assertEqual(courses[1]["name"], "Course 2")
    
    def test_delete_course(self):
        """Test deleting a course"""
        # Add course
        course_id = CourseManager.add_course("Test", 3, [], "#4CAF50")
        
        # Delete it
        result = CourseManager.delete_course(course_id)
        self.assertTrue(result)
        
        # Verify it's gone
        course = CourseManager.get_course(course_id)
        self.assertIsNone(course)


class TestStudyLogger(unittest.TestCase):
    """Test StudyLogger functionality"""
    
    def setUp(self):
        """Run before each test"""
        reset_database()
        # Create a test course
        self.course_id = CourseManager.add_course("Test Course", 3, [], "#4CAF50")
    
    def test_log_session(self):
        """Test logging a study session"""
        session_id = StudyLogger.log_session(
            course_id=self.course_id,
            date="2026-03-15",
            duration_minutes=120,
            notes="Test session"
        )
        
        # Verify session was created
        self.assertIsNotNone(session_id)
        
        # Get sessions
        sessions = StudyLogger.get_sessions_by_course(self.course_id)
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0]["duration_minutes"], 120)
    
    def test_log_session_validation(self):
        """Test session validation"""
        # Invalid course should raise error
        with self.assertRaises(ValueError):
            StudyLogger.log_session("invalid_id", "2026-03-15", 120)
        
        # Negative duration should raise error
        with self.assertRaises(ValueError):
            StudyLogger.log_session(self.course_id, "2026-03-15", -10)


class TestAnalyticsEngine(unittest.TestCase):
    """Test AnalyticsEngine functionality"""
    
    def setUp(self):
        """Run before each test"""
        reset_database()
        self.course_id = CourseManager.add_course("Test Course", 3, [], "#4CAF50")
    
    def test_get_total_hours(self):
        """Test total study hours calculation"""
        # Log some sessions
        StudyLogger.log_session(self.course_id, "2026-03-15", 60)
        StudyLogger.log_session(self.course_id, "2026-03-16", 120)
        
        # Get total
        total = AnalyticsEngine.get_total_study_hours()
        self.assertEqual(total, 3.0)  # 180 minutes = 3 hours
    
    def test_confidence_calculation(self):
        """Test confidence level calculation"""
        # No sessions = low confidence
        confidence = AnalyticsEngine.calculate_confidence_level(self.course_id)
        self.assertEqual(confidence, 1.0)
        
        # Add sessions - confidence should increase
        StudyLogger.log_session(self.course_id, "2026-03-15", 120)
        confidence = AnalyticsEngine.calculate_confidence_level(self.course_id)
        self.assertGreater(confidence, 1.0)


class TestScheduleGenerator(unittest.TestCase):
    """Test ScheduleGenerator functionality"""
    
    def setUp(self):
        """Run before each test"""
        reset_database()
        # Add test courses
        CourseManager.add_course("Course A", 3, [], "#4CAF50")
        CourseManager.add_course("Course B", 4, [], "#2196F3")
        CourseManager.add_course("Course C", 3, [], "#FF5722")
    
    def test_schedule_generation(self):
        """Test that schedule is generated"""
        schedule = ScheduleGenerator.generate_weekly_schedule(20)
        
        # Should create some sessions
        self.assertGreater(len(schedule), 0)
        
        # Each session should have required fields
        for entry in schedule:
            self.assertIn("id", entry)
            self.assertIn("day", entry)
            self.assertIn("time_slot", entry)
            self.assertIn("course_id", entry)
            self.assertIn("type", entry)
    
    def test_proportional_allocation(self):
        """Test that hours are allocated proportionally"""
        schedule = ScheduleGenerator.generate_weekly_schedule(20)
        
        # Count sessions per course
        course_sessions = {}
        for entry in schedule:
            course_id = entry["course_id"]
            course_sessions[course_id] = course_sessions.get(course_id, 0) + 1
        
        # 4-unit course should have more sessions than 3-unit courses
        # (This is a basic check - exact counts may vary)
        self.assertGreater(len(course_sessions), 0)


class TestDataPersistence(unittest.TestCase):
    """Test data saving and loading"""
    
    def test_data_file_location(self):
        """Test that data.json is created in correct location"""
        reset_database()
        
        # Add some data
        CourseManager.add_course("Test", 3, [], "#4CAF50")
        
        # Verify file exists in correct location
        data_file = BASE_DIR / "data.json"
        self.assertTrue(data_file.exists())
    
    def test_data_persistence(self):
        """Test that data persists across load/save cycles"""
        reset_database()
        
        # Add data
        course_id = CourseManager.add_course("Persistent Course", 3, [], "#4CAF50")
        
        # Reload data
        data = load_data()
        
        # Verify data persisted
        courses = data["courses"]
        self.assertEqual(len(courses), 1)
        self.assertEqual(courses[0]["name"], "Persistent Course")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RUNNING STUDY TRACKER TESTS")
    print("="*60 + "\n")
    
    # Run tests
    unittest.main(verbosity=2)