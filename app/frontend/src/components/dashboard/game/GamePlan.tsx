import { Stack, Title, Text, Table, Card, Divider, Grid, Group, Space, Paper, Box } from "@mantine/core";
import { TeamAnalysisResponse, GameSimulationResponse } from "../../../generated/client";
import StringList from "../StringList";

export default function GamePlan({ gameSimulation, teamAnalysis, opponentAnalysis }: { gameSimulation: GameSimulationResponse, teamAnalysis: TeamAnalysisResponse, opponentAnalysis: TeamAnalysisResponse }) {
    return (
        <>
            <Stack>
                <Title order={3}>Game Plan</Title>
                <Card>
                    <Card.Section>
                        Team keys to Victory
                    </Card.Section>
                    <StringList maxElements={5} text={gameSimulation.sim_success_factors} />
                </Card>
                <Divider my='sm' />
                <Card>
                    <Card.Section>
                        Key Matchups
                    </Card.Section>
                    <StringList text={gameSimulation.sim_key_matchups} />
                </Card>
                <Divider my='sm' />
                <Grid>
                    <Grid.Col span={6}>
                        <Card>
                            <Card.Section>
                                Offensive Keys to Victory
                            </Card.Section>
                            <StringList maxElements={5} text={teamAnalysis.offensive_keys.join('\n')} />
                        </Card>
                    </Grid.Col>
                    <Grid.Col span={6}>
                        <Card>
                            <Card.Section>
                                Defensive Keys to Victory
                            </Card.Section>
                            <StringList maxElements={5} text={opponentAnalysis.defensive_keys.join('\n')} />
                        </Card>
                    </Grid.Col>
                </Grid>
                <Divider my='sm' />
                <Grid>
                    <Grid.Col span={6}>
                        <Card>
                            <Card.Section>
                                Situational Adjustments
                            </Card.Section>
                            <StringList maxElements={5} text={teamAnalysis.situational_adjustments.join('\n')} />
                        </Card>
                    </Grid.Col>
                    <Grid.Col span={6}>
                        <Card>
                            <Card.Section>
                                Rotation Plan
                            </Card.Section>
                            <StringList maxElements={5} text={teamAnalysis.rotation_plan.join('\n')} />
                        </Card>
                    </Grid.Col>
                </Grid>
            </Stack>
            <Space h='256px' />
        </>
    )
}