import secrets
from dash import Dash, html, dcc
import random
from src.discord import DiscordLink
from src.nGraph import nGraph

from src.mj import getRunningJobsForUser
from src.node import NodeType


def random_job(graph: nGraph, userId: str):
    node = graph.random_node()
    DL = DiscordLink()

    if node is None:
        return html.Div([html.H4("No nodes in graph")])

    jobs = getRunningJobsForUser(userId, 20)
    if not jobs:
        return html.Div([html.H4("failed to get running jobs")])

    jobs = jobs.json()

    print("Got recent this many recent jobs: ", len(jobs))
    if len(jobs) >= 7:  # lazy way to deal with delays in the api
        print("Too many jobs running to add a random one")

    # get a random node from graph.nodes
    node = graph.random_node()

    while node is None or not (
        node.type == NodeType.prompt  # or node.type == NodeType.variation
    ):
        node = graph.random_node()

    if node is None:
        return html.Div([html.H4("No nodes in graph")])

    if node.type == NodeType.prompt:
        print("Got random prompt node:", node.id)
        print("Running prompt as random job: " + node.id)
        print(DL.imagine(node.id, node))
        return html.Div([html.H4("Running prompt as random job: " + node.prompt)])

    print("Got random node: " + str(node))

    if len(node.job.image_paths) == 1:  #  upsample
        jobType = "MJ::JOB::variation::1::SOLO"
        jobNumber = 1
    elif len(node.job.image_paths) == 4:  # variation
        jobTypes = ["MJ::JOB::variation::", "MJ::JOB::upsample::"]
        # randomly select a job type from the jobTypes list
        jobType = secrets.choice(jobTypes)
        jobNumber = secrets.choice([1, 2, 3, 4])
        jobType = jobType + str(jobNumber)
    elif node.reference_job_id is not None:  # root node
        jobType = "MJ::JOB::reroll::0::SOLO"
        jobNumber = 0

    print(
        "Running the random job of type: "
        + str(jobType)
        + " with job number: "
        + str(jobNumber)
        + "on node "
        + str(node.id)
    )
    result = DL.runJob(node, jobType)
    if not result:
        return html.Div(
            [
                html.H3(
                    f"Failed to run {jobType} for {node.id}... reason: {result.text}... repeated failures mean you should probably stop"
                )
            ]
        )

    return html.Div([html.H4(f"Added {jobType} job for {node.id}")])
