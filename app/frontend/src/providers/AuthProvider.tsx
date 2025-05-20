import { ReactNode, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../mutations';
import { Center, Loader } from '@mantine/core';
import { Stack } from '@mantine/core';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const navigate = useNavigate();
  const { data: user, isLoading, isError } = useUser();

  useEffect(() => {
    console.log("isLoading", isLoading);
    console.log("isError", isError);
    console.log("user", user);
    if (!isLoading && isError) {
      window.location.href = '/auth/login';
    }
  }, [isLoading, isError, navigate]);

  if (isLoading) {
    return <Stack><Center><Loader type="dots" /></Center></Stack>;
  }

  if (!user) {
    return null;
  }

  return <>{children}</>;
};
