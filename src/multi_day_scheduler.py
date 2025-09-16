# Complete Multi-Day Scheduler with Delete Functions
# File: src/multi_day_scheduler.py

import anthropic
import sqlite3
import json
import sys
import os
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import re

# Add config directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from config.credentials import CLAUDE_API_KEY
except ImportError:
    print("Error: Could not import CLAUDE_API_KEY from config.credentials")
    sys.exit(1)

class MultiDayScheduler:
    """
    Advanced Multi-Day Planning System with Full CRUD Operations
    
    AI Implementation Concepts Demonstrated:
    - Multi-dimensional Optimization: Balance time, energy, priority across days
    - Constraint Satisfaction: Respect deadlines, dependencies, capacity limits
    - Pattern Recognition: Learn from user's productivity patterns
    - Recursive Planning: Break large projects into manageable daily chunks
    - Predictive Scheduling: Anticipate conflicts and suggest alternatives
    - Data Management: Complete Create, Read, Update, Delete operations
    """
    
    def __init__(self, db_path: str):
        self.client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
        self.db_path = db_path
        self.setup_advanced_database()
    
    def setup_advanced_database(self):
        """Create advanced scheduling tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Multi-day projects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS multi_day_projects (
                    id INTEGER PRIMARY KEY,
                    project_name TEXT,
                    description TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    priority TEXT,
                    total_estimated_hours REAL,
                    completion_status REAL DEFAULT 0,
                    created_date TIMESTAMP
                )
            ''')
            
            # Daily capacity and energy profiles
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_profiles (
                    id INTEGER PRIMARY KEY,
                    date TEXT,
                    available_hours REAL,
                    energy_morning REAL,
                    energy_afternoon REAL,
                    energy_evening REAL,
                    focus_capacity REAL,
                    notes TEXT
                )
            ''')
            
            # Multi-day schedule assignments
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS multi_day_assignments (
                    id INTEGER PRIMARY KEY,
                    project_id INTEGER,
                    date TEXT,
                    time_slot TEXT,
                    task_description TEXT,
                    estimated_duration INTEGER,
                    priority TEXT,
                    energy_requirement TEXT,
                    dependencies TEXT,
                    status TEXT DEFAULT 'planned',
                    FOREIGN KEY (project_id) REFERENCES multi_day_projects (id)
                )
            ''')
            
            # Recurring task patterns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS recurring_tasks (
                    id INTEGER PRIMARY KEY,
                    task_name TEXT,
                    description TEXT,
                    frequency TEXT,
                    duration INTEGER,
                    preferred_time TEXT,
                    energy_level TEXT,
                    days_of_week TEXT,
                    start_date TEXT,
                    end_date TEXT,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            conn.commit()
    
    def analyze_multi_day_project(self, project_description: str, deadline_days: int, 
                                estimated_total_hours: float) -> Dict[str, Any]:
        """
        AI Implementation Concept: Project Decomposition
        
        Use AI to break down large projects into manageable daily tasks
        while considering realistic time constraints and dependencies.
        """
        try:
            prompt = f"""
            Analyze this multi-day project for optimal scheduling:
            
            Project: {project_description}
            Deadline: {deadline_days} days from now
            Estimated Total Time: {estimated_total_hours} hours
            
            Please provide a detailed breakdown in JSON format:
            {{
                "project_phases": [
                    {{
                        "phase_name": "Research and Planning",
                        "description": "Detailed phase description",
                        "estimated_hours": 8.0,
                        "priority": "high",
                        "dependencies": [],
                        "optimal_day_range": [1, 3],
                        "daily_tasks": [
                            {{
                                "task": "Specific daily task",
                                "duration_minutes": 120,
                                "energy_required": "high",
                                "best_time_of_day": "morning"
                            }}
                        ]
                    }}
                ],
                "critical_path": ["phase1", "phase2", "phase3"],
                "risk_factors": ["potential delays", "resource constraints"],
                "buffer_recommendations": {{
                    "minimum_buffer_days": 2,
                    "recommended_daily_hours": 3.5,
                    "intensity_distribution": "front-loaded"
                }},
                "success_metrics": ["measurable outcomes", "key milestones"],
                "flexibility_points": ["areas where schedule can be adjusted"]
            }}
            
            Consider realistic work capacity, energy management, and dependency chains.
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                return json.loads(json_match.group())
            else:
                return self.create_fallback_project_breakdown(
                    project_description, deadline_days, estimated_total_hours
                )
                
        except Exception as e:
            print(f"Error in project analysis: {str(e)}")
            return self.create_fallback_project_breakdown(
                project_description, deadline_days, estimated_total_hours
            )
    
    def create_fallback_project_breakdown(self, project: str, days: int, hours: float) -> Dict[str, Any]:
        """Fallback project breakdown if AI analysis fails"""
        daily_hours = hours / max(days - 1, 1)  # Leave 1 day buffer
        
        return {
            "project_phases": [
                {
                    "phase_name": "Planning",
                    "description": f"Plan and organize {project}",
                    "estimated_hours": hours * 0.2,
                    "priority": "high",
                    "dependencies": [],
                    "optimal_day_range": [1, 2],
                    "daily_tasks": [
                        {
                            "task": f"Plan {project} approach",
                            "duration_minutes": int((hours * 0.2) * 60),
                            "energy_required": "high",
                            "best_time_of_day": "morning"
                        }
                    ]
                },
                {
                    "phase_name": "Execution",
                    "description": f"Execute main work for {project}",
                    "estimated_hours": hours * 0.7,
                    "priority": "high",
                    "dependencies": ["Planning"],
                    "optimal_day_range": [2, days-1],
                    "daily_tasks": [
                        {
                            "task": f"Work on {project}",
                            "duration_minutes": int(daily_hours * 60),
                            "energy_required": "medium",
                            "best_time_of_day": "morning"
                        }
                    ]
                },
                {
                    "phase_name": "Review",
                    "description": f"Review and finalize {project}",
                    "estimated_hours": hours * 0.1,
                    "priority": "medium",
                    "dependencies": ["Execution"],
                    "optimal_day_range": [days-1, days],
                    "daily_tasks": [
                        {
                            "task": f"Review and finalize {project}",
                            "duration_minutes": int((hours * 0.1) * 60),
                            "energy_required": "medium",
                            "best_time_of_day": "afternoon"
                        }
                    ]
                }
            ],
            "critical_path": ["Planning", "Execution", "Review"],
            "risk_factors": ["Time constraints", "Scope creep"],
            "buffer_recommendations": {
                "minimum_buffer_days": 1,
                "recommended_daily_hours": daily_hours,
                "intensity_distribution": "even"
            },
            "success_metrics": ["Project completion", "Quality standards met"],
            "flexibility_points": ["Task ordering within phases"]
        }
    
    def generate_week_schedule(self, start_date: date, projects: List[Dict], 
                             recurring_tasks: List[Dict], daily_capacity: Dict) -> Dict[str, Any]:
        """
        AI Implementation Concept: Multi-Dimensional Optimization
        
        Create optimal week schedule balancing multiple projects, recurring tasks,
        energy levels, and capacity constraints.
        """
        try:
            # Prepare data for AI analysis
            schedule_context = {
                "start_date": start_date.isoformat(),
                "projects": projects,
                "recurring_tasks": recurring_tasks,
                "daily_capacity": daily_capacity,
                "week_days": [(start_date + timedelta(days=i)).isoformat() for i in range(7)]
            }
            
            prompt = f"""
            Create an optimized 7-day schedule with the following constraints:
            
            Schedule Context: {json.dumps(schedule_context, indent=2)}
            
            Optimization Goals:
            1. Respect project deadlines and dependencies
            2. Balance daily workload within capacity limits
            3. Optimize for energy levels throughout each day
            4. Include all recurring tasks at preferred times
            5. Provide buffer time for unexpected issues
            6. Minimize context switching between different types of work
            
            Provide schedule in JSON format:
            {{
                "weekly_schedule": {{
                    "2025-01-15": [
                        {{
                            "time": "9:00 AM",
                            "task": "Project A - Planning Phase",
                            "duration": "2 hours",
                            "project_id": "proj_a",
                            "energy_match": "high energy for complex planning",
                            "priority": "high",
                            "type": "project_work"
                        }},
                        {{
                            "time": "11:00 AM",
                            "task": "Daily Email Review",
                            "duration": "30 minutes", 
                            "project_id": "recurring",
                            "energy_match": "medium energy for routine task",
                            "priority": "medium",
                            "type": "recurring"
                        }}
                    ]
                }},
                "optimization_notes": {{
                    "workload_balance": "Even distribution with lighter Friday",
                    "energy_optimization": "High-focus work scheduled for mornings",
                    "risk_mitigation": "Buffer time included each day",
                    "context_switching": "Related tasks grouped together"
                }},
                "weekly_metrics": {{
                    "total_project_hours": 32.5,
                    "recurring_task_hours": 8.5,
                    "buffer_hours": 7.0,
                    "capacity_utilization": "85%"
                }},
                "flexibility_recommendations": [
                    "Tuesday afternoon can accommodate urgent requests",
                    "Friday has extra buffer for week wrap-up"
                ]
            }}
            
            Prioritize realistic scheduling and sustainable work patterns.
            """
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = response.content[0].text.strip()
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            
            if json_match:
                return json.loads(json_match.group())
            else:
                return self.create_fallback_week_schedule(start_date, projects, recurring_tasks)
                
        except Exception as e:
            print(f"Error in week schedule generation: {str(e)}")
            return self.create_fallback_week_schedule(start_date, projects, recurring_tasks)
    
    def create_fallback_week_schedule(self, start_date: date, projects: List[Dict], 
                                    recurring_tasks: List[Dict]) -> Dict[str, Any]:
        """Fallback week schedule if AI generation fails"""
        schedule = {"weekly_schedule": {}}
        
        for i in range(7):
            current_date = (start_date + timedelta(days=i)).isoformat()
            daily_tasks = []
            
            # Add morning project work
            if projects:
                daily_tasks.append({
                    "time": "9:00 AM",
                    "task": f"{projects[0].get('project_name', 'Project Work')} - Daily Progress",
                    "duration": "2 hours",
                    "project_id": projects[0].get('id', 'project_1'),
                    "energy_match": "high energy morning work",
                    "priority": "high",
                    "type": "project_work"
                })
            
            # Add recurring tasks
            for task in recurring_tasks:
                if i < len(recurring_tasks):  # Distribute across week
                    daily_tasks.append({
                        "time": task.get('preferred_time', '2:00 PM'),
                        "task": task.get('task_name', 'Recurring Task'),
                        "duration": f"{task.get('duration', 30)} minutes",
                        "project_id": "recurring",
                        "energy_match": "medium energy routine work",
                        "priority": "medium",
                        "type": "recurring"
                    })
            
            schedule["weekly_schedule"][current_date] = daily_tasks
        
        schedule.update({
            "optimization_notes": {
                "workload_balance": "Basic distribution applied",
                "energy_optimization": "Morning focus work scheduled",
                "risk_mitigation": "Standard buffer included",
                "context_switching": "Grouped by task type"
            },
            "weekly_metrics": {
                "total_project_hours": 14.0,
                "recurring_task_hours": 6.0,
                "buffer_hours": 8.0,
                "capacity_utilization": "70%"
            },
            "flexibility_recommendations": [
                "Afternoons available for adjustments",
                "Weekend buffer for overflow work"
            ]
        })
        
        return schedule
    
    def create_recurring_task_pattern(self, task_name: str, frequency: str, 
                                    duration: int, preferred_time: str) -> int:
        """Create a new recurring task pattern"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO recurring_tasks 
                (task_name, frequency, duration, preferred_time, energy_level, start_date)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (task_name, frequency, duration, preferred_time, 'medium', 
                  datetime.now().isoformat()))
            conn.commit()
            return cursor.lastrowid
    
    def delete_recurring_task(self, task_id: int) -> bool:
        """Delete a recurring task by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM recurring_tasks WHERE id = ?', (task_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def update_recurring_task(self, task_id: int, updates: Dict[str, Any]) -> bool:
        """Update a recurring task"""
        if not updates:
            return False
            
        set_clauses = []
        values = []
        
        for key, value in updates.items():
            if key in ['task_name', 'description', 'frequency', 'duration', 
                      'preferred_time', 'energy_level', 'days_of_week', 'is_active']:
                set_clauses.append(f"{key} = ?")
                values.append(value)
        
        if not set_clauses:
            return False
            
        values.append(task_id)
        query = f"UPDATE recurring_tasks SET {', '.join(set_clauses)} WHERE id = ?"
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0
    
    def save_multi_day_project(self, project_data: Dict[str, Any], 
                              analysis: Dict[str, Any]) -> int:
        """Save multi-day project and its breakdown"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Save main project
            cursor.execute('''
                INSERT INTO multi_day_projects 
                (project_name, description, start_date, end_date, priority, 
                 total_estimated_hours, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                project_data['name'],
                project_data['description'],
                project_data['start_date'],
                project_data['end_date'],
                project_data.get('priority', 'medium'),
                project_data.get('estimated_hours', 0),
                datetime.now()
            ))
            
            project_id = cursor.lastrowid
            
            # Save daily task assignments
            current_date = datetime.fromisoformat(project_data['start_date']).date()
            end_date = datetime.fromisoformat(project_data['end_date']).date()
            
            for phase in analysis.get('project_phases', []):
                phase_start_day = phase.get('optimal_day_range', [1, 1])[0] - 1
                assignment_date = current_date + timedelta(days=phase_start_day)
                
                for daily_task in phase.get('daily_tasks', []):
                    if assignment_date <= end_date:
                        cursor.execute('''
                            INSERT INTO multi_day_assignments
                            (project_id, date, task_description, estimated_duration, 
                             priority, energy_requirement, time_slot)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            project_id,
                            assignment_date.isoformat(),
                            daily_task.get('task', 'Project work'),
                            daily_task.get('duration_minutes', 60),
                            phase.get('priority', 'medium'),
                            daily_task.get('energy_required', 'medium'),
                            daily_task.get('best_time_of_day', 'morning')
                        ))
                        
                        assignment_date += timedelta(days=1)
            
            conn.commit()
            return project_id
    
    def delete_multi_day_project(self, project_id: int) -> bool:
        """Delete a multi-day project and all its assignments"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete project assignments first (foreign key constraint)
            cursor.execute('DELETE FROM multi_day_assignments WHERE project_id = ?', (project_id,))
            
            # Delete the project
            cursor.execute('DELETE FROM multi_day_projects WHERE id = ?', (project_id,))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def update_project_completion(self, project_id: int, completion_percentage: float) -> bool:
        """Update project completion status"""
        completion_percentage = max(0.0, min(1.0, completion_percentage))  # Clamp between 0 and 1
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE multi_day_projects 
                SET completion_status = ? 
                WHERE id = ?
            ''', (completion_percentage, project_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_projects_in_period(self, start_date: date, end_date: date) -> List[Dict]:
        """Get all projects active in the specified period"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, project_name, description, start_date, end_date, 
                       priority, total_estimated_hours, completion_status
                FROM multi_day_projects
                WHERE start_date <= ? AND end_date >= ?
                ORDER BY priority DESC, start_date ASC
            ''', (end_date.isoformat(), start_date.isoformat()))
            
            projects = []
            for row in cursor.fetchall():
                projects.append({
                    'id': row[0],
                    'project_name': row[1],
                    'description': row[2],
                    'start_date': row[3],
                    'end_date': row[4],
                    'priority': row[5],
                    'total_estimated_hours': row[6],
                    'completion_status': row[7]
                })
            
            return projects
    
    def get_project_by_id(self, project_id: int) -> Optional[Dict]:
        """Get a specific project by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, project_name, description, start_date, end_date, 
                       priority, total_estimated_hours, completion_status, created_date
                FROM multi_day_projects
                WHERE id = ?
            ''', (project_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'project_name': row[1],
                    'description': row[2],
                    'start_date': row[3],
                    'end_date': row[4],
                    'priority': row[5],
                    'total_estimated_hours': row[6],
                    'completion_status': row[7],
                    'created_date': row[8]
                }
            return None
    
    def get_recurring_tasks(self) -> List[Dict]:
        """Get all active recurring tasks"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, task_name, description, frequency, duration, 
                       preferred_time, energy_level, days_of_week
                FROM recurring_tasks
                WHERE is_active = TRUE
                ORDER BY task_name ASC
            ''')
            
            tasks = []
            for row in cursor.fetchall():
                tasks.append({
                    'id': row[0],
                    'task_name': row[1],
                    'description': row[2],
                    'frequency': row[3],
                    'duration': row[4],
                    'preferred_time': row[5],
                    'energy_level': row[6],
                    'days_of_week': row[7]
                })
            
            return tasks
    
    def get_recurring_task_by_id(self, task_id: int) -> Optional[Dict]:
        """Get a specific recurring task by ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, task_name, description, frequency, duration, 
                       preferred_time, energy_level, days_of_week, 
                       start_date, end_date, is_active
                FROM recurring_tasks
                WHERE id = ?
            ''', (task_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'task_name': row[1],
                    'description': row[2],
                    'frequency': row[3],
                    'duration': row[4],
                    'preferred_time': row[5],
                    'energy_level': row[6],
                    'days_of_week': row[7],
                    'start_date': row[8],
                    'end_date': row[9],
                    'is_active': row[10]
                }
            return None
    
    def save_weekly_schedule(self, schedule_data: Dict[str, Any], 
                           start_date: date) -> int:
        """Save complete weekly schedule"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Save to saved_schedules table for compatibility
            schedule_name = f"Weekly Schedule {start_date.strftime('%Y-%m-%d')}"
            cursor.execute('''
                INSERT INTO saved_schedules (schedule_name, schedule_data, created_date, task_count)
                VALUES (?, ?, ?, ?)
            ''', (
                schedule_name,
                json.dumps(schedule_data),
                datetime.now(),
                sum(len(daily_tasks) for daily_tasks in schedule_data['weekly_schedule'].values())
            ))
            
            return cursor.lastrowid