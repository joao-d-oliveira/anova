import React from "react";
import { Flex, Stack, Title, Text, Anchor } from "@mantine/core";
import { Container } from "@mantine/core";


function Error404() {
    return (
        <Container size="md" py="lg" mih="75vh">
            <Stack gap="md" justify="space-between" h="100%">
                <Flex direction="column" justify="space-between" h="100%">
                    <Flex justify="center">
                        <Title my="md">Not found!</Title>
                    </Flex>
                    <Stack gap="xs" align="center" justify="center">
                        <Text>The page you are looking for does not not seem to exist, where would you like to go?</Text>
                        <Anchor href="/">Home</Anchor>
                        <Anchor href="/auth/signup">Signup</Anchor>
                        <Anchor href="/auth/login">Login</Anchor>
                        <Anchor href="/auth/forgot-password">Forgot Password</Anchor>
                        <Anchor href="/auth/reset-password">Reset Password</Anchor>
                    </Stack>
                </Flex>
            </Stack>
        </Container>
    )
}

export default Error404;