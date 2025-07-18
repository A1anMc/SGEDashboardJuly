import { render, screen, fireEvent } from '../../../../tests/test-utils';
import TaskForm from '../TaskForm';
import { Task, User, Project } from '../../../types/models';

const mockTask: Task = {
  id: '1',
  title: 'Test Task',
  description: 'Test Description',
  status: 'todo',
  priority: 'medium',
  due_date: new Date().toISOString(),
  assignee_id: '1',
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  tags: []
};

const mockUsers: User[] = [
  {
    id: '1',
    email: 'test@example.com',
    full_name: 'Test User',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

const mockProjects: Project[] = [
  {
    id: '1',
    title: 'Test Project',
    description: 'Test Project Description',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
];

// Mock react-hook-form
jest.mock('react-hook-form', () => ({
  useForm: () => ({
    register: (name: string) => ({
      name,
      onChange: (e: any) => e.target.value,
      onBlur: jest.fn(),
      ref: jest.fn(),
    }),
    handleSubmit: (fn: any) => (e: any) => {
      e.preventDefault();
      fn({
        title: 'New Task',
        priority: 'high',
        status: 'todo',
      });
    },
    formState: { errors: {} },
    setValue: jest.fn(),
    watch: jest.fn().mockReturnValue([]),
  }),
}));

describe('TaskForm', () => {
  it('renders form fields with correct values when editing', () => {
    render(
      <TaskForm
        task={mockTask}
        users={mockUsers}
        projects={mockProjects}
        onSubmit={() => {}}
        onCancel={() => {}}
      />
    );

    // Check if form fields are present
    expect(screen.getByLabelText('Title')).toBeInTheDocument();
    expect(screen.getByLabelText('Description')).toBeInTheDocument();
    expect(screen.getByLabelText('Priority')).toBeInTheDocument();
  });

  it('shows all status options when editing', () => {
    render(
      <TaskForm
        task={mockTask}
        users={mockUsers}
        projects={mockProjects}
        onSubmit={() => {}}
        onCancel={() => {}}
      />
    );

    // Get status select
    const statusSelect = screen.getByLabelText('Status');
    
    // Check all status options are available
    const options = ['To Do', 'In Progress', 'In Review', 'Done', 'Archived'];
    options.forEach(status => {
      expect(screen.getByRole('option', { name: status })).toBeInTheDocument();
    });
  });

  it('submits form with correct data', () => {
    const onSubmit = jest.fn();
    render(
      <TaskForm
        users={mockUsers}
        projects={mockProjects}
        onSubmit={onSubmit}
        onCancel={() => {}}
      />
    );

    // Fill in form fields
    fireEvent.change(screen.getByLabelText('Title'), {
      target: { value: 'New Task' }
    });
    
    fireEvent.change(screen.getByLabelText('Priority'), {
      target: { value: 'high' }
    });

    // Submit form
    fireEvent.click(screen.getByRole('button', { name: /create task/i }));

    // Check if onSubmit was called with correct data
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({
        title: 'New Task',
        priority: 'high',
        status: 'todo' // New tasks should default to 'todo'
      })
    );
  });
}); 