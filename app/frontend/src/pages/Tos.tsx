import { Card, Center, Container, Stack, Text, Title, Image, Box } from "@mantine/core";

export default function Tos() {
    return (
        <Box bg='gray.1' mih='100vh' m={0} p={0}>
            <Container size='md'>
                <Center py='lg'>
                    <Image maw={100} src="/imgs/anova_logo.png" alt="Anova Logo" pb='xl' />
                </Center>
                <Card>
                    <Box bg='white'>
                        <Card.Section>
                            Anova Terms and Conditions
                        </Card.Section>
                        <Stack>
                            <Title order={2}>Terms of Service</Title>
                            <Text>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                            </Text>
                            <Text>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                            </Text>
                            <Text>
                                Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
                            </Text>
                        </Stack>
                    </Box>
                </Card>
            </Container>
        </Box>
    )
}