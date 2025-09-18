import React from 'react';
import './CategoryFilter.css';

interface CategoryFilterProps {
  selectedCategory: string | null;
  onCategoryChange: (category: string | null) => void;
  className?: string;
}

const CATEGORIES = [
  { key: null, label: 'All', color: 'var(--loud-black)' },
  { key: 'TURBULENCE', label: 'Turbulence', color: 'var(--loud-orange)', icon: '⚠️' },
  { key: 'JETLIFE', label: 'JetLife', color: 'var(--loud-purple)', icon: '✈️' },
  { key: 'AIRSPACE', label: 'Airspace', color: 'var(--loud-orange)', icon: '🌐' },
  { key: 'MISSION', label: 'Mission', color: 'var(--loud-purple)', icon: '🎯' },
  { key: 'ARCHIVE', label: 'Archive', color: 'var(--loud-gray-dark)', icon: '📚' },
  { key: 'NOISE', label: 'Noise', color: 'var(--loud-gray-dark)', icon: '📢' }
];

const CategoryFilter: React.FC<CategoryFilterProps> = ({ 
  selectedCategory, 
  onCategoryChange, 
  className = '' 
}) => {
  return (
    <div className={`category-filter ${className}`}>
      <div className="category-chips">
        {CATEGORIES.map((category) => (
          <button
            key={category.key || 'all'}
            onClick={() => onCategoryChange(category.key)}
            className={`category-chip ${selectedCategory === category.key ? 'active' : ''}`}
            style={{
              '--category-color': category.color
            } as React.CSSProperties}
          >
            {category.icon && <span className="category-icon">{category.icon}</span>}
            <span className="category-label">{category.label}</span>
          </button>
        ))}
      </div>
    </div>
  );
};

export default CategoryFilter;
