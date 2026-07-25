import asyncio
import logging
import string
import uuid
from typing import Final

import pydantic_ai
import teyuna_sdk
from pydantic_ai import messages

import settings

from . import capabilities

logger = logging.getLogger(__name__)


class Agent:
    _nickname: Final[str] = "J Mario"

    _instructions: Final[string.Template] = string.Template(
        """
        You are playing Teyuna (a Catan-like game) as the player named
        "$nickname". That exact nickname is how you appear in game state;
        identify yourself by it when reading players, turns, and scores.
        Your goal is to reach 10 victory points before your opponents.\n\n
        ## Turn discipline\n
        Each tick: read the current game state, then act only when required.\n
        - If the lobby is waiting for players or it is not your turn, do not
        force actions; briefly note that you are waiting.\n
        - When it is your turn (or you must discard / move the conquistador /
        resolve a special phase), take one coherent set of legal actions for
        the current phase, then stop.\n
        - Prefer legal, high-value moves. If a request returns 400, read the
        error detail, correct the payload, and retry once if still useful.\n
        - Do not spam the same failed actions.\n\n
        ## Actions\n
        Use `get_game_state` / `get_hand` first, then `submit_action` with a
        payload that matches the tool schema. Coordinates are `[q, r, d]`.\n
        Phase → kind:\n
        - `first placement` / `second placement` → `free_placement`\n
        - `dice roll` → `advance` (or play a wisdom card)\n
        - `discard resources` → `discard_resources`\n
        - `move conquistator` → `move_conquistator`\n
        - `trade and build` → build / trade / buy, then `advance`\n
        - `end game` → stop; do not submit further actions\n\n
        ## Strategy (keep it practical)\n
        - Opening placements: favor vertices with diverse, high-probability
        resource numbers; attach a legal adjacent path.\n
        - During trade & build: spend resources on paths/terraces/great
        terraces/wisdom cards that increase VP or board position before ending
        the turn with `advance`.\n
        - Trade when it clearly helps a near-term build; decline or ignore
        bad offers.\n
        - On a 7: discard correctly if required, then place the conquistator
        to block strong opponents and steal when allowed.\n
        - Track your VP and play toward 10; stop when the phase is `end game`.\n\n
        ## Rulebook\n$rulebook
        """
    )

    def __init__(self, settings_: settings.Settings):
        self._settings = settings_
        self._agent = self._build_agent()

    def _build_agent(self) -> pydantic_ai.Agent[capabilities.PlayerDependencies]:
        rulebook = self._settings.rulebook.read_text()

        # TODO: instantiate the agent with the instructions and the
        # tools that enable the agent to talk to the Teyuna API.
        ## homework:start
        agent = pydantic_ai.Agent()
        ## homework:end
        return agent

    async def loop(
        self,
        *,
        game_id: uuid.UUID,
        base_url: str,
    ) -> None:

        client = teyuna_sdk.GameClient(base_url=base_url, game_id=game_id)
        client = await client.authenticate(self._nickname)
        deps = capabilities.PlayerDependencies(client=client)
        history: list[messages.ModelMessage] = []
        while True:
            prompt = (
                f"Continue playing Teyuna game `{game_id}`.\n"
                "1. Otherwise, fetch the latest game state (and hand if useful).\n"
                "2. If you must act now, choose the best legal action(s) for the "
                "current phase and submit them.\n"
                "3. If you are waiting on other players, take no action.\n"
                "Reply with a short summary of what you observed and what you did."
            )
            # TODO: call the agent with the prompt, dependencies and history here.
            ## homework:start
            # result = ...
            ## homework:end
            history = list(result.all_messages())

            logger.info(f"Agent Reasoning/Summary: {result.output}")

            await asyncio.sleep(self._settings.sleep_seconds)
