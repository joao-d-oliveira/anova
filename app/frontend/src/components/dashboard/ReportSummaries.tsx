import { Card, Stack, Title, Text, Group, Button } from "@mantine/core";

import { useReportSummaries } from "../../mutations";
import { useEffect } from "react";
import { filledButtonProps } from "../../props/Button";
import { IconReport } from "@tabler/icons-react";

export default function ReportSummaries() {
    const { reportSummaries } = useReportSummaries();

    useEffect(() => {
        console.log(reportSummaries.data);
    }, [reportSummaries.data]);

    return (
        <Stack>
            {reportSummaries.data?.map((summary) => (
                <Card key={summary.id}>
                    <Group justify="space-between">
                        <Stack gap={2}>
                            <Text fw={600} fz={18}>{summary.home_team} vs {summary.away_team}</Text>
                            <Text>{new Date(summary.created_at).toLocaleDateString()}</Text>
                        </Stack>
                        <Button {...filledButtonProps} size='sm' onClick={() => window.location.href = `/dashboard/game-report?game_uuid=${summary.game_uuid}`}>View Report</Button>
                    </Group>
                </Card>
            ))}
        </Stack>
    )
}