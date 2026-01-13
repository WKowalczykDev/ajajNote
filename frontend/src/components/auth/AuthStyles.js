import styled from 'styled-components';

export const AuthContainer = styled.div`
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
`;

export const AuthCard = styled.div`
  background: ${props => props.theme.colors.bgSecondary};
  border-radius: 16px;
  padding: 40px;
  width: 100%;
  max-width: 440px;
  box-shadow: ${props => props.theme.shadows.xl};
`;

export const AuthTitle = styled.h1`
  font-size: 28px;
  font-weight: 700;
  margin-bottom: 8px;
  text-align: center;
`;

export const AuthSubtitle = styled.p`
  color: ${props => props.theme.colors.textSecondary};
  text-align: center;
  margin-bottom: 32px;
`;

export const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

export const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

export const Label = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: ${props => props.theme.colors.textSecondary};
`;

export const ErrorMessage = styled.div`
  padding: 12px;
  background: ${props => props.theme.colors.error}20;
  border: 1px solid ${props => props.theme.colors.error};
  border-radius: 8px;
  color: ${props => props.theme.colors.error};
  font-size: 14px;
  margin-bottom: 16px;
`;

export const AuthSwitch = styled.div`
  text-align: center;
  margin-top: 24px;
  color: ${props => props.theme.colors.textSecondary};
  font-size: 14px;

  button {
    color: ${props => props.theme.colors.primary};
    background: none;
    padding: 0;
    margin-left: 4px;
    font-weight: 500;
    
    &:hover {
      text-decoration: underline;
    }
  }
`;