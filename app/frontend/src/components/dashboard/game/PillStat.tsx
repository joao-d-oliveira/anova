import { Group, Text, Paper } from "@mantine/core";


export default function PillStat({ label, value }: { label: string, value: string }) {
    return (
        <Paper bg='gray.1' p='2px' radius='md'>
            <Group justify='space-between' gap='0px'>
                <Group justify='center' w='50%'>
                    <Text size='sm' ta='center' pt={'2px'} >
                        {label}
                    </Text>
                </Group>
                <Paper bg='white' w='50%' radius='md'>
                    <Text size='sm' ta='center' pt={'2px'} mb={'0px'}>
                        {value}
                    </Text>
                </Paper>
            </Group>
        </Paper>
    )
}