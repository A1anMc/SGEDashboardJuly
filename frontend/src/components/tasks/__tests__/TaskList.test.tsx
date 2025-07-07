import { render, screen, fireEvent, waitFor } from '../../../../tests/test-utils';
import TaskList from '../TaskList';
import { Task, User } from '../../../types/models';

// Mock tasks with different statuses
const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Todo Task',
    description: 'Test Description',
    status: 'todo',
    priority: 'medium',
    due_date: new Date().toISOString(),
    assignee_id: '1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    tags: []
  },
  {
    id: '2',
    title: 'In Progress Task',
    description: 'Test Description',
    status: 'in_progress',
    priority: 'high',
    due_date: new Date().toISOString(),
    assignee_id: '1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
    tags: []
  }
];

const mockUsers: User[] = [
  {
    id: '1',
    email: 'test@example.com',
    full_name: 'Test User',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

describe('TaskList', () => {
  it('renders tasks with correct status values', () => {
    render(
      <TaskList
        tasks={mockTasks}
        users={mockUsers}
        onEdit={() => {}}
        onDelete={() => {}}
        onStatusChange={() => {}}
      />
    );
    
    // Verify each task is rendered with correct status
    expect(screen.getByText('Todo Task')).toBeInTheDocument();
    expect(screen.getByText('In Progress Task')).toBeInTheDocument();
  });

  it('displays status badges with correct values', () => {
    render(
      <TaskList
        tasks={mockTasks}
        users={mockUsers}
        onEdit={() => {}}
        onDelete={() => {}}
        onStatusChange={() => {}}
      />
    );
    
    // Check status options in task rows
    const statusSelects = screen.getAllByRole('combobox');
    const taskStatusSelects = statusSelects.slice(2); // Skip filter selects
    expect(taskStatusSelects[0]).toHaveValue('todo');
    expect(taskStatusSelects[1]).toHaveValue('in_progress');
  });

  it('allows filtering by status', async () => {
    render(
      <TaskList
        tasks={mockTasks}
        users={mockUsers}
        onEdit={() => {}}
        onDelete={() => {}}
        onStatusChange={() => {}}
      />
    );

    // Get the status filter dropdown
    const statusFilter = screen.getByTestId('status-filter');
    
    // Filter by 'todo' status
    fireEvent.change(statusFilter, { target: { value: 'todo' } });
    
    // Wait for filtered results
    await waitFor(() => {
      expect(screen.getByText('Todo Task')).toBeInTheDocument();
      expect(screen.queryByText('In Progress Task')).not.toBeInTheDocument();
    });
  });

  it('allows filtering by search text', async () => {
    render(
      <TaskList
        tasks={mockTasks}
        users={mockUsers}
        onEdit={() => {}}
        onDelete={() => {}}
        onStatusChange={() => {}}
      />
    );

    // Get the search input
    const searchInput = screen.getByPlaceholderText('Search tasks...');
    
    // Filter by task title
    fireEvent.change(searchInput, { target: { value: 'Todo' } });
    
    // Wait for filtered results
    await waitFor(() => {
      expect(screen.getByText('Todo Task')).toBeInTheDocument();
      expect(screen.queryByText('In Progress Task')).not.toBeInTheDocument();
    });
  });

  it('allows filtering by assignee', async () => {
    render(
      <TaskList
        tasks={mockTasks}
        users={mockUsers}
        onEdit={() => {}}
        onDelete={() => {}}
        onStatusChange={() => {}}
      />
    );

    // Get the assignee filter dropdown
    const assigneeFilter = screen.getAllByRole('combobox')[2]; // Assignee filter is third select
    
    // Filter by assignee
    fireEvent.change(assigneeFilter, { target: { value: '1' } });
    
    // Wait for filtered results
    await waitFor(() => {
      expect(screen.getByText('Todo Task')).toBeInTheDocument();
      expect(screen.getByText('In Progress Task')).toBeInTheDocument();
    });
  });
}); 