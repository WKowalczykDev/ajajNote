import styled from 'styled-components';

export const Button = styled.button`
  padding: ${props => props.size === 'sm' ? '8px 16px' : '12px 24px'};
  background: ${props => props.variant === 'secondary'
    ? props.theme.colors.bgTertiary
    : props.variant === 'danger'
        ? props.theme.colors.error
        : props.theme.colors.primary};
  color: ${props => props.theme.colors.text};
  border-radius: 8px;
  font-size: ${props => props.size === 'sm' ? '14px' : '16px'};
  font-weight: 500;
  transition: all ${props => props.theme.transitions.fast};
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: center;
  
  &:hover:not(:disabled) {
    background: ${props => props.variant === 'secondary'
    ? props.theme.colors.bgHover
    : props.variant === 'danger'
        ? '#dc2626'
        : props.theme.colors.primaryHover};
    transform: translateY(-1px);
    box-shadow: ${props => props.theme.shadows.md};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;