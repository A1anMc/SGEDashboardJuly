import React from 'react';
import { render, screen } from '@testing-library/react';
import Avatar from '../avatar';

describe('Avatar', () => {
  it('renders with email seed', () => {
    render(<Avatar email="test@example.com" />);
    const avatar = screen.getByAltText('Avatar for test@example.com');
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveAttribute('src', expect.stringContaining('test%40example.com'));
  });

  it('renders with name seed', () => {
    render(<Avatar name="John Doe" />);
    const avatar = screen.getByAltText('Avatar for John Doe');
    expect(avatar).toBeInTheDocument();
    expect(avatar).toHaveAttribute('src', expect.stringContaining('John%20Doe'));
  });

  it('renders with correct size classes', () => {
    const { rerender } = render(<Avatar size="sm" />);
    let avatar = screen.getByAltText('Avatar for user');
    expect(avatar).toHaveClass('h-8', 'w-8');

    rerender(<Avatar size="lg" />);
    avatar = screen.getByAltText('Avatar for user');
    expect(avatar).toHaveClass('h-12', 'w-12');
  });

  it('renders with custom className', () => {
    render(<Avatar className="custom-class" />);
    const avatarContainer = screen.getByAltText('Avatar for user').parentElement;
    expect(avatarContainer).toHaveClass('custom-class');
  });

  it('uses default seed when no email or name provided', () => {
    render(<Avatar />);
    const avatar = screen.getByAltText('Avatar for user');
    expect(avatar).toHaveAttribute('src', expect.stringContaining('default'));
  });
}); 