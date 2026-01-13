import React, { useState } from 'react';
import { AuthContainer, AuthCard, AuthTitle, AuthSubtitle, AuthSwitch } from '../components/auth/AuthStyles';
import { LoginForm } from '../components/auth/LoginForm';
import { SignupForm } from '../components/auth/SignupForm';

export const AuthPage = () => {
    const [isLogin, setIsLogin] = useState(true);

    return (
        <AuthContainer>
            <AuthCard>
                <AuthTitle>{isLogin ? 'Welcome Back' : 'Create Account'}</AuthTitle>
                <AuthSubtitle>
                    {isLogin ? 'Sign in to access your notes' : 'Start transcribing your audio notes'}
                </AuthSubtitle>

                {isLogin ? <LoginForm /> : <SignupForm />}

                <AuthSwitch>
                    {isLogin ? "Don't have an account?" : 'Already have an account?'}
                    <button onClick={() => setIsLogin(!isLogin)}>
                        {isLogin ? 'Sign Up' : 'Sign In'}
                    </button>
                </AuthSwitch>
            </AuthCard>
        </AuthContainer>
    );
};