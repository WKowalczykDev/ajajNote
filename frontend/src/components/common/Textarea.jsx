import styled from 'styled-components';

export const Textarea = styled.textarea`
  width: 100%;
  padding: 12px 16px;
  background: ${props => props.theme.colors.bgTertiary};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 8px;
  color: ${props => props.theme.colors.text};
  font-size: 14px;
  min-height: 120px;
  resize: vertical;
  transition: all ${props => props.theme.transitions.fast};

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  }

  &::placeholder {
    color: ${props => props.theme.colors.textMuted};
  }
`;