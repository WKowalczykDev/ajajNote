import styled from 'styled-components';

export const StatusBadge = styled.span`
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => {
    switch(props.status) {
        case 'pending': return props.theme.colors.warning;
        case 'processed': return props.theme.colors.success;
        case 'failed': return props.theme.colors.error;
        default: return props.theme.colors.warning;
    }
}};
  color: white;
  text-transform: capitalize;
`;