import { Card, Divider, Text } from "@mantine/core";
import { TeamAnalysisResponse } from "../../../generated/client";

export default function KeyStats({team_name, team_analysis}: {team_name: string, team_analysis: TeamAnalysisResponse}) {
    return (
        <Card h="100%">
            <Card.Section>
                {team_name} Key Stats
            </Card.Section>
            <>
                {team_analysis.strengths.slice(0, 3).map((line, index) => (
                    <>
                        {index > 0 && <Divider />}
                        <Text py='xs' key={index}>{line}</Text>
                    </>
                ))}
            </>
        </Card>
    )
}