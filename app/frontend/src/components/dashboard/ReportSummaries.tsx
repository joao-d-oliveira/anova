import { Card, Stack, Title, Text, Group, Button } from "@mantine/core";

import { useDownloadReport, useReportSummaries } from "../../mutations";
import { useEffect } from "react";
import { filledButtonProps, outlineButtonProps } from "../../props/Button";
import { IconDownload, IconReport } from "@tabler/icons-react";

export default function ReportSummaries() {
    const { reportSummaries } = useReportSummaries();
    const { downloadReport } = useDownloadReport();

    useEffect(() => {
        console.log(reportSummaries.data);
    }, [reportSummaries.data]);

    return (
        <Stack>
            {reportSummaries.data?.map((summary) => (
                <Card key={summary.id}>
                    <Group justify="space-between" align="start">
                        <Stack gap={4}>
                            <Text fw={600} fz={22}>{summary.home_team} vs {summary.away_team}</Text>
                            <Text c='dimmed' size='sm'>Created {new Date(summary.created_at).toLocaleDateString()}</Text>
                        </Stack>
                        <Group>
                            <Button {...filledButtonProps} size='sm' onClick={() => window.location.href = `/dashboard/game-report?game_uuid=${summary.game_uuid}`}>View Report</Button>
                            <Button {...outlineButtonProps} size='sm' onClick={() => downloadReport.mutate({ game_uuid: summary.game_uuid })} leftSection={<IconDownload stroke={1.3} size={22} />}>Download</Button>
                        </Group>
                    </Group>
                </Card>
            ))}
        </Stack>
    )
}