import React, { useReducer } from 'react';
import { Task, User } from '../../types/models';
import { format } from 'date-fns';

interface TaskListProps {
  tasks: Task[];
  users: User[];
  onEdit: (task: Task) => void;
  onDelete: (taskId: string) => void;
  onStatusChange: (taskId: string, status: Task['status']) => void;
}

const priorityColors = {
  low: 'bg-green-100 text-green-800',
  medium: 'bg-yellow-100 text-yellow-800',
  high: 'bg-red-100 text-red-800',
  urgent: 'bg-red-200 text-red-900',
};

const statusColors = {
  todo: 'bg-gray-100 text-gray-800',
  in_progress: 'bg-blue-100 text-blue-800',
  in_review: 'bg-purple-100 text-purple-800',
  done: 'bg-green-100 text-green-800',
  archived: 'bg-gray-200 text-gray-600',
};

interface State {
  filter: {
    status: string;
    assignee: string;
    search: string;
  };
  sortField: keyof Task;
  sortDirection: 'asc' | 'desc';
}

type Action =
  | { type: 'SET_FILTER'; field: keyof State['filter']; value: string }
  | { type: 'SET_SORT'; field: keyof Task }
  | { type: 'TOGGLE_SORT_DIRECTION' };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case 'SET_FILTER':
      return {
        ...state,
        filter: {
          ...state.filter,
          [action.field]: action.value
        }
      };
    case 'SET_SORT':
      return {
        ...state,
        sortField: action.field,
        sortDirection: 'asc'
      };
    case 'TOGGLE_SORT_DIRECTION':
      return {
        ...state,
        sortDirection: state.sortDirection === 'asc' ? 'desc' : 'asc'
      };
    default:
      return state;
  }
}

export default function TaskList({ tasks, users, onEdit, onDelete, onStatusChange }: TaskListProps) {
  const [state, dispatch] = useReducer(reducer, {
    filter: {
      status: '',
      assignee: '',
      search: '',
    },
    sortField: 'due_date',
    sortDirection: 'asc'
  });

  const handleSort = (field: keyof Task) => {
    if (field === state.sortField) {
      dispatch({ type: 'TOGGLE_SORT_DIRECTION' });
    } else {
      dispatch({ type: 'SET_SORT', field });
    }
  };

  const filteredAndSortedTasks = tasks
    .filter(task => {
      const matchesStatus = !state.filter.status || task.status === state.filter.status;
      const matchesAssignee = !state.filter.assignee || task.assignee_id === state.filter.assignee;
      const matchesSearch = !state.filter.search || 
        task.title.toLowerCase().includes(state.filter.search.toLowerCase()) ||
        task.description?.toLowerCase().includes(state.filter.search.toLowerCase());
      return matchesStatus && matchesAssignee && matchesSearch;
    })
    .sort((a, b) => {
      const aValue = a[state.sortField];
      const bValue = b[state.sortField];
      
      // Handle undefined values
      if (aValue === undefined && bValue === undefined) return 0;
      if (aValue === undefined) return 1;
      if (bValue === undefined) return -1;
      
      if (aValue === bValue) return 0;
      const comparison = aValue > bValue ? 1 : -1;
      return state.sortDirection === 'asc' ? comparison : -comparison;
    });

  const getStatusLabel = (status: string) => {
    const labels = {
      todo: 'To Do',
      in_progress: 'In Progress',
      in_review: 'In Review',
      done: 'Done',
      archived: 'Archived',
    };
    return labels[status as keyof typeof labels] || status;
  };

  const getPriorityLabel = (priority: string) => {
    const labels = {
      low: 'Low',
      medium: 'Medium',
      high: 'High',
      urgent: 'Urgent',
    };
    return labels[priority as keyof typeof labels] || priority;
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-wrap gap-4 bg-white p-4 rounded-lg shadow">
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="Search tasks..."
            value={state.filter.search}
            onChange={(e) => dispatch({ type: 'SET_FILTER', field: 'search', value: e.target.value })}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
        </div>
        <select
          value={state.filter.status}
          onChange={(e) => dispatch({ type: 'SET_FILTER', field: 'status', value: e.target.value })}
          className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          data-testid="status-filter"
        >
          <option value="">All Statuses</option>
          <option value="todo">To Do</option>
          <option value="in_progress">In Progress</option>
          <option value="in_review">In Review</option>
          <option value="done">Done</option>
          <option value="archived">Archived</option>
        </select>
        <select
          value={state.filter.assignee}
          onChange={(e) => dispatch({ type: 'SET_FILTER', field: 'assignee', value: e.target.value })}
          className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          <option value="">All Assignees</option>
          {users.map(user => (
            <option key={user.id} value={user.id}>{user.full_name}</option>
          ))}
        </select>
      </div>

      {/* Task Table */}
      <div className="overflow-x-auto bg-white rounded-lg shadow">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSort('title')}
              >
                Title
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer"
                onClick={() => handleSort('due_date')}
              >
                Due Date
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Priority
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Assignee
              </th>
              <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredAndSortedTasks.map(task => (
              <tr key={task.id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">{task.title}</div>
                  {task.description && (
                    <div className="text-sm text-gray-500">{task.description}</div>
                  )}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {task.due_date ? format(new Date(task.due_date), 'MMM d, yyyy') : '-'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${priorityColors[task.priority]}`}>
                    {getPriorityLabel(task.priority)}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <select
                    value={task.status}
                    onChange={(e) => onStatusChange(task.id, e.target.value as Task['status'])}
                    className={`text-xs rounded-full px-2 py-1 ${statusColors[task.status as keyof typeof statusColors]} border-transparent focus:border-gray-500 focus:ring-0`}
                  >
                    <option value="todo">To Do</option>
                    <option value="in_progress">In Progress</option>
                    <option value="in_review">In Review</option>
                    <option value="done">Done</option>
                    <option value="archived">Archived</option>
                  </select>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm text-gray-900">
                    {users.find(u => u.id === task.assignee_id)?.full_name || '-'}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button
                    onClick={() => onEdit(task)}
                    className="text-indigo-600 hover:text-indigo-900 mr-4"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(task.id)}
                    className="text-red-600 hover:text-red-900"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
} 