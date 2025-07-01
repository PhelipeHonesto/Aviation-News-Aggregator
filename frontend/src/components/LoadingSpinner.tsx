import './LoadingSpinner.css';

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  className?: string;
}

const LoadingSpinner = ({ size = 'medium', color = '#f17500', className = '' }: LoadingSpinnerProps) => {
  return (
    <div className={`loading-spinner ${size} ${className}`} style={{ '--spinner-color': color } as React.CSSProperties}>
      <div className="spinner-ring"></div>
    </div>
  );
};

export default LoadingSpinner; 
