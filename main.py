import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkinter import dialog
from unicodedata import name

from matplotlib import colors, units
from pyparsing import col
from pyparsing import col
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
        self.sidebar = ttk.Frame(main_frame, width=200, style="Sidebar.TFrame")
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        self.create_sidebar()
    
        # Right content area (calendar/views) - CHANGED TO tk.Frame
        self.content_area = tk.Frame(main_frame, bg=Colors.BG_SECONDARY)  # ← FIXED
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
            no_courses = tk.Label(
                self.content_area,
                text="No courses yet. Click 'Add New Course' to get started!",
                font=Fonts.BODY,
                bg=Colors.BG_SECONDARY,
                fg=Colors.TEXT_SECONDARY
            )
            no_courses.pack(pady=50)
        else:
            # Create a scrollable frame for course cards
            canvas = tk.Canvas(self.content_area, bg=Colors.BG_SECONDARY, highlightthickness=0)
            scrollbar = ttk.Scrollbar(self.content_area, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=Colors.BG_SECONDARY)
        
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
        
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
        
            # Display each course
            for course in self.courses:
                self.create_course_card(scrollable_frame, course)
        
            canvas.pack(side="left", fill="both", expand=True, padx=20)
            scrollbar.pack(side="right", fill="y")
    
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
        """Show dialog to add a new course with color picker"""
        course_dialog = tk.Toplevel(self.root)
        course_dialog.title("Add New Course")
        course_dialog.geometry("450x400")
        course_dialog.configure(bg=Colors.BG_PRIMARY)
    
        # Make dialog modal
        course_dialog.transient(self.root)
        course_dialog.grab_set()
    
        # Header
        header = tk.Label(
            course_dialog,
            text="Add New Course",
            font=Fonts.HEADING_1,
            bg=Colors.BG_PRIMARY,
            fg=Colors.PRIMARY
        )
        header.pack(pady=20)
    
        # Form frame
        form_frame = tk.Frame(course_dialog, bg=Colors.BG_PRIMARY)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=30)
    
        # Course name
        tk.Label(
            form_frame,
            text="Course Name:",
            font=Fonts.BODY_BOLD,
            bg=Colors.BG_PRIMARY,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor=tk.W, pady=(10, 5))
    
        name_entry = ttk.Entry(form_frame, width=40, font=Fonts.BODY)
        name_entry.pack(fill=tk.X)
        name_entry.focus()
    
        # Units
        tk.Label(
            form_frame,
            text="Credit Units:",
            font=Fonts.BODY_BOLD,
            bg=Colors.BG_PRIMARY,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor=tk.W, pady=(15, 5))
    
        units_entry = ttk.Entry(form_frame, width=40, font=Fonts.BODY)
        units_entry.pack(fill=tk.X)
    
        # Color selection
        tk.Label(
            form_frame,
            text="Course Color:",
            font=Fonts.BODY_BOLD,
            bg=Colors.BG_PRIMARY,
            fg=Colors.TEXT_PRIMARY
        ).pack(anchor=tk.W, pady=(15, 5))
    
        # Color options with preview
        color_frame = tk.Frame(form_frame, bg=Colors.BG_PRIMARY)
        color_frame.pack(fill=tk.X, pady=5)
    
        # Define color options
        color_options = [
            ("Blue", "#1a73e8"),
            ("Green", "#34a853"),
            ("Orange", "#fbbc04"),
            ("Red", "#ea4335"),
            ("Purple", "#9334e6"),
            ("Teal", "#00acc1"),
            ("Pink", "#e91e63"),
            ("Indigo", "#3f51b5"),
        ]
    
        selected_color = tk.StringVar(value="#1a73e8")  # Default blue
    
        # Create color selection buttons
        colors_container = tk.Frame(color_frame, bg=Colors.BG_PRIMARY)
        colors_container.pack()
    
        def create_color_button(color_name, color_code, row, col):
            """Create a clickable color button"""
            btn_frame = tk.Frame(colors_container, bg=Colors.BG_PRIMARY)
            btn_frame.grid(row=row, column=col, padx=5, pady=5)
        
            # Color preview circle
            color_btn = tk.Button(
                btn_frame,
                bg=color_code,
                width=3,
                height=1,
                relief=tk.RAISED,
                borderwidth=2,
                command=lambda: select_color(color_code, color_btn)
            )
            color_btn.pack()
        
            # Color name label
            tk.Label(
                btn_frame,
                text=color_name,
                font=Fonts.SMALL,
                bg=Colors.BG_PRIMARY,
                fg=Colors.TEXT_SECONDARY
            ).pack()
        
            return color_btn
    
        # Store color buttons for selection highlighting
        color_buttons = {}
    
        def select_color(color_code, clicked_btn):
            """Handle color selection"""
            selected_color.set(color_code)
            # Reset all buttons
            for btn in color_buttons.values():
                btn.config(relief=tk.RAISED, borderwidth=2)
            # Highlight selected
            clicked_btn.config(relief=tk.SUNKEN, borderwidth=3)
    
        # Create color buttons in a grid (2 rows x 4 columns)
        for idx, (color_name, color_code) in enumerate(color_options):
            row = idx // 4
            col = idx % 4
            btn = create_color_button(color_name, color_code, row, col)
            color_buttons[color_code] = btn
        
            # Pre-select first color
            if idx == 0:
                btn.config(relief=tk.SUNKEN, borderwidth=3)
    
        # Save function
        def save_course():
            """Save course with comprehensive error handling"""
            try:
                name = name_entry.get().strip()
                units_str = units_entry.get().strip()
                color = selected_color.get()
            
                # Validate name
                if not name:
                    messagebox.showerror(
                        "Validation Error", 
                        "Please enter a course name.\n\nCourse name cannot be empty."
                    )
                    name_entry.focus()
                    return
            
                # Validate units
                try:
                    units = int(units_str)
                except ValueError:
                    messagebox.showerror(
                        "Validation Error", 
                        "Units must be a valid number.\n\nPlease enter a whole number (e.g., 3, 4, 5)."
                    )
                    units_entry.focus()
                    units_entry.select_range(0, tk.END)
                    return
            
                if units <= 0:
                    messagebox.showerror(
                        "Validation Error", 
                        "Units must be a positive number.\n\nPlease enter 1 or more units."
                    )
                    units_entry.focus()
                    units_entry.select_range(0, tk.END)
                    return
            
                if units > 20:
                    result = messagebox.askyesno(
                        "Confirm High Unit Count", 
                        f"{units} units seems unusually high.\n\nMost courses are 1-6 units.\n\nDo you want to continue?"
                    )
                    if not result:
                        units_entry.focus()
                        units_entry.select_range(0, tk.END)
                        return
            
                # Add course with selected color
                try:
                    course_id = CourseManager.add_course(name, units, [], color)
                except Exception as e:
                    messagebox.showerror("Database Error", f"Could not add course:\n\n{str(e)}")
                    return

                    messagebox.showinfo(
                        "Success", 
                        f"✓ Course '{name}' added successfully!"
                        )
                
                    dialog.destroy()
                    self.refresh_data()
                    self.show_courses()
                
                except ValueError as ve:
                    messagebox.showerror("Database Error", f"Could not add course:\n\n{str(ve)}")
                except Exception as e:
                    messagebox.showerror("Unexpected Error", f"An unexpected error occurred:\n\n{str(e)}")
        
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save course:\n\n{str(e)}")
    
        # Buttons frame
        btn_frame = tk.Frame(dialog, bg=Colors.BG_PRIMARY)
        btn_frame.pack(pady=20)
    
        # Save button
        save_btn = ModernButton(
            btn_frame,
            text=f"{Icons.SAVE} Add Course",
            command=save_course,
            style="primary"
        )
        save_btn.pack(side=tk.LEFT, padx=5)
    
        # Cancel button
        cancel_btn = ModernButton(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            style="secondary"
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)
    
        # Enter key to save
        dialog.bind('<Return>', lambda e: save_course())
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
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

        self.display_schedule_grid()

    def display_schedule_grid(self):
        """Show the weekly schedule in a visual calendar grid"""
        from tracker import load_data, CourseManager
    
        data = load_data()
        schedule = data.get("weekly_schedule", [])
    
        if not schedule:
            no_schedule = tk.Label(
                self.content_area,
                text="No schedule yet. Click 'Generate New Schedule' above.",
                font=Fonts.BODY,
                bg=Colors.BG_SECONDARY,
                fg=Colors.TEXT_SECONDARY
            )
            no_schedule.pack(pady=50)
            return
    
        # Create scrollable canvas for calendar
        canvas = tk.Canvas(self.content_area, bg=Colors.BG_SECONDARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.content_area, orient="vertical", command=canvas.yview)
        calendar_frame = tk.Frame(canvas, bg=Colors.BG_SECONDARY)
    
        calendar_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
    
        canvas.create_window((0, 0), window=calendar_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
    
        # Calendar grid setup
        days = ["Time", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        hours = list(range(8, 22))  # 8 AM to 10 PM
    
        # Create header row (days of week)
        for col, day in enumerate(days):
            if col == 0:
                # Time column header
                header = tk.Label(
                    calendar_frame,
                    text=day,
                    font=Fonts.BODY_BOLD,
                    bg=Colors.PRIMARY,
                    fg=Colors.WHITE,
                    width=8,
                    height=2,
                    relief=tk.RAISED,
                    borderwidth=1
                )
            else:
                # Day column headers
                header = tk.Label(
                    calendar_frame,
                    text=day,
                    font=Fonts.BODY_BOLD,
                    bg=Colors.PRIMARY,
                    fg=Colors.WHITE,
                    width=15,
                    height=2,
                    relief=tk.RAISED,
                    borderwidth=1
                )
            header.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
    
        # Create time slots and schedule entries
        for row_idx, hour in enumerate(hours):
            # Time label (first column)
            time_label = tk.Label(
                calendar_frame,
                text=f"{hour:02d}:00",
                font=Fonts.BODY,
                bg=Colors.GRAY,
                fg=Colors.TEXT_PRIMARY,
                width=8,
                height=3,
                relief=tk.RIDGE,
                borderwidth=1
            )
            time_label.grid(row=row_idx + 1, column=0, sticky="nsew", padx=1, pady=1)
        
            # Create cells for each day
            for col_idx, day in enumerate(days[1:], start=1):
                # Check if there's a schedule entry for this day and hour
                entry_found = None
                for entry in schedule:
                    if entry["day"] == day:
                        # Parse time slot
                        start_time = entry["time_slot"].split("-")[0]
                        start_hour = int(start_time.split(":")[0])
                    
                        # Check if this entry starts at this hour
                        if start_hour == hour:
                            entry_found = entry
                            break
            
                if entry_found:
                    # Get course details
                    course = CourseManager.get_course(entry_found["course_id"])
                
                    if course:
                        # Determine color and icon
                        color = course.get('color', Colors.PRIMARY)
                        icon = "🎓" if entry_found["type"] == "class" else "📚"
                    
                        # Create colored entry cell
                        entry_cell = tk.Label(
                            calendar_frame,
                            text=f"{icon}\n{course['name']}\n{entry_found['time_slot']}",
                            font=Fonts.SMALL,
                            bg=color,
                            fg=Colors.WHITE,
                            width=15,
                            height=3,
                            relief=tk.RAISED,
                            borderwidth=2,
                            wraplength=100,
                            justify=tk.CENTER
                        )
                        entry_cell.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=1, pady=1)
                    else:
                        # Empty cell
                        empty_cell = tk.Label(
                            calendar_frame,
                            text="",
                            bg=Colors.WHITE,
                            relief=tk.RIDGE,
                            borderwidth=1
                        )
                        empty_cell.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=1, pady=1)
                else:
                    # Empty cell (no entry at this time)
                    empty_cell = tk.Label(
                        calendar_frame,
                        text="",
                        bg=Colors.WHITE,
                        relief=tk.RIDGE,
                        borderwidth=1,
                        height=3
                    )
                    empty_cell.grid(row=row_idx + 1, column=col_idx, sticky="nsew", padx=1, pady=1)
    
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=10)
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