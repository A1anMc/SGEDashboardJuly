# Task Management System Documentation

## Overview
The task management system is a core component of the SGE Dashboard, providing functionality for tracking tasks, time entries, and comments across projects.

## System Components

### Models

#### Task Model
- Primary model for task management
- Fields:
  - `id`: Integer primary key
  - `title`: String (required)
  - `description`: Text (optional)
  - `status`: Enum ["todo", "in_progress", "in_review", "done", "archived"]
  - `priority`: Enum ["low", "medium", "high", "urgent"]
  - `estimated_hours`: Integer (optional)
  - `actual_hours`: Integer (calculated from time entries)
  - `due_date`: DateTime (optional)
  - `project_id`: Integer (required, foreign key)
  - `creator_id`: Integer (optional, foreign key)
  - `assignee_id`: Integer (optional, foreign key)
  - `tags`: JSON array
  - `attachments`: JSON array
  - Timestamps: `created_at`, `updated_at`, `completed_at`

#### TaskComment Model
- Allows users to comment on tasks with threading and reactions support
- Fields:
  - `id`: Integer primary key
  - `task_id`: Integer (required, foreign key)
  - `user_id`: Integer (required, foreign key)
  - `content`: Text (required)
  - `parent_id`: Integer (optional, foreign key, for threaded comments)
  - `reactions`: JSON dictionary (stores emoji reactions and user counts)
  - Timestamps: `created_at`, `updated_at`

#### TimeEntry Model
- Tracks time spent on tasks
- Fields:
  - `id`: Integer primary key
  - `task_id`: Integer (required, foreign key)
  - `user_id`: Integer (required, foreign key)
  - `duration_minutes`: Integer (required)
  - `description`: Text (optional)
  - `started_at`: DateTime (required)
  - `ended_at`: DateTime (required)
  - `created_at`: DateTime

### API Endpoints

#### Tasks
- `POST /tasks/`: Create a new task
- `GET /tasks/`: List tasks with filters
- `GET /tasks/{task_id}`: Get task details
- `PUT /tasks/{task_id}`: Update task
- `DELETE /tasks/{task_id}`: Delete task

#### Comments
- `POST /tasks/{task_id}/comments`: Add comment to task
- `GET /tasks/{task_id}/comments`: Get all comments for a task
- `POST /tasks/{task_id}/comments/{comment_id}/reply`: Reply to a specific comment
- `POST /tasks/{task_id}/comments/{comment_id}/reactions`: Add/remove reaction to a comment

#### Time Entries
- `POST /tasks/{task_id}/time`: Add time entry to task

### Relationships
- Task → Project (Many-to-One)
- Task → User (Many-to-One for creator and assignee)
- Task → Comments (One-to-Many)
- Task → TimeEntries (One-to-Many)

## Data Validation

### Task Status Validation
- Enforced through SQL CHECK constraints
- Valid values: ["todo", "in_progress", "in_review", "done", "archived"]
- Validated at database level

### Task Priority Validation
- Enforced through SQL CHECK constraints
- Valid values: ["low", "medium", "high", "urgent"]
- Validated at database level

### Time Tracking
- Automatic calculation of actual hours from time entries
- Uses SQLAlchemy event listeners to update task hours
- Maintains consistency between time entries and task total

## Build Issues & Resolutions

### Previous Build Issues
1. **Database Migration Issues**
   - Initial migration used UUID and PostgreSQL-specific features
   - Fixed by using integer IDs and PostgreSQL-compatible constraints

2. **Model Relationship Issues**
   - TeamMember relationship caused circular imports
   - Fixed by removing unnecessary relationships

3. **Time Tracking Calculation**
   - Time entry events weren't updating task hours
   - Fixed by adding SQLAlchemy event listeners

### Current Working Functionality
1. **Task Management**
   - ✅ Create, read, update, delete tasks
   - ✅ Status and priority management
   - ✅ Project assignment
   - ✅ User assignment

2. **Comments**
   - ✅ Add comments to tasks
   - ✅ Track comment history
   - ✅ User attribution
   - ✅ Threaded comments support
   - ✅ Emoji reactions
   - ✅ Proper handling of nested discussions

3. **Time Tracking**
   - ✅ Log time entries
   - ✅ Calculate total time spent
   - ✅ Track start and end times

4. **Data Validation**
   - ✅ Status constraints
   - ✅ Priority constraints
   - ✅ Required field validation

## Testing
All components are tested with pytest:
- Task CRUD operations
- Status updates
- Comment functionality
- Time tracking
- Data constraints
- Cascade deletion

## Integration with Existing System
The task management system integrates with:
- Project management module
- User authentication system
- Frontend dashboard views

## Future Improvements
1. Add task dependencies
2. Implement task templates
3. Add recurring tasks
4. Enhance time tracking with real-time updates
5. Add task analytics and reporting

### Comment Threading
- Comments support a hierarchical structure
- Parent-child relationships allow for nested discussions
- Each comment can:
  - Be a top-level comment (parent_id = null)
  - Be a reply to another comment (parent_id references another comment)
  - Have multiple child comments
  - Track its position in the thread hierarchy

### Reaction System
- Comments support emoji reactions from users
- Functionality:
  - Users can add/remove emoji reactions
  - Each reaction type tracks the count of users
  - Reactions are stored as a mutable dictionary
  - Uses SQLAlchemy's `flag_modified` for proper tracking of dictionary changes
- Implementation:
  - Reactions stored in JSON format: `{"emoji": {"count": number, "users": [user_ids]}}`
  - Automatic initialization of empty reactions dictionary for new comments
  - Proper handling of dictionary mutations in database

## Access Control and Permissions

### Role-Based Access Control
The task management system implements a hierarchical permission system with the following roles:

#### Core Roles
1. **Owner**
   - Created the task
   - Full administrative rights over the task
   - Can delete task and transfer ownership
   - Can modify all task attributes
   - Retains admin rights regardless of reassignment

2. **Assignee**
   - Current task executor
   - Can update task status
   - Can add time entries
   - Can reassign with owner approval
   - Can add/edit their own comments

3. **Follower**
   - Subscribed to task updates
   - Can view task and all comments
   - Can add comments and reactions
   - Receives notifications
   - Cannot modify task attributes

4. **Observer**
   - Read-only access
   - Can view task and comments
   - Can add reactions
   - No modification rights

### Permission Matrix
| Action                    | Owner | Assignee | Follower | Observer |
|--------------------------|-------|----------|----------|----------|
| View Task                | ✅    | ✅       | ✅       | ✅       |
| Create Task              | ✅    | ✅       | ✅       | ❌       |
| Edit Task Details        | ✅    | ✅*      | ❌       | ❌       |
| Delete Task              | ✅    | ❌       | ❌       | ❌       |
| Assign/Reassign          | ✅    | ✅**     | ❌       | ❌       |
| Add Comments             | ✅    | ✅       | ✅       | ❌       |
| Edit Own Comments        | ✅    | ✅       | ✅       | ❌       |
| Delete Any Comment       | ✅    | ❌       | ❌       | ❌       |
| Add Reactions            | ✅    | ✅       | ✅       | ✅       |
| Change Status            | ✅    | ✅       | ❌       | ❌       |
| Add Time Entries         | ✅    | ✅       | ❌       | ❌       |

\* Limited to specific fields
\** Requires owner approval

### Permission Inheritance
- Subtasks inherit parent task permissions by default
- Project-level roles override task-level permissions
- Team leads automatically get owner permissions for their team's tasks

### Integration Points
- Permissions affect notification delivery
- Role-based Slack/Notion visibility
- API endpoint authorization
- Frontend component rendering

## Code Maintenance and Validation

### Cleanup and Validation Script
The project includes a `cleanup_and_validate.py` script that helps maintain code quality and test coverage. This tool:

1. **Code Cleanup**
   - Uses `vulture` to detect unused code
   - Identifies potentially unused Python files
   - Provides interactive confirmation before deletion
   - Logs all cleanup actions

2. **Test Coverage**
   - Runs pytest with coverage reporting
   - Enforces minimum coverage threshold (90%)
   - Generates detailed coverage reports
   - Flags if coverage drops below threshold

### Extended Validation Checks

#### Invalid Code Detection
1. **Syntax Validation**
   - Checks for Python syntax errors
   - Validates import statements
   - Ensures proper function definitions
   - Verifies class hierarchies

2. **Dependency Analysis**
   - Identifies missing package imports
   - Checks for outdated package references
   - Validates package version compatibility
   - Flags removed packages still in use

3. **Route and API Validation**
   - Verifies API endpoint implementations
   - Checks for unused route definitions
   - Validates route parameter types
   - Ensures proper route registration

4. **Module Integration**
   - Checks `__init__.py` references
   - Validates router registrations
   - Verifies CLI command registration
   - Ensures proper module imports

#### Test File Management
- Tracks unused test files
- Validates test coverage mapping
- Ensures test class naming conventions
- Checks for orphaned test fixtures

### Usage
```bash
# Install dependencies
pip install vulture pytest pytest-cov pylint mypy

# Run the cleanup script
python cleanup_and_validate.py

# Additional validation commands
pylint app/     # Syntax and style checking
mypy app/      # Type checking
```

### Script Output
- Creates `vulture_report.txt` with unused code analysis
- Generates `cleanup_log.txt` with:
  - List of deleted files
  - Current test coverage percentage
  - Coverage threshold status
  - Any cleanup warnings or errors
- Produces validation reports:
  - Syntax error log
  - Import validation results
  - Route usage analysis
  - Test coverage mapping

### Configuration
- Base directory: Script's parent directory
- App directory: `app/` subdirectory
- Minimum coverage: 90%
- Log file: `cleanup_log.txt`
- Validation thresholds:
  - Maximum cyclomatic complexity: 10
  - Maximum function length: 50 lines
  - Minimum test coverage per file: 80%

### Best Practices
1. Run the script before major releases
2. Review `vulture_report.txt` carefully before confirming deletions
3. Investigate if coverage drops below threshold
4. Keep cleanup logs for audit trail
5. Address all syntax and import warnings
6. Maintain test coverage for new code
7. Regular dependency audits
8. Review unused route reports 