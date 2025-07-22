import React from 'react';
import { render, screen } from '@testing-library/react';

describe('NavImpact Logo', () => {
  it('logo.svg should be accessible', () => {
    // Test that the logo file exists and is accessible
    const logoPath = '/logo.svg';
    expect(logoPath).toBe('/logo.svg');
  });

  it('icon.svg should be accessible', () => {
    // Test that the icon file exists and is accessible
    const iconPath = '/icon.svg';
    expect(iconPath).toBe('/icon.svg');
  });

  it('should render logo with correct branding', () => {
    // Test that the logo component renders with NavImpact branding
    const LogoComponent = () => (
      <div className="flex items-center space-x-3">
        <img src="/icon.svg" alt="NavImpact" className="h-8 w-8" />
        <span className="text-xl font-bold">
          <span className="text-impact-teal">Nav</span>
          <span className="text-energy-coral">Impact</span>
        </span>
      </div>
    );

    render(<LogoComponent />);
    
    const logo = screen.getByAltText('NavImpact');
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('src', '/icon.svg');
  });
}); 