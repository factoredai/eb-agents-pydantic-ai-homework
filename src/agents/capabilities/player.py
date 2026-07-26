import dataclasses

import pydantic_ai
import teyuna_core
import teyuna_sdk
from pydantic_ai import capabilities


@dataclasses.dataclass
class PlayerDependencies:
    client: teyuna_sdk.GameClient


player = capabilities.Capability[PlayerDependencies](
    description=(
        "Interact with a Teyuna game you already joined. Use get_game_state to "
        "inspect the public board and turn state, get_hand for your private "
        "resources/cards, and submit_action to play legal moves for the current phase."
    ),
)


@player.tool
async def get_game_state(
    ctx: pydantic_ai.RunContext[PlayerDependencies],
    /,
) -> teyuna_core.Game:
    """Fetch the public game state.

    Call this first on every tick before deciding whether to act.

    Important fields:
    - `phase`: current phase name (e.g. "dice roll", "trade and build").
    - `turn_order`: nicknames in turn order; index 0 is the active player.
      Empty while still in lobby.
    - `to_discard_resources`: map of nickname → cards to discard. If your
      nickname is listed, you must discard even when it is not your turn.
    - `players`: public seats, VP, settlement/path counts (not exact resources).
    - `settlements` / `paths` / `map` / `conquistator_location` / `harbours`:
      board geometry for placement and blocking decisions.
    - `trade_proposals`: open offers you may accept.
    - `available_slots`: lobby seats still open.

    Sample call: get_game_state()
    """
    return await ctx.deps.client.get_game()


@player.tool
async def get_hand(
    ctx: pydantic_ai.RunContext[PlayerDependencies],
    /,
) -> teyuna_core.PlayerHand:
    """Fetch your private hand (resources + wisdom cards).

    Public game state does not reveal your exact resource counts or card types.
    Call this when you need to:
    - decide what to discard (`discard resources` phase),
    - decide what you can afford to build or buy,
    - choose which wisdom card to play,
    - craft a trade offer/request.

    Returns `{ "resources": {"wood": 2, ...}, "wisdom_cards": ["warrior", ...] }`.

    Sample call: get_hand()
    """
    return await ctx.deps.client.get_hand()


@player.tool
async def submit_action(
    ctx: pydantic_ai.RunContext[PlayerDependencies],
    /,
    action: teyuna_core.AnyPlayerAction,
) -> teyuna_core.AnyActionExecutionResult:
    """Submit one legal player action for the current phase.

    Always set `kind`. Omit `by`, `due_to_timeout`, and `rng_` — the server
    fills those from your session.

    Coordinates are length-3 integer arrays `[q, r, d]` (not objects).
    Resource keys are lowercase: wood, stone, maize, cotton, gold.
    Settlement `item` is `"terrace"` or `"great terrace"`.

    Call only after get_game_state (and get_hand when relevant) shows you must
    act — see the how-to section of your instructions for the decision loop,
    phase→action map, and sample payloads.

    On validation or HTTP 400 errors, read the detail, fix the payload once,
    and retry only if still useful. Do not spam the same failed call.
    """
    return await ctx.deps.client.submit_action(action)
