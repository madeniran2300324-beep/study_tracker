import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tracker import CourseManager, StudyLogger, AnalyticsEngine, ScheduleGenerator

class StudyTrackerApp:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Study Tracker")
        self.root.geometry("1200x800")
        
        # Set up the main layout
        self.setup_ui()
        
        # Load initial data
        self.refresh_data()
    
    def setup_ui(self):
        """Create the main UI layout"""
        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left sidebar (navigation)
        self.sidebar = ttk.Frame(main_frame, width=200)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.create_sidebar()
        
        # Right content area (calendar/views)
        self.content_area = ttk.Frame(main_frame)
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.create_content_area()
    
    def create_sidebar(self):
        """Create navigation sidebar"""
        # Title
        title = ttk.Label(
            self.sidebar, 
            text="Study Tracker",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=20)
        
        # Navigation buttons
        buttons = [
            ("📚 Courses", self.show_courses),
            ("⏱️ Log Study Time", self.log_study_time),
            ("📅 Weekly Schedule", self.show_schedule_view),
            ("📊 View Statistics", self.show_statistics),
            ("🎯 Exam Prep", self.show_exam_prep),
        ]
        
        for text, command in buttons:
            btn = ttk.Button(
                self.sidebar,
                text=text,
                command=command,
                width=20
            )
            btn.pack(pady=5, padx=10)
    
    def create_content_area(self):
        """Create main content area"""
        # Welcome message
        welcome = ttk.Label(
            self.content_area,
            text="Welcome to Study Tracker!",
            font=("Arial", 24)
        )
        welcome.pack(pady=50)
        
        info = ttk.Label(
            self.content_area,
            text="Use the sidebar to navigate",
            font=("Arial", 12)
        )
        info.pack()
    
    def refresh_data(self):
        """Reload data from JSON"""
        self.courses = CourseManager.list_courses()
        print(f"Loaded {len(self.courses)} course(s)")
    
    # ============================================
    # NAVIGATION HANDLERS
    # ============================================
    
    def show_courses(self):
        """Display courses view"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Header
        header = ttk.Label(
            self.content_area,
            text="My Courses",
            font=("Arial", 20, "bold")
        )
        header.pack(pady=20)
        
        # Add course button
        add_btn = ttk.Button(
            self.content_area,
            text="+ Add New Course",
            command=self.add_course_dialog
        )
        add_btn.pack(pady=10)
        
        # Course list
        if not self.courses:
            no_courses = ttk.Label(
                self.content_area,
                text="No courses yet. Click 'Add New Course' to get started!",
                font=("Arial", 12)
            )
            no_courses.pack(pady=50)
        else:
            # Create a frame for course cards
            courses_frame = ttk.Frame(self.content_area)
            courses_frame.pack(fill=tk.BOTH, expand=True, padx=20)
            
            for course in self.courses:
                self.create_course_card(courses_frame, course)
    
    def create_course_card(self, parent, course):
        """Create a card display for a course"""
        card = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        card.pack(fill=tk.X, pady=10, padx=10)
        
        # Course name
        name = ttk.Label(
            card,
            text=course['name'],
            font=("Arial", 14, "bold")
        )
        name.pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Course details
        details = ttk.Label(
            card,
            text=f"Units: {course['units']} | Sessions: {len(course['schedule'])}",
            font=("Arial", 10)
        )
        details.pack(anchor=tk.W, padx=10)
        
        # Study hours
        hours = AnalyticsEngine.get_hours_by_course(course['id'])
        hours_label = ttk.Label(
            card,
            text=f"Total Study Time: {hours} hours",
            font=("Arial", 10)
        )
        hours_label.pack(anchor=tk.W, padx=10, pady=(5, 10))
    
    def add_course_dialog(self):
        """Show dialog to add a new course"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Course")
        dialog.geometry("400x300")
        
        # Course name
        ttk.Label(dialog, text="Course Name:").pack(pady=(20, 5))
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack()
        
        # Units
        ttk.Label(dialog, text="Credit Units:").pack(pady=(10, 5))
        units_entry = ttk.Entry(dialog, width=40)
        units_entry.pack()
        
        def save_course():
            name = name_entry.get().strip()
            units_str = units_entry.get().strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter a course name")
                return
            
            try:
                units = int(units_str)
                if units <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Units must be a positive number")
                return
            
            # Add course (with empty schedule for now)
            CourseManager.add_course(name, units, [], "#4CAF50")
            messagebox.showinfo("Success", f"Added {name}!")
            
            dialog.destroy()
            self.refresh_data()
            self.show_courses()
        
        # Save button
        save_btn = ttk.Button(dialog, text="Add Course", command=save_course)
        save_btn.pack(pady=20)
    
    def log_study_time(self):
        """Show study time logging view"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = ttk.Label(
            self.content_area,
            text="Log Study Time",
            font=("Arial", 20, "bold")
        )
        header.pack(pady=20)
        
        if not self.courses:
            ttk.Label(
                self.content_area,
                text="Add courses first before logging study time!",
                font=("Arial", 12)
            ).pack(pady=50)
            return
        
        # Create form
        form_frame = ttk.Frame(self.content_area)
        form_frame.pack(pady=20)
        
        # Course selection
        ttk.Label(form_frame, text="Select Course:").grid(row=0, column=0, pady=10, sticky=tk.W)
        course_var = tk.StringVar()
        course_names = [c['name'] for c in self.courses]
        course_combo = ttk.Combobox(
            form_frame,
            textvariable=course_var,
            values=course_names,
            state="readonly",
            width=30
        )
        course_combo.grid(row=0, column=1, pady=10)
        if course_names:
            course_combo.current(0)
        
        # Date
        ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, pady=10, sticky=tk.W)
        date_entry = ttk.Entry(form_frame, width=32)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        date_entry.grid(row=1, column=1, pady=10)
        
        # Duration
        ttk.Label(form_frame, text="Duration (minutes):").grid(row=2, column=0, pady=10, sticky=tk.W)
        duration_entry = ttk.Entry(form_frame, width=32)
        duration_entry.grid(row=2, column=1, pady=10)
        
        # Notes
        ttk.Label(form_frame, text="Notes (optional):").grid(row=3, column=0, pady=10, sticky=tk.W)
        notes_entry = ttk.Entry(form_frame, width=32)
        notes_entry.grid(row=3, column=1, pady=10)
        
        def save_session():
            # Get selected course
            selected_name = course_var.get()
            course_id = None
            for c in self.courses:
                if c['name'] == selected_name:
                    course_id = c['id']
                    break
            
            if not course_id:
                messagebox.showerror("Error", "Please select a course")
                return
            
            date = date_entry.get().strip()
            duration_str = duration_entry.get().strip()
            notes = notes_entry.get().strip()
            
            # Validate
            try:
                duration = int(duration_str)
                if duration <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error", "Duration must be a positive number")
                return
            
            # Validate date format
            try:
                datetime.fromisoformat(date)
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            # Log session
            StudyLogger.log_session(course_id, date, duration, notes)
            messagebox.showinfo("Success", f"Logged {duration} minutes for {selected_name}!")
            
            # Clear form
            duration_entry.delete(0, tk.END)
            notes_entry.delete(0, tk.END)
        
        # Save button
        save_btn = ttk.Button(form_frame, text="Log Session", command=save_session)
        save_btn.grid(row=4, column=0, columnspan=2, pady=20)
    
    def show_statistics(self):
        """Show statistics view"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = ttk.Label(
            self.content_area,
            text="Study Statistics",
            font=("Arial", 20, "bold")
        )
        header.pack(pady=20)
        
        # Total hours
        total = AnalyticsEngine.get_total_study_hours()
        ttk.Label(
            self.content_area,
            text=f"Total Study Time: {total} hours",
            font=("Arial", 16, "bold")
        ).pack(pady=20)
        
        # Course breakdown
        if self.courses:
            ttk.Label(
                self.content_area,
                text="By Course:",
                font=("Arial", 14, "bold")
            ).pack(pady=(20, 10))
            
            # Create a frame for course stats
            stats_frame = ttk.Frame(self.content_area)
            stats_frame.pack(fill=tk.BOTH, expand=True, padx=40)
            
            for course in self.courses:
                summary = AnalyticsEngine.get_course_summary(course['id'])
                
                # Course stat card
                card = ttk.Frame(stats_frame, relief=tk.GROOVE, borderwidth=2)
                card.pack(fill=tk.X, pady=10, padx=10)
                
                ttk.Label(
                    card,
                    text=summary['name'],
                    font=("Arial", 12, "bold")
                ).pack(anchor=tk.W, padx=10, pady=(10, 5))
                
                ttk.Label(
                    card,
                    text=f"Study Time: {summary['total_hours']} hours | Sessions: {summary['total_sessions']}",
                    font=("Arial", 10)
                ).pack(anchor=tk.W, padx=10)
                
                ttk.Label(
                    card,
                    text=f"Consistency: {summary['consistency']}% | Confidence: {summary['confidence_level']}/5.0",
                    font=("Arial", 10)
                ).pack(anchor=tk.W, padx=10, pady=(0, 10))
        else:
            ttk.Label(
                self.content_area,
                text="No courses yet!",
                font=("Arial", 12)
            ).pack(pady=50)
    
    def show_exam_prep(self):
        """Show exam preparation view"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        header = ttk.Label(
            self.content_area,
            text="Exam Preparation",
            font=("Arial", 20, "bold")
        )
        header.pack(pady=20)
        
        ttk.Label(
            self.content_area,
            text="Exam prep features coming in Week 4!",
            font=("Arial", 12)
        ).pack(pady=50)

    def show_schedule_view(self):
        """Display and manage weekly schedule"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Header
        header = ttk.Label(
            self.content_area,
            text="Weekly Study Schedule",
            font=("Arial", 20, "bold")
        )
        header.pack(pady=20)
        
        # Generate button
        def generate_schedule():
            success = ScheduleGenerator.regenerate_full_schedule(20)
            if success:
                messagebox.showinfo("Success", "Schedule generated!")
                self.refresh_data()
                self.show_schedule_view()  # Refresh to show new schedule
        
        generate_btn = ttk.Button(
            self.content_area,
            text="🔄 Generate New Schedule (20 hours/week)",
            command=generate_schedule
        )
        generate_btn.pack(pady=10)
        
        # Display current schedule
        self.display_schedule_grid()

    def display_schedule_grid(self):
        """Show the weekly schedule in a grid"""
        from tracker import load_data, CourseManager
        
        data = load_data()
        schedule = data.get("weekly_schedule", [])
        
        if not schedule:
            ttk.Label(
                self.content_area,
                text="No schedule yet. Click 'Generate New Schedule' above.",
                font=("Arial", 12)
            ).pack(pady=50)
            return
        
        # Create a frame for the schedule
        schedule_frame = ttk.Frame(self.content_area)
        schedule_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Add scrollbar if needed
        canvas = tk.Canvas(schedule_frame)
        scrollbar = ttk.Scrollbar(schedule_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Group by day
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for day in days:
            day_entries = [s for s in schedule if s["day"] == day]
            
            if day_entries:
                # Day header
                day_label = ttk.Label(
                    scrollable_frame,
                    text=day,
                    font=("Arial", 14, "bold")
                )
                day_label.pack(anchor=tk.W, pady=(10, 5))
                
                # Entries for this day
                for entry in sorted(day_entries, key=lambda x: x["time_slot"]):
                    course = CourseManager.get_course(entry["course_id"])
                    entry_type = "📚 Study" if entry["type"] == "study" else "🎓 Class"
                    
                    entry_text = f"  {entry['time_slot']:15} - {course['name']} ({entry_type})"
                    
                    entry_label = ttk.Label(
                        scrollable_frame,
                        text=entry_text,
                        font=("Arial", 11)
                    )
                    entry_label.pack(anchor=tk.W, padx=20)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

# ============================================
# RUN THE APP
# ============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTrackerApp(root)
    root.mainloop()