import React from 'react';
import styled from 'styled-components';
import { Button } from '../common/Button';
import { useAuth } from '../../context/AuthContext';

const HeaderContainer = styled.header`
  background: ${props => props.theme.colors.bgSecondary};
  border-bottom: 1px solid ${props => props.theme.colors.border};
  padding: 16px 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Logo = styled.div`
  font-size: 20px;
  font-weight: 700;
  color: ${props => props.theme.colors.primary};
`;

const UserSection = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const UserName = styled.span`
  color: ${props => props.theme.colors.textSecondary};
  font-size: 14px;
`;

export const Header = () => {
    const { user, logout } = useAuth();

    return (
        <HeaderContainer>
            <Logo>ajajNote</Logo>
            <UserSection>
                <UserName>👤 {user?.name}</UserName>
                <Button size="sm" variant="secondary" onClick={logout}>
                    Logout
                </Button>
            </UserSection>
        </HeaderContainer>
    );
};