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
        Your goal is to reach 10 victory points before your opponents.

        ## Tools
        You already joined and authenticated. Play only through these tools:
        1. `get_game_state()` — public board, phase, turn order, discards, trades.
        2. `get_hand()` — your private resources and wisdom cards.
        3. `submit_action(action)` — one legal move; always set `kind`.

        Coordinates are length-3 integer arrays `[q, r, d]` (not objects).
        Resource keys are lowercase (wood, stone, maize, cotton, gold).
        Omit `by`, `due_to_timeout`, and `rng_` on actions.

        Follow the how-to decision loop and phase→action map below. Prefer
        legal, high-value moves. If `submit_action` returns 400 / an error
        detail, fix the payload and retry once if still useful; otherwise
        stop for this tick.

        ## Rulebook
        $rulebook

        ## How to play
        $howto
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
                f"Continue playing Teyuna game `{game_id}` as `{self._nickname}`.\n"
                "Fetch game state (and hand if useful), act only if required, "
                "then stop. Reply with a short summary of what you observed "
                "and what you did."
            )
            # TODO: call the agent with the prompt, dependencies and history here.
            ## homework:start
            raise NotImplementedError
            ## homework:end
            history = list(result.all_messages())

            logger.info(f"Agent Reasoning/Summary: {result.output}")

            await asyncio.sleep(self._settings.sleep_seconds)
