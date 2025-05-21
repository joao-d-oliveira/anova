import { Group, Text, Paper } from "@mantine/core";


export default function PillStat({ label, value }: { label: string, value: string }) {
    return (
        <Paper bg='gray.1' p='2px' radius='md'>
            <Group justify='space-between' gap='0px'>
                <Group justify='center' w='50%'>
                    <Text ta='center'>
                        {label}
                    </Text>
                </Group>
                <Paper bg='white' w='50%' radius='md'>
                    <Text ta='center'>
                        {value}
                    </Text>
                </Paper>
            </Group>
        </Paper>
    )
}