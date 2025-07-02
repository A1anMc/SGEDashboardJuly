import React, { useState } from 'react';
import { useSession } from 'next-auth/react';
import { format } from 'date-fns';

interface Comment {
  id: number;
  content: string;
  user_id: number;
  created_at: string;
  updated_at: string;
  mentions: number[];
  reactions: Record<string, number[]>;
  replies: Comment[];
}

interface CommentThreadProps {
  comments: Comment[];
  taskId: number;
  onCommentAdded: () => void;
}

interface CommentFormProps {
  taskId: number;
  parentId?: number;
  onCommentAdded: () => void;
  onCancel?: () => void;
}

const CommentForm: React.FC<CommentFormProps> = ({ taskId, parentId, onCommentAdded, onCancel }) => {
  const [content, setContent] = useState('');
  const { data: session } = useSession();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    try {
      const response = await fetch('/api/comments', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.accessToken}`,
        },
        body: JSON.stringify({
          task_id: taskId,
          parent_id: parentId,
          content: content.trim(),
        }),
      });

      if (response.ok) {
        setContent('');
        onCommentAdded();
        onCancel?.();
      }
    } catch (error) {
      console.error('Failed to add comment:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-2">
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="Write a comment..."
        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500"
        rows={3}
      />
      <div className="flex space-x-2">
        <button
          type="submit"
          className="px-4 py-2 text-white bg-blue-500 rounded-md hover:bg-blue-600"
        >
          Post
        </button>
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300"
          >
            Cancel
          </button>
        )}
      </div>
    </form>
  );
};

const SingleComment: React.FC<{ comment: Comment; taskId: number; onCommentAdded: () => void }> = ({
  comment,
  taskId,
  onCommentAdded,
}) => {
  const [isReplying, setIsReplying] = useState(false);
  const [showReplies, setShowReplies] = useState(false);
  const { data: session } = useSession();

  const handleReaction = async (emoji: string, action: 'add' | 'remove') => {
    try {
      await fetch(`/api/comments/${comment.id}/reaction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.accessToken}`,
        },
        body: JSON.stringify({ emoji, action }),
      });
      onCommentAdded();
    } catch (error) {
      console.error('Failed to update reaction:', error);
    }
  };

  return (
    <div className="mt-4 space-y-2">
      <div className="flex items-start space-x-3 bg-gray-50 p-4 rounded-lg">
        <div className="flex-grow">
          <div className="flex items-center space-x-2">
            <span className="font-medium">User {comment.user_id}</span>
            <span className="text-gray-500 text-sm">
              {format(new Date(comment.created_at), 'MMM d, yyyy h:mm a')}
            </span>
          </div>
          <p className="mt-2 text-gray-700">{comment.content}</p>
          
          {/* Reactions */}
          <div className="flex items-center space-x-2 mt-2">
            {Object.entries(comment.reactions).map(([emoji, users]) => (
              <button
                key={emoji}
                onClick={() => handleReaction(emoji, users.includes(session?.user?.id || 0) ? 'remove' : 'add')}
                className={`px-2 py-1 rounded-full text-sm ${
                  users.includes(session?.user?.id || 0) ? 'bg-blue-100' : 'bg-gray-100'
                }`}
              >
                {emoji} {users.length}
              </button>
            ))}
            <button
              onClick={() => handleReaction('👍', '👍' in comment.reactions ? 'remove' : 'add')}
              className="px-2 py-1 bg-gray-100 rounded-full text-sm hover:bg-gray-200"
            >
              👍
            </button>
          </div>

          <div className="flex items-center space-x-4 mt-2">
            <button
              onClick={() => setIsReplying(!isReplying)}
              className="text-sm text-blue-500 hover:text-blue-600"
            >
              Reply
            </button>
            {comment.replies.length > 0 && (
              <button
                onClick={() => setShowReplies(!showReplies)}
                className="text-sm text-gray-500 hover:text-gray-600"
              >
                {showReplies ? 'Hide' : 'Show'} {comment.replies.length} replies
              </button>
            )}
          </div>
        </div>
      </div>

      {isReplying && (
        <div className="ml-8">
          <CommentForm
            taskId={taskId}
            parentId={comment.id}
            onCommentAdded={onCommentAdded}
            onCancel={() => setIsReplying(false)}
          />
        </div>
      )}

      {showReplies && comment.replies.length > 0 && (
        <div className="ml-8">
          {comment.replies.map((reply) => (
            <SingleComment
              key={reply.id}
              comment={reply}
              taskId={taskId}
              onCommentAdded={onCommentAdded}
            />
          ))}
        </div>
      )}
    </div>
  );
};

const CommentThread: React.FC<CommentThreadProps> = ({ comments, taskId, onCommentAdded }) => {
  return (
    <div className="space-y-4">
      <CommentForm taskId={taskId} onCommentAdded={onCommentAdded} />
      {comments.map((comment) => (
        <SingleComment
          key={comment.id}
          comment={comment}
          taskId={taskId}
          onCommentAdded={onCommentAdded}
        />
      ))}
    </div>
  );
};

export default CommentThread; 