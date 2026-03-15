from email import header
from posixpath import sep
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from matplotlib import colors
from tracker import CourseManager, StudyLogger, AnalyticsEngine, ScheduleGenerator, load_data
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from styles import Colors, Fonts, ModernButton, Card, SectionHeader, Icons, configure_styles

class StudyTrackerApp:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Study Tracker")
        self.root.geometry("1200x800")
        
        #Configure modern styles
        configure_styles()
        self.root.configure(bg=Colors.BG_PRIMARY)

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
        """Create modern navigation sidebar"""
        # Sidebar frame with custom color
        self.sidebar.configure(style="Sidebar.TFrame")
    
        # App title with icon
        title_frame = ttk.Frame(self.sidebar, style="Sidebar.TFrame")
        title_frame.pack(pady=30)
    
        icon_label = tk.Label(
            title_frame,
            text="📚",
            font=("Segoe UI", 32),
            bg=Colors.BG_SIDEBAR
        )
        icon_label.pack()
    
        title = tk.Label(
            title_frame,
            text="Study Tracker",
            font=Fonts.TITLE,
            bg=Colors.BG_SIDEBAR,
            fg=Colors.PRIMARY
        )
        title.pack(pady=(10, 0))
    
        # Separator
        sep = ttk.Separator(self.sidebar, orient='horizontal')
        sep.pack(fill=tk.X, padx=20, pady=20)
    
        # Navigation buttons with icons
        buttons = [
            (f"{Icons.COURSES}  Courses", self.show_courses),
            (f"{Icons.LOG}  Log Study Time", self.log_study_time),
            (f"{Icons.SCHEDULE}  Weekly Schedule", self.show_schedule_view),
            (f"{Icons.STATS}  Statistics", self.show_statistics),
            (f"{Icons.EXAM}  Exam Prep", self.show_exam_prep),
        ]
    
        for text, command in buttons:
            btn = ttk.Button(
                self.sidebar,
                text=text,
                command=command,
                style="Sidebar.TButton",
                width=22
            )
            btn.pack(pady=5, padx=15, ipady=5)
    
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
    
    def lighten_color(self, hex_color):
        """Convert a hex color to a lighter shade for study blocks"""
        # Remove the # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert hex to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Lighten by mixing with white (increase each channel by 40%)
        r = min(255, int(r + (255 - r) * 0.6))
        g = min(255, int(g + (255 - g) * 0.6))
        b = min(255, int(b + (255 - b) * 0.6))
        
        # Convert back to hex
        return f'#{r:02x}{g:02x}{b:02x}'
    
    # ============================================
    # NAVIGATION HANDLERS
    # ============================================
    
    def show_courses(self):
        """Display courses view"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
        # Set background color
        self.content_area.configure(bg=Colors.BG_SECONDARY)
    
        # Header with icon
        header_frame = tk.Frame(self.content_area, bg=Colors.BG_SECONDARY)
        header_frame.pack(pady=30)
    
        header = tk.Label(
            header_frame,
            text=f"{Icons.COURSES} My Courses",
            font=Fonts.TITLE,
            bg=Colors.BG_SECONDARY,
            fg=Colors.PRIMARY
        )
        header.pack()
    
        # Modern add button
        add_btn = ModernButton(
            self.content_area,
            text=f"{Icons.ADD} Add New Course",
            command=self.add_course_dialog,
            style="primary"
        )
        add_btn.pack(pady=15)
      
        
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
        """Create a beautiful course card"""
        # Use Card widget for shadow effect
        card = Card(parent)
        card.pack(fill=tk.X, pady=12, padx=15)
    
        # Color strip on the left
        color_strip = tk.Frame(
            card,
            bg=course.get('color', Colors.PRIMARY),
            width=6
        )
        color_strip.pack(side=tk.LEFT, fill=tk.Y)
    
        # Content area
        content = tk.Frame(card, bg=Colors.WHITE)
        content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=15, pady=15)
    
        # Course name
        name_label = tk.Label(
            content,
            text=course['name'],
            font=Fonts.HEADING_2,
            bg=Colors.WHITE,
            fg=Colors.TEXT_PRIMARY,
            anchor=tk.W
        )
        name_label.pack(anchor=tk.W)
    
        # Course details
        units_text = f"{Icons.STAR} {course['units']} Units"
        sessions_text = f"{Icons.CALENDAR} {len(course.get('schedule', []))} Class Sessions"
    
        details_label = tk.Label(
            content,
            text=f"{units_text}  •  {sessions_text}",
            font=Fonts.BODY,
            bg=Colors.WHITE,
            fg=Colors.TEXT_SECONDARY,
            anchor=tk.W
        )
        details_label.pack(anchor=tk.W, pady=(5, 10))
    
        # Study stats
        hours = AnalyticsEngine.get_hours_by_course(course['id'])
        confidence = AnalyticsEngine.calculate_confidence_level(course['id'])
    
        stats_frame = tk.Frame(content, bg=Colors.WHITE)
        stats_frame.pack(fill=tk.X)
    
        # Hours badge
        hours_badge = tk.Frame(stats_frame, bg=Colors.PRIMARY_LIGHT, padx=12, pady=6)
        hours_badge.pack(side=tk.LEFT, padx=(0, 10))
    
        hours_label = tk.Label(
            hours_badge,
            text=f"{hours:.1f}h studied",
            font=Fonts.BODY_BOLD,
            bg=Colors.PRIMARY_LIGHT,
            fg=Colors.WHITE
        )
        hours_label.pack()
    
        # Confidence badge
        if confidence >= 4.0:
            conf_color = Colors.SECONDARY
            conf_icon = Icons.PRIORITY_LOW
        elif confidence >= 2.5:
            conf_color = Colors.WARNING
            conf_icon = Icons.PRIORITY_MED
        else:
            conf_color = Colors.DANGER
            conf_icon = Icons.PRIORITY_HIGH
    
        conf_badge = tk.Frame(stats_frame, bg=conf_color, padx=12, pady=6)
        conf_badge.pack(side=tk.LEFT)
    
        conf_label = tk.Label(
            conf_badge,
            text=f"{conf_icon} {confidence:.1f}/5.0",
            font=Fonts.BODY_BOLD,
            bg=conf_color,
            fg=Colors.WHITE
        )
        conf_label.pack()
    
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
    
        # Set background color
        self.content_area.configure(bg=Colors.BG_SECONDARY)
    
        # Header with icon
        header_frame = tk.Frame(self.content_area, bg=Colors.BG_SECONDARY)
        header_frame.pack(pady=30)
    
        header = tk.Label(
            header_frame,
            text=f"{Icons.LOG} Log Study Time",
            font=Fonts.TITLE,
            bg=Colors.BG_SECONDARY,
            fg=Colors.PRIMARY
        )
        header.pack()
        
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
        """Show statistics view with charts"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
        # Set background color
        self.content_area.configure(bg=Colors.BG_SECONDARY)
    
        # Header with icon
        header_frame = tk.Frame(self.content_area, bg=Colors.BG_SECONDARY)
        header_frame.pack(pady=30)
    
        header = tk.Label(
            header_frame,
            text=f"{Icons.STATS} Study Statistics",
            font=Fonts.TITLE,
            bg=Colors.BG_SECONDARY,
            fg=Colors.PRIMARY
        )
        header.pack()
    
        # Check if we have data
        if not self.courses:
            ttk.Label(
                self.content_area,
                text="No courses yet. Add courses to see statistics!",
                font=("Arial", 12)
            ).pack(pady=50)
            return
    
        # Get study data
        course_names = []
        study_hours = []
        colors = []
    
        for course in self.courses:
            hours = AnalyticsEngine.get_hours_by_course(course['id'])
            if hours > 0:  # Only show courses with study time
                course_names.append(course['name'])
                study_hours.append(hours)
                colors.append(course.get('color', '#4CAF50'))
    
        if not study_hours:
            ttk.Label(
                self.content_area,
                text="No study sessions logged yet. Start logging your study time!",
                font=("Arial", 12)
            ).pack(pady=50)
            return
    
        # Total hours display
        total = sum(study_hours)
        total_label = ttk.Label(
            self.content_area,
            text=f"Total Study Time: {total:.1f} hours",
            font=("Arial", 16, "bold")
        )
        total_label.pack(pady=10)
    
        # Chart type selector
        chart_frame = ttk.Frame(self.content_area)
        chart_frame.pack(pady=10)
    
        chart_type = tk.StringVar(value="bar")
    
        def update_chart():
        # Remove old chart
            for widget in chart_container.winfo_children():
                widget.destroy()
        
            if chart_type.get() == "bar":
                self.create_bar_chart(chart_container, course_names, study_hours, colors)
            else:
                self.create_pie_chart(chart_container, course_names, study_hours, colors)
    
        ttk.Label(chart_frame, text="Chart Type:", font=("Arial", 11)).pack(side=tk.LEFT, padx=5)
    
        bar_radio = ttk.Radiobutton(
            chart_frame,
            text="Bar Chart",
            variable=chart_type,
            value="bar",
            command=update_chart
        )
        bar_radio.pack(side=tk.LEFT, padx=5)
    
        pie_radio = ttk.Radiobutton(
            chart_frame,
            text="Pie Chart",
            variable=chart_type,
            value="pie",
            command=update_chart
        )
        pie_radio.pack(side=tk.LEFT, padx=5)
    
        # Chart container
        chart_container = ttk.Frame(self.content_area)
        chart_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
    
        # Show initial chart
        self.create_bar_chart(chart_container, course_names, study_hours, colors)
    
        # Detailed breakdown
        details_frame = ttk.LabelFrame(self.content_area, text="Detailed Breakdown", padding=10)
        details_frame.pack(fill=tk.X, padx=20, pady=10)
    
        for i, course in enumerate(self.courses):
            hours = AnalyticsEngine.get_hours_by_course(course['id'])
            confidence = AnalyticsEngine.calculate_confidence_level(course['id'])
        
            if hours > 0:
                percentage = (hours / total) * 100
                detail_text = f"{course['name']}: {hours:.1f}h ({percentage:.1f}%) | Confidence: {confidence:.1f}/5.0"
            else:
                detail_text = f"{course['name']}: No study time logged yet"
        
            detail_label = ttk.Label(
                details_frame,
                text=detail_text,
                font=("Arial", 10)
            )
            detail_label.pack(anchor=tk.W, pady=2)

    def create_bar_chart(self, parent, course_names, study_hours, colors):
        """Create a bar chart of study hours"""
        # Create figure
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
    
        # Create bars
        bars = ax.bar(course_names, study_hours, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
    
        # Customize chart
        ax.set_xlabel('Course', fontsize=12, fontweight='bold')
        ax.set_ylabel('Hours Studied', fontsize=12, fontweight='bold')
        ax.set_title('Study Time by Course', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
    
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width()/2., 
                height,
                f'{height:.1f}h',
                ha='center', 
                va='bottom',
                fontweight='bold'
            )
    
        # Rotate x-axis labels if many courses
        if len(course_names) > 3:
            ax.set_xticklabels(course_names, rotation=45, ha='right')
    
        fig.tight_layout()
    
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_pie_chart(self, parent, course_names, study_hours, colors):
        """Create a pie chart of study time distribution"""
        # Create figure
        fig = Figure(figsize=(8, 5), dpi=100)
        ax = fig.add_subplot(111)
    
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            study_hours,
            labels=course_names,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 11, 'fontweight': 'bold'}
        )
    
        # Make percentage text white for better visibility
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
        ax.set_title('Study Time Distribution', fontsize=14, fontweight='bold', pad=20)
    
        # Equal aspect ratio ensures circular pie
        ax.axis('equal')
    
        fig.tight_layout()
    
        # Embed in tkinter
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def show_exam_prep(self):
        """Show exam preparation view with priorities"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
        # Set background color
        self.content_area.configure(bg=Colors.BG_SECONDARY)
    
        # Header with icon
        header_frame = tk.Frame(self.content_area, bg=Colors.BG_SECONDARY)
        header_frame.pack(pady=30)
    
        header = tk.Label(
            header_frame,
            text=f"{Icons.EXAM} Exam Preparation Planner",
            font=Fonts.TITLE,
            bg=Colors.BG_SECONDARY,
            fg=Colors.PRIMARY
        )
        header.pack()
        
        # Check if we have courses
        if not self.courses:
            ttk.Label(
                self.content_area,
                text="Add courses first to see exam preparation recommendations!",
                font=("Arial", 12)
            ).pack(pady=50)
            return
        
        # Update confidence levels
        AnalyticsEngine.update_all_confidence_levels()
        self.refresh_data()
        
        # Get confidence data
        data = load_data()
        confidence_data = data.get("exam_confidence", [])
        
        if not confidence_data:
            ttk.Label(
                self.content_area,
                text="Log some study sessions first to generate confidence levels!",
                font=("Arial", 12)
            ).pack(pady=50)
            return
        
        # Info section
        info_frame = ttk.LabelFrame(self.content_area, text="How This Works", padding=15)
        info_frame.pack(fill=tk.X, padx=20, pady=10)
        
        info_text = """Confidence levels are automatically calculated based on:
        • Hours studied (40% weight)
        • Study consistency - how regularly you study (40% weight)  
        • Recency - have you studied recently? (20% weight)
        
        Courses with LOW confidence need MORE exam prep time!"""
        
        ttk.Label(
            info_frame,
            text=info_text,
            font=("Arial", 10),
            justify=tk.LEFT
        ).pack(anchor=tk.W)
        
        # Priority recommendations
        priority_frame = ttk.LabelFrame(self.content_area, text="Exam Priority Recommendations", padding=15)
        priority_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create priority list
        priorities = []
        for conf in confidence_data:
            course = CourseManager.get_course(conf["course_id"])
            if course:
                # Priority score = units × (6 - confidence) 
                # Higher score = needs more attention
                priority_score = course["units"] * (6 - conf["confidence_level"])
                
                priorities.append({
                    "course": course,
                    "confidence": conf["confidence_level"],
                    "priority_score": priority_score,
                    "hours": AnalyticsEngine.get_hours_by_course(course["id"])
                })
        
        # Sort by priority (highest first)
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        
        # Display priorities
        for i, item in enumerate(priorities):
            rank = i + 1
            course = item["course"]
            confidence = item["confidence"]
            hours = item["hours"]
            
            # Determine priority level
            if rank == 1:
                priority_label = "🔴 HIGHEST PRIORITY"
                bg_color = "#ffebee"
            elif rank <= 3:
                priority_label = "🟡 High Priority"
                bg_color = "#fff9c4"
            else:
                priority_label = "🟢 Lower Priority"
                bg_color = "#e8f5e9"
            
            # Create card for each course
            card = tk.Frame(priority_frame, relief=tk.RAISED, borderwidth=2, bg=bg_color)
            card.pack(fill=tk.X, pady=8, padx=5)
            
            # Rank and priority
            rank_label = tk.Label(
                card,
                text=f"#{rank}  {priority_label}",
                font=("Arial", 12, "bold"),
                bg=bg_color
            )
            rank_label.pack(anchor=tk.W, padx=10, pady=(10, 5))
            
            # Course name
            course_label = tk.Label(
                card,
                text=course["name"],
                font=("Arial", 14, "bold"),
                bg=bg_color
            )
            course_label.pack(anchor=tk.W, padx=10)
            
            # Stats
            stats_text = f"Confidence: {confidence:.1f}/5.0  |  Study Time: {hours:.1f}h  |  Units: {course['units']}"
            stats_label = tk.Label(
                card,
                text=stats_text,
                font=("Arial", 10),
                bg=bg_color
            )
            stats_label.pack(anchor=tk.W, padx=10, pady=(5, 10))
            
            # Recommendation
            if confidence < 2.5:
                recommendation = "⚠️ Urgent: Schedule intensive review sessions"
            elif confidence < 3.5:
                recommendation = "📝 Recommended: Add more practice problems and review"
            else:
                recommendation = "✓ On track: Maintain current study pace"
            
            rec_label = tk.Label(
                card,
                text=recommendation,
                font=("Arial", 10, "italic"),
                bg=bg_color,
                fg="#1976d2"
            )
            rec_label.pack(anchor=tk.W, padx=10, pady=(0, 10))

    def show_schedule_view(self):
        """Display and manage weekly schedule"""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
        # Set background color
        self.content_area.configure(bg=Colors.BG_SECONDARY)
    
        # Header with icon
        header_frame = tk.Frame(self.content_area, bg=Colors.BG_SECONDARY)
        header_frame.pack(pady=30)
    
        header = tk.Label(
            header_frame,
            text=f"{Icons.SCHEDULE} Weekly Study Schedule",
            font=Fonts.TITLE,
            bg=Colors.BG_SECONDARY,
            fg=Colors.PRIMARY
        )
        header.pack()
    
        # Generate button (modern style)
        def generate_schedule():
            success = ScheduleGenerator.regenerate_full_schedule(20)
            if success:
                messagebox.showinfo("Success", "Schedule generated!")
                self.refresh_data()
                self.show_schedule_view()
    
        generate_btn = ModernButton(
            self.content_area,
            text=f"{Icons.REFRESH} Generate New Schedule (20 hours/week)",
            command=generate_schedule,
            style="success"
        )
        generate_btn.pack(pady=15)

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

    def show_calendar_view(self):
        """Display visual calendar grid"""
        from tracker import load_data, CourseManager
        
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Header
        header = ttk.Label(
            self.content_area,
            text="Weekly Calendar View",
            font=("Arial", 20, "bold")
        )
        header.pack(pady=20)
        
        # Load schedule data
        data = load_data()
        schedule = data.get("weekly_schedule", [])
        
        if not schedule:
            ttk.Label(
                self.content_area,
                text="No schedule generated yet. Go to 'Weekly Schedule' and click 'Generate New Schedule'.",
                font=("Arial", 12)
            ).pack(pady=50)
            return
        
        # Create scrollable frame for calendar
        calendar_container = ttk.Frame(self.content_area)
        calendar_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        canvas = tk.Canvas(calendar_container, bg='white')
        scrollbar_y = ttk.Scrollbar(calendar_container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(calendar_container, orient="horizontal", command=canvas.xview)
        
        calendar_frame = ttk.Frame(canvas)
        
        calendar_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=calendar_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # Build the calendar grid
        self.build_calendar_grid(calendar_frame, schedule)
        
        # Pack scrollbars and canvas
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        calendar_container.grid_rowconfigure(0, weight=1)
        calendar_container.grid_columnconfigure(0, weight=1)

    def build_calendar_grid(self, parent, schedule):
        """Create the actual calendar grid with time slots and events"""
        from tracker import CourseManager
        
        # Days of the week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        # Time slots (8 AM to 10 PM)
        time_slots = []
        for hour in range(8, 22):
            time_slots.append(f"{hour:02d}:00")
        
        # Header row - Days
        tk.Label(
            parent,
            text="Time",
            font=("Arial", 10, "bold"),
            bg="#E8EAF6",
            relief=tk.RIDGE,
            width=8,
            height=2
        ).grid(row=0, column=0, sticky="nsew", padx=1, pady=1)
        
        for col, day in enumerate(days, start=1):
            tk.Label(
                parent,
                text=day,
                font=("Arial", 11, "bold"),
                bg="#3F51B5",
                fg="white",
                relief=tk.RIDGE,
                height=2
            ).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        
        # Create grid cells
        self.calendar_cells = {}  # Store cell references
        
        for row, time_slot in enumerate(time_slots, start=1):
            # Time label (left column)
            tk.Label(
                parent,
                text=time_slot,
                font=("Arial", 9),
                bg="#E8EAF6",
                relief=tk.RIDGE,
                width=8
            ).grid(row=row, column=0, sticky="nsew", padx=1, pady=1)
            
            # Day cells
            for col, day in enumerate(days, start=1):
                cell = tk.Frame(
                    parent,
                    bg="white",
                    relief=tk.RIDGE,
                    borderwidth=1,
                    width=120,
                    height=60
                )
                cell.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)
                cell.grid_propagate(False)  # Maintain fixed size
                
                # Store cell reference
                self.calendar_cells[(day, time_slot)] = cell
        
        # Populate cells with schedule events
        for entry in schedule:
            day = entry["day"]
            time_range = entry["time_slot"]
            course_id = entry["course_id"]
            entry_type = entry["type"]
            
            # Parse time slot (e.g., "14:00-16:00")
            start_time, end_time = time_range.split("-")
            start_hour = start_time.split(":")[0]
            
            # Get course details
            course = CourseManager.get_course(course_id)
            if not course:
                continue
            
            # Determine color
            if entry_type == "class":
                bg_color = course.get("color", "#4CAF50")
                label_text = f"🎓 {course['name']}\n{time_range}"
            else:  # study
                bg_color = self.lighten_color(course.get("color", "#4CAF50"))
                label_text = f"📚 {course['name']}\n{time_range}"
            
            # Find the cell and add the event
            cell_key = (day, f"{start_hour}:00")
            if cell_key in self.calendar_cells:
                cell = self.calendar_cells[cell_key]
                
                # Create event label
                event_label = tk.Label(
                    cell,
                    text=label_text,
                    bg=bg_color,
                    fg="white" if entry_type == "class" else "black",
                    font=("Arial", 9, "bold"),
                    wraplength=110,
                    justify=tk.CENTER,
                    relief=tk.RAISED,
                    borderwidth=2
                )
                event_label.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

# ============================================
# RUN THE APP
# ============================================

if __name__ == "__main__":
    root = tk.Tk()
    app = StudyTrackerApp(root)
    root.mainloop()