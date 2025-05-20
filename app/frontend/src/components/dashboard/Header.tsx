import { Anchor, Group, Image, Stack, Text } from "@mantine/core";
import { useUser } from "../../mutations";

export default function Header() {
    const { data: user } = useUser();
    if (!user) {
        return <div>Loading...</div>;
    }
    return (
        <Group justify="space-between" py='md'>
                <Image maw={100} src="/imgs/anova_logo.png" alt="Anova Logo" pb='xl' />
                <Stack gap='0' justify='flex-end'>
                    <Text>Welcome, {user.email}</Text>
                    <Anchor href="/auth/logout">
                        Logout
                    </Anchor>
                </Stack>
            </Group>
    );
}