import { Stack, Title, Text, Card, Divider, Grid, Group, Space } from "@mantine/core";
import { TeamAnalysisResponse, GameSimulationResponse } from "../../../generated/client";
import PlayDetails from "./PlayDetails";


export default function Playbook({ gameSimulation, teamAnalysis, opponentAnalysis }: { gameSimulation: GameSimulationResponse, teamAnalysis: TeamAnalysisResponse, opponentAnalysis: TeamAnalysisResponse }) {
    return (
        <>
            <Stack>
                <Title order={3}>Playbook</Title>

                {/* Offensive Plays */}
                <Grid>
                    {gameSimulation.playbook_offensive_plays.slice(0, 3).map((play, index) => (
                        <Grid.Col span={4} key={`offensive-${index}`}>
                            <Card h="100%">
                                <Card.Section>
                                    {play.play_name}
                                </Card.Section>
                                <PlayDetails
                                    purpose={play.purpose}
                                    execution={play.execution}
                                    counter={play.counter}
                                />
                            </Card>
                        </Grid.Col>
                    ))}
                </Grid>

                <Divider my="md" />

                {/* Defensive Plays */}
                <Grid>
                    {gameSimulation.playbook_defensive_plays.slice(0, 3).map((play, index) => (
                        <Grid.Col span={4} key={`defensive-${index}`}>
                            <Card h="100%">
                                <Card.Section>
                                    {play.play_name}
                                </Card.Section>
                                <PlayDetails
                                    purpose={play.purpose}
                                    execution={play.execution}
                                    counter={play.counter}
                                />
                            </Card>
                        </Grid.Col>
                    ))}
                </Grid>

                <Divider my="md" />

                {/* Special Situations */}
                <Title order={4}>Special Situations</Title>
                <Grid>
                    {gameSimulation.playbook_special_situations.slice(0, 2).map((play, index) => (
                        <Grid.Col span={6} key={`special-${index}`}>
                            <Card>
                                <Card.Section>
                                    {play.play_name}
                                </Card.Section>
                                <PlayDetails
                                    purpose={play.purpose}
                                    execution={play.execution}
                                    counter={play.counter}
                                />
                            </Card>
                        </Grid.Col>
                    ))}
                </Grid>

                <Divider my="md" />

                {/* Inbound and After Timeout Plays */}
                <Grid>
                    <Grid.Col span={6}>
                        <Title order={4} mb="md">Inbound Plays</Title>
                        {gameSimulation.playbook_inbound_plays.slice(0, 1).map((play, index) => (
                            <Card key={`inbound-${index}`}>
                                <Card.Section>
                                    {play.play_name}
                                </Card.Section>
                                <PlayDetails
                                    purpose={play.purpose}
                                    execution={play.execution}
                                    counter={play.counter}
                                />
                            </Card>
                        ))}
                    </Grid.Col>
                    <Grid.Col span={6}>
                        <Title order={4} mb="md">After Timeout / Special Scoring Plays</Title>
                        {gameSimulation.playbook_after_timeout_special_plays.slice(0, 1).map((play, index) => (
                            <Card key={`ato-${index}`}>
                                <Card.Section>
                                    {play.play_name}
                                </Card.Section>
                                <PlayDetails
                                    purpose={play.purpose}
                                    execution={play.execution}
                                    counter={play.counter}
                                />
                            </Card>
                        ))}
                    </Grid.Col>
                </Grid>
            </Stack>
            <Space h="256px" />
        </>
    );
}