'use client';

import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import TaskList from '../../../components/tasks/TaskList';
import TaskForm from '../../../components/tasks/TaskForm';
import { Task, User, Project, CreateTaskRequest, UpdateTaskRequest } from '../../../types/models';
import { tasksApi, usersApi, projectsApi } from '../../../services/api';
import { Dialog } from '@headlessui/react';

export default function TasksPage() {
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | undefined>();
  const queryClient = useQueryClient();

  // Fetch tasks
  const { data: tasks = [], isLoading: isLoadingTasks } = useQuery({
    queryKey: ['tasks'],
    queryFn: async () => {
      const response = await tasksApi.getAll();
      return response.data.data; // First .data is axios response, second .data is ApiResponse
    },
  });

  // Fetch users
  const { data: users = [], isLoading: isLoadingUsers } = useQuery({
    queryKey: ['users'],
    queryFn: async () => {
      const response = await usersApi.getAll();
      return response.data.data; // First .data is axios response, second .data is ApiResponse
    },
  });

  // Fetch projects
  const { data: projects = [], isLoading: isLoadingProjects } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectsApi.getAll();
      return response.data.data; // First .data is axios response, second .data is ApiResponse
    },
  });

  // Create task mutation
  const createTask = useMutation({
    mutationFn: async (data: CreateTaskRequest) => {
      const response = await tasksApi.create(data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      setIsFormOpen(false);
    },
  });

  // Update task mutation
  const updateTask = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: UpdateTaskRequest }) => {
      const response = await tasksApi.update(id, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
      setIsFormOpen(false);
      setSelectedTask(undefined);
    },
  });

  // Delete task mutation
  const deleteTask = useMutation({
    mutationFn: async (id: string) => {
      const response = await tasksApi.delete(id);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tasks'] });
    },
  });

  const handleSubmit = async (data: CreateTaskRequest | UpdateTaskRequest) => {
    if ('id' in data) {
      await updateTask.mutateAsync({ id: data.id, data });
    } else {
      await createTask.mutateAsync(data);
    }
  };

  const handleEdit = (task: Task) => {
    setSelectedTask(task);
    setIsFormOpen(true);
  };

  const handleDelete = async (taskId: string) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      await deleteTask.mutateAsync(taskId);
    }
  };

  const handleStatusChange = async (taskId: string, status: Task['status']) => {
    await updateTask.mutateAsync({
      id: taskId,
      data: {
        id: taskId,
        status
      }
    });
  };

  if (isLoadingTasks || isLoadingUsers || isLoadingProjects) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-lg text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Tasks</h1>
        <button
          onClick={() => {
            setSelectedTask(undefined);
            setIsFormOpen(true);
          }}
          className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2"
        >
          Create Task
        </button>
      </div>

      <TaskList
        tasks={tasks}
        users={users}
        onEdit={handleEdit}
        onDelete={handleDelete}
        onStatusChange={handleStatusChange}
      />

      <Dialog
        open={isFormOpen}
        onClose={() => {
          setIsFormOpen(false);
          setSelectedTask(undefined);
        }}
        className="relative z-50"
      >
        <div className="fixed inset-0 bg-black/30" aria-hidden="true" />

        <div className="fixed inset-0 flex items-center justify-center p-4">
          <Dialog.Panel className="mx-auto max-w-2xl w-full bg-white rounded-xl p-6 shadow-xl">
            <Dialog.Title className="text-lg font-medium leading-6 text-gray-900 mb-4">
              {selectedTask ? 'Edit Task' : 'Create Task'}
            </Dialog.Title>

            <TaskForm
              task={selectedTask}
              users={users}
              projects={projects}
              onSubmit={handleSubmit}
              onCancel={() => {
                setIsFormOpen(false);
                setSelectedTask(undefined);
              }}
            />
          </Dialog.Panel>
        </div>
      </Dialog>
    </div>
  );
} 