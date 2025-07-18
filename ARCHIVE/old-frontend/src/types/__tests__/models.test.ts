import { Task, TaskStatus, Tag, User } from '../models';

describe('Type Definitions', () => {
  describe('TaskStatus', () => {
    it('should have the correct status values', () => {
      const validStatuses: TaskStatus[] = ['todo', 'in_progress', 'in_review', 'done', 'archived'];
      
      // This test will fail if TaskStatus type doesn't match these exact values
      validStatuses.forEach(status => {
        const typedStatus: TaskStatus = status;
        expect(typedStatus).toBeDefined();
      });
    });
  });

  describe('Tag Type', () => {
    it('should have id and name properties', () => {
      const tag: Tag = {
        id: '1',
        name: 'test-tag'
      };
      
      expect(tag.id).toBeDefined();
      expect(tag.name).toBeDefined();
    });
  });

  describe('User Type', () => {
    it('should use snake_case for property names', () => {
      const user: User = {
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      
      expect(user.full_name).toBeDefined(); // Should use full_name, not name
      expect(user.created_at).toBeDefined();
      expect(user.updated_at).toBeDefined();
    });
  });

  describe('Task Type', () => {
    it('should have consistent property names', () => {
      const task: Task = {
        id: '1',
        title: 'Test Task',
        description: 'Test Description',
        status: 'todo',
        due_date: new Date().toISOString(),
        assignee_id: '1',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        tags: [{ id: '1', name: 'test-tag' }]
      };
      
      expect(task.due_date).toBeDefined(); // Should use due_date, not dueDate
      expect(task.assignee_id).toBeDefined(); // Should use assignee_id, not assignedTo
      expect(task.tags[0].id).toBeDefined(); // Tags should be objects with id and name
    });
  });
}); 