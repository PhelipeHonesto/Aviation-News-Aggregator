export interface ErrorInfo {
  message: string;
  suggestion: string;
  retryable: boolean;
  action?: string;
}

export const getErrorInfo = (error: any, context: string): ErrorInfo => {
  const errorMessage = error?.message || error?.toString() || 'An unknown error occurred';
  
  // Network/Connection errors
  if (errorMessage.includes('Failed to fetch') || errorMessage.includes('NetworkError')) {
    return {
      message: 'Connection failed',
      suggestion: 'Please check your internet connection and try again.',
      retryable: true,
      action: 'Retry'
    };
  }
  
  // Backend connection errors
  if (errorMessage.includes('Could not connect to the backend')) {
    return {
      message: 'Backend service unavailable',
      suggestion: 'The server might be down. Please try again in a moment.',
      retryable: true,
      action: 'Retry'
    };
  }
  
  // API errors
  if (errorMessage.includes('500') || errorMessage.includes('Internal Server Error')) {
    return {
      message: 'Server error',
      suggestion: 'Something went wrong on our end. Please try again.',
      retryable: true,
      action: 'Retry'
    };
  }
  
  if (errorMessage.includes('404') || errorMessage.includes('Not Found')) {
    return {
      message: 'Resource not found',
      suggestion: 'The requested resource could not be found.',
      retryable: false
    };
  }
  
  if (errorMessage.includes('403') || errorMessage.includes('Forbidden')) {
    return {
      message: 'Access denied',
      suggestion: 'You don\'t have permission to perform this action.',
      retryable: false
    };
  }
  
  // OpenAI API errors
  if (errorMessage.includes('OPENAI_API_KEY') || errorMessage.includes('OpenAI')) {
    return {
      message: 'AI service unavailable',
      suggestion: 'OpenAI API key is not configured. Please contact your administrator.',
      retryable: false
    };
  }
  
  // Slack errors
  if (errorMessage.includes('SLACK_WEBHOOK_URL') || errorMessage.includes('Slack')) {
    return {
      message: 'Slack integration unavailable',
      suggestion: 'Slack webhook is not configured. Article will be marked as posted locally.',
      retryable: false
    };
  }
  
  // Timeout errors
  if (errorMessage.includes('timeout') || errorMessage.includes('Timeout')) {
    return {
      message: 'Request timed out',
      suggestion: 'The request took too long. Please try again.',
      retryable: true,
      action: 'Retry'
    };
  }
  
  // Default error
  return {
    message: `Error: ${context}`,
    suggestion: 'Please try again. If the problem persists, contact support.',
    retryable: true,
    action: 'Retry'
  };
};

export const isRetryableError = (error: any): boolean => {
  const errorInfo = getErrorInfo(error, '');
  return errorInfo.retryable;
}; 