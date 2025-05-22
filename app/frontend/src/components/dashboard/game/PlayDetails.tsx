import { Stack, Text, Divider } from "@mantine/core";

export interface PlayDetailsProps {
    purpose: string;
    execution: string;
    counter: string;
}

export default function PlayDetails({ purpose, execution, counter }: PlayDetailsProps) {
    return (
        <Stack mt="4" gap='xs'>
            <div>
                <Text fw={500} size="sm" c="dimmed">Purpose</Text>
                <Text>{purpose}</Text>
            </div>
            <Divider my="0" />
            <div>
                <Text fw={500} size="sm" c="dimmed">Execution</Text>
                <Text>{execution}</Text>
            </div>
            <Divider my="0" />
            <div>
                <Text fw={500} size="sm" c="dimmed">Counter</Text>
                <Text>{counter}</Text>
            </div>
        </Stack>
    );
}