import { type PaginationMode } from '../hooks/usePagination';
import './PaginationModeSelector.css';

interface PaginationModeSelectorProps {
  currentMode: PaginationMode;
  onModeChange: (mode: PaginationMode) => void;
  totalItems: number;
}

const PaginationModeSelector = ({
  currentMode,
  onModeChange,
  totalItems
}: PaginationModeSelectorProps) => {
  const modes: Array<{
    value: PaginationMode;
    label: string;
    description: string;
    icon: string;
    recommended: boolean;
  }> = [
    {
      value: 'infinite',
      label: 'Infinite Scroll',
      description: 'Automatically load more as you scroll',
      icon: '📜',
      recommended: true
    },
    {
      value: 'load-more',
      label: 'Load More',
      description: 'Click to load more articles',
      icon: '⬇️',
      recommended: false
    },
    {
      value: 'pagination',
      label: 'Pages',
      description: 'Navigate through numbered pages',
      icon: '📄',
      recommended: false
    }
  ];

  return (
    <div className="pagination-mode-selector">
      <div className="mode-selector-header">
        <h3>Display Mode</h3>
        <span className="total-items">{totalItems} articles</span>
      </div>
      
      <div className="mode-options">
        {modes.map((mode) => (
          <button
            key={mode.value}
            onClick={() => onModeChange(mode.value)}
            className={`mode-option ${currentMode === mode.value ? 'active' : ''}`}
            aria-label={`Switch to ${mode.label} mode`}
          >
            <div className="mode-icon">{mode.icon}</div>
            <div className="mode-content">
              <div className="mode-header">
                <span className="mode-label">{mode.label}</span>
                {mode.recommended && (
                  <span className="recommended-badge">Recommended</span>
                )}
              </div>
              <span className="mode-description">{mode.description}</span>
            </div>
            <div className="mode-check">
              {currentMode === mode.value && '✓'}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default PaginationModeSelector; 