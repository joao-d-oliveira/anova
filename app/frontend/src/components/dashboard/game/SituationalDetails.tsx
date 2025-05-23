import { Stack, Text, Divider } from "@mantine/core";

export interface SituationalDetailsProps {
    purpose: string;
    execution: string;
    adjustment: string;
}

export default function SituationalDetails({ purpose, execution, adjustment }: SituationalDetailsProps) {
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
                <Text fw={500} size="sm" c="dimmed">Adjustment</Text>
                <Text>{adjustment}</Text>
            </div>
        </Stack>
    );
}