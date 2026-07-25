import asyncio
import dataclasses
import logging
import string
import uuid
from typing import Any, Final

import httpx2
import pydantic_ai
from pydantic_ai import messages

import settings

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class Dependencies:
    client: httpx2.AsyncClient


@dataclasses.dataclass
class HTTPResponse:
    status_code: int
    data: dict[str, Any]
    headers: dict[str, str]
    error: str | None = None


class Agent:
    _nickname: Final[str] = "Hernan Darío"

    _instructions: Final[string.Template] = string.Template(
        """
        Your nickname is {{nickname}}.
        You are a skilled Teyuna player (a Catan-like game).
        Your goal is to reach 10 victory points before your opponents.\n\n
        ## Interface\n
        Play exclusively through `make_api_request`. Paths are relative to
        the API base URL.\n
        - If you are unsure about endpoints or request/response schemas,
        GET `/openapi.json` once and reuse what you learn.\n
        - Join with POST `/games/{game_id}/players` and a unique nickname
        (do not reuse names already seated).\n
        - Persist the `token` from the join response. On later authenticated
        calls (hand, actions, etc.), pass
        '`headers={"Authorization": "Bearer <token>"}`.\n'
        - Submit moves with POST `/games/{game_id}/actions` using the
        `kind` and fields described by the API.\n
        - Inspect public state with GET `/games/{game_id}` and your private
        hand with GET `/games/{game_id}/hand` when needed.\n\n
        ## Turn discipline\n
        Each tick: read the current game state, then act only when required.\n
        - If the lobby is waiting for players or it is not your turn, do not
        force actions; briefly note that you are waiting.\n
        - When it is your turn (or you must discard / move the conquistador /
        resolve a special phase), take one coherent set of legal actions for
        the current phase, then stop.\n
        - Prefer legal, high-value moves. If a request returns 400, read the
        error detail, correct the payload, and retry once if still useful.\n
        - Do not re-join after you already have a token. Do not spam the same
        failed action.\n\n
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
        ## Rulebook\n{{rulebook}}
        """
    )

    def __init__(self, settings_: settings.Settings):
        self._settings = settings_
        self._agent = self._build_agent()

    def _build_agent(self) -> pydantic_ai.Agent[Dependencies]:
        rulebook = self._settings.rulebook.read_text()

        # TODO: instantiate the agent with the instructions and the
        # tool to make API requests.
        ## homework:start
        # agent = pydantic_ai.Agent()
        ## homework:end
        return agent

    async def loop(
        self,
        *,
        game_id: uuid.UUID,
        base_url: str,
    ) -> None:

        async with httpx2.AsyncClient(base_url=base_url) as client:
            deps = Dependencies(client=client)
            history: list[messages.ModelMessage] = []
            while True:
                prompt = (
                    f"Continue playing Teyuna game `{game_id}`.\n"
                    "1. If you have not joined yet, join with a unique nickname and "
                    "remember the auth token.\n"
                    "2. Otherwise, fetch the latest game state (and hand if useful).\n"
                    "3. If you must act now, choose the best legal action(s) for the "
                    "current phase and submit them.\n"
                    "4. If you are waiting on other players, take no action.\n"
                    "Reply with a short summary of what you observed and what you did."
                )
                # TODO: call the agent with the prompt, dependencies and history here.
                ## homework:start
                raise NotImplementedError
                ## homework:end
                history = list(result.all_messages())

                logger.info(f"Agent Reasoning/Summary: {result.output}")

                await asyncio.sleep(self._settings.sleep_seconds)


async def make_api_request(
    ctx: pydantic_ai.RunContext[Dependencies],
    method: str,
    endpoint: str,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
) -> HTTPResponse:
    """Call the Teyuna game HTTP API.

    Args:
        method: HTTP method such as "GET" or "POST".
        endpoint: Path relative to the API base URL
            (e.g. "/openapi.json", "/games/{game_id}", "/games/{game_id}/actions").
        payload: JSON body for POST requests. Use an empty dict for GET.
        headers: Optional HTTP headers. After joining, pass
            {"Authorization": "Bearer <token>"} on authenticated endpoints.

    Returns:
        status_code, parsed JSON data (when available), response headers, and
        any error message. Read error/detail fields carefully on non-2xx responses.
    """
    client = ctx.deps.client
    response = await client.request(
        method=method, url=endpoint, json=payload, headers=headers
    )
    response_headers = dict(response.headers)

    try:
        data = response.json()
    except httpx2.HTTPStatusError as e:
        logger.error(f"HTTP status error: {e}")
        return HTTPResponse(
            status_code=response.status_code,
            data={},
            headers=response_headers,
            error=str(e),
        )
    return HTTPResponse(
        status_code=response.status_code,
        data=data,
        headers=response_headers,
        error=None,
    )
