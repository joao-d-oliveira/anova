import { ReactNode, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useUser } from '../mutations';
import { Center, Loader } from '@mantine/core';
import { Stack } from '@mantine/core';

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const { user } = useUser();

  useEffect(() => {
    console.log("user", user);
    if (user.isError) {
      window.location.href = `/auth/login?message=${encodeURI("You must be logged in to access this page")}&messageType=${encodeURIComponent("error")}`;
    }
  }, [user.isError]);

  if (user.isPending) {
    return <Stack><Center><Loader type="dots" /></Center></Stack>;
  }

  if (user.isPending) {
    return <Loader type="dots" />;
  }

  return <>{children}</>;
};
