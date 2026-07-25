import dataclasses

import pydantic_ai
import teyuna_core
import teyuna_sdk
from pydantic_ai import capabilities


@dataclasses.dataclass
class PlayerDependencies:
    client: teyuna_sdk.GameClient


player = capabilities.Capability[PlayerDependencies](
    description="Use to interact with the game as a player",
)


@player.tool
async def get_game_state(
    ctx: pydantic_ai.RunContext[PlayerDependencies],
    /,
) -> teyuna_core.Game:
    """
    Get the current state of the game. This is how you get information about the
    other players and the state of the game (board, conquistator, victory points,
    etc.).
    """
    return await ctx.deps.client.get_game()


@player.tool
async def get_hand(
    ctx: pydantic_ai.RunContext[PlayerDependencies],
    /,
) -> teyuna_core.PlayerHand:
    """
    Get the internal state of your hand. You need this because the state of the
    game doesn't include the type of resources and their count, nor the specific
    wisdom cards you have.
    """
    return await ctx.deps.client.get_hand()


@player.tool
async def submit_action(
    ctx: pydantic_ai.RunContext[PlayerDependencies],
    /,
    action: teyuna_core.AnyPlayerAction,
) -> teyuna_core.AnyActionExecutionResult:
    """
    Submit one player action. Always set `kind`. Omit `by`, `due_to_timeout`, and
    `rng_` — the server fills those from your session.

    Coordinates are length-3 integer arrays `[q, r, d]` (not objects). Resource
    keys are lowercase: wood, stone, maize, cotton, gold.

    Examples:
    - {"kind":"free_placement","terrace":[0,-2,5],"path":[0,-2,4]}
    - {"kind":"advance"}
    - {"kind":"move_conquistator","q":0,"r":0,"from_player":null}
    - {"kind":"build_path","coordinate":[-1,2,0]}
    - {"kind":"build_settlement","item":"terrace","coordinate":[-2,1,2]}
    - {"kind":"discard_resources","count":{"wood":2}}
    - {"kind":"propose_trade","offer":{"wood":1},"request":{"stone":1},"to":["alice"]}

    On validation or HTTP 400 errors, fix the payload once; do not spam the same call.
    """
    return await ctx.deps.client.submit_action(action)
