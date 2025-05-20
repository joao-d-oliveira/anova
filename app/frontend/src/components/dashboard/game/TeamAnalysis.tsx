import { Stack, Title, Text, Table} from "@mantine/core";
import { Team, TeamStats } from "../../../generated/client";
import { ProjectedPlayer } from "../../../generated/client";

export default function TeamAnalysis({ team, teamStats, playerStats }: { team: Team, teamStats: TeamStats, playerStats: ProjectedPlayer[] }) {
    return (
        <Stack>
            <Title order={1}>{team.name} Report</Title>
            <Text>
                {team.record}
            </Text>
        </Stack>
    )
}