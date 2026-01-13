import styled from 'styled-components';

export const Select = styled.select`
  padding: 10px 16px;
  background: ${props => props.theme.colors.bgTertiary};
  border: 1px solid ${props => props.theme.colors.border};
  border-radius: 8px;
  color: ${props => props.theme.colors.text};
  font-size: 14px;
  cursor: pointer;
  transition: all ${props => props.theme.transitions.fast};

  &:focus {
    outline: none;
    border-color: ${props => props.theme.colors.primary};
  }

  option {
    background: ${props => props.theme.colors.bgTertiary};
    color: ${props => props.theme.colors.text};
  }
`;