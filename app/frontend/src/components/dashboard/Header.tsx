import { Anchor, Group, Image, Stack, Text } from "@mantine/core";
import { useLogout, useUser } from "../../mutations";

export default function Header() {
    const { user } = useUser();
    const { logout } = useLogout();

    if (user.isPending) {
        return <div>Loading...</div>;
    }
    return (
        <Group justify="space-between" pt='xs'>
            <Anchor href="/dashboard">
                <Image maw={100} src="/imgs/anova_logo.png" alt="Anova Logo" pb='xl' />
            </Anchor>
            <Stack gap='0' justify='flex-end'>
                <Text>Welcome, {user.data?.name}</Text>
                <Anchor onClick={() => logout.mutate()} fz='sm' ta='right' td="underline">
                    Logout
                </Anchor>
            </Stack>
        </Group>
    );
}