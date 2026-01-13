import styled from 'styled-components';

export const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  animation: fadeIn 0.2s ease;

  @keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
`;

export const ModalContent = styled.div`
  background: ${props => props.theme.colors.bgSecondary};
  border-radius: 12px;
  max-width: ${props => props.maxWidth || '600px'};
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: ${props => props.theme.shadows.xl};
  animation: slideUp 0.3s ease;

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;

export const ModalHeader = styled.div`
  padding: 24px;
  border-bottom: 1px solid ${props => props.theme.colors.border};
  display: flex;
  justify-content: space-between;
  align-items: center;

  h2 {
    font-size: 20px;
    font-weight: 600;
  }
`;

export const ModalBody = styled.div`
  padding: 24px;
`;

export const CloseButton = styled.button`
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: transparent;
  color: ${props => props.theme.colors.textSecondary};
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all ${props => props.theme.transitions.fast};
  font-size: 20px;

  &:hover {
    background: ${props => props.theme.colors.bgHover};
    color: ${props => props.theme.colors.text};
  }
`;
export const EditableTitleInput = styled.input`
    width: 100%;
    padding: 8px 12px;
    border-radius: 8px;
    border: 1px solid ${props => props.theme.colors.border};
    background: ${props => props.theme.colors.bgTertiary};
    outline: none;
    cursor: text;
    transition: border-color 0.2s, box-shadow 0.2s;
    color: white;
    margin-right: 10px;
    &:focus {
        box-shadow: 0 0 0 2px ${props => props.theme.colors.primary}33;
    }
`;

export const EditableTitle = styled.h2`
    cursor: text;
    color: white;
`;
