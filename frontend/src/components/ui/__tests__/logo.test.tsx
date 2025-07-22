import React from 'react';
import { render, screen } from '@testing-library/react';
import Logo from '../logo';

describe('NavImpact Logo Component', () => {
  it('renders full logo by default', () => {
    render(<Logo />);
    
    const logo = screen.getByAltText('NavImpact');
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('src', '/icon.svg');
    
    // Check for text content
    expect(screen.getByText('Nav')).toBeInTheDocument();
    expect(screen.getByText('Impact')).toBeInTheDocument();
  });

  it('renders icon-only variant', () => {
    render(<Logo variant="icon" />);
    
    const logo = screen.getByAltText('NavImpact');
    expect(logo).toBeInTheDocument();
    
    // Should not have text content
    expect(screen.queryByText('Nav')).not.toBeInTheDocument();
    expect(screen.queryByText('Impact')).not.toBeInTheDocument();
  });

  it('renders with different sizes', () => {
    const { rerender } = render(<Logo size="sm" />);
    let logo = screen.getByAltText('NavImpact');
    expect(logo).toHaveClass('h-6', 'w-6');
    
    rerender(<Logo size="lg" />);
    logo = screen.getByAltText('NavImpact');
    expect(logo).toHaveClass('h-12', 'w-12');
  });

  it('renders as link when href provided', () => {
    render(<Logo href="/dashboard" />);
    
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/dashboard');
  });

  it('applies custom className', () => {
    render(<Logo className="custom-class" />);
    
    const container = screen.getByAltText('NavImpact').closest('div')?.parentElement;
    expect(container).toHaveClass('custom-class');
  });

  it('has animation classes', () => {
    render(<Logo />);
    
    const container = screen.getByAltText('NavImpact').closest('div')?.parentElement;
    expect(container).toHaveClass('transition-all', 'duration-300', 'hover:scale-105');
  });
}); 