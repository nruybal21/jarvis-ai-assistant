# jarvis-ai-assistant
Personal AI productivity assistant built with Claude API
# Jarvis AI Assistant

A personal AI productivity assistant powered by Claude API that helps manage tasks, emails, meetings, and provides intelligent time management suggestions.

## 🎯 Project Goals

This project serves as both a practical productivity tool and a learning journey into AI integration. Built while learning AI development fundamentals, it demonstrates:

- **AI API Integration** with Anthropic's Claude
- **Natural Language Processing** for task analysis
- **Intelligent Scheduling** based on productivity patterns
- **Data Management** with SQLite for persistent memory
- **Email & Calendar Integration** (Office 365/Outlook)

## 🚀 Features

### Current (v0.1)
- ✅ **Intelligent Task Analysis** - Claude analyzes tasks and suggests optimal timing
- ✅ **Smart Scheduling** - Creates daily schedules based on energy levels and priorities  
- ✅ **Database Memory** - Remembers patterns and preferences over time
- ✅ **Daily Check-ins** - Personalized productivity insights

### In Development (v0.2)
- 🔄 **Email Intelligence** - Automatic email categorization and action item extraction
- 🔄 **Meeting Assistant** - Pre-meeting briefs and post-meeting follow-ups
- 🔄 **Time Tracking** - Automatic productivity pattern recognition
- 🔄 **Proactive Suggestions** - AI recommendations based on schedule and energy

### Planned (v0.3+)
- 📋 **Voice Interface** - Voice commands and responses
- 📊 **Analytics Dashboard** - Productivity insights and trends
- 🔗 **Multi-platform Integration** - Slack, Teams, project management tools
- 📱 **Mobile Notifications** - Cross-platform reminders and updates

## 🛠️ Tech Stack

- **AI Integration**: Anthropic Claude API
- **Language**: Python 3.11+
- **Database**: SQLite (with future PostgreSQL migration)
- **Email/Calendar**: Microsoft Graph API (Office 365)
- **Task Scheduling**: Python `schedule` library
- **Data Analysis**: Pandas (for productivity pattern analysis)

## 📁 Project Structure

```
jarvis-ai-assistant/
├── src/                    # Main application code
│   ├── basic_jarvis.py    # Core AI intelligence functions
│   ├── database.py        # Database operations and memory
│   └── test_claude.py     # API connection testing
├── config/                # Configuration and credentials
│   └── credentials.py     # API keys (not in git)
├── data/                  # Database and logs
│   └── jarvis.db         # SQLite database (not in git)
├── tests/                 # Unit tests
└── README.md             # This file
```

## 🚦 Getting Started

### Prerequisites
- Python 3.11 or higher
- Anthropic Claude API key ([get one here](https://console.anthropic.com))
- Git for version control

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/jarvis-ai-assistant.git
   cd jarvis-ai-assistant
   ```

2. **Install dependencies**
   ```bash
   pip install anthropic python-dotenv
   ```

3. **Set up credentials**
   ```bash
   # Create config/credentials.py with your API key
   echo 'CLAUDE_API_KEY = "your_api_key_here"' > config/credentials.py
   ```

4. **Test the connection**
   ```bash
   python src/test_claude.py
   ```

5. **Try the basic assistant**
   ```bash
   python src/basic_jarvis.py
   ```

## 📖 Usage Examples

### Task Analysis
```python
# Ask Jarvis to analyze a task
jarvis.analyze_task("Study machine learning for 1 hour")

# Returns structured analysis:
# - Optimal timing suggestions
# - Preparation steps needed  
# - Success criteria
# - Estimated duration refinement
```

### Smart Scheduling
```python
# Create an optimized schedule
tasks = ["Check emails", "Python practice", "Team meeting prep"]
schedule = jarvis.suggest_schedule(tasks)

# Returns time-blocked schedule with:
# - Energy-matched task placement
# - Buffer time between activities
# - Productivity optimization tips
```

## 📊 Learning Progress

This project tracks my journey learning AI integration:

- **Week 1**: Basic Claude API integration ✅
- **Week 2**: Database design and task management ✅  
- **Week 3**: Email processing intelligence 🔄
- **Week 4**: Meeting and calendar integration 📋
- **Week 5+**: Advanced pattern recognition and prediction 📋

## 🤝 Contributing

This is primarily a personal learning project, but feedback and suggestions are welcome! Areas where I'm actively learning:

- AI prompt engineering best practices
- Scalable system architecture
- Production deployment strategies
- Advanced natural language processing

## 📄 License

MIT License - feel free to use this code for your own learning projects.

## 🙏 Acknowledgments

- **Anthropic Claude** for the AI capabilities
- **AI Integration community** for guidance and best practices
- **Open source contributors** whose projects inspired this approach

---

*Built as part of my journey to become an AI Integration Specialist. Follow along as I learn to bridge AI capabilities with real-world productivity needs.*
