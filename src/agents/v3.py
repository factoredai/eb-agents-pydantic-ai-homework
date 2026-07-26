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
    _nickname: Final[str] = "Jorge Varón"

    _instructions: Final[string.Template] = string.Template("""""")

    def __init__(self, settings_: settings.Settings):
        self._settings = settings_
        self._agent = self._build_agent()

    def _build_agent(self) -> pydantic_ai.Agent[capabilities.PlayerDependencies]:
        rulebook = self._settings.rulebook.read_text()
        howto = self._settings.howto.read_text()

        # TODO: instantiate the agent with the instructions and the
        # capabilities that enable the agent to talk to the Teyuna API.
        # agent = pydantic_ai.Agent()
        ## homework:start
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
        # TODO: Engineer your own loop here so that the agent acts only when it has
        # a meaningful action to take.
        ## homework:start
        raise NotImplementedError("Not implemented")
        ## homework:end
