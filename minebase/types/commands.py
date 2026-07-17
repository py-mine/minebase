from __future__ import annotations

from typing import Annotated, Literal, Union, final

from pydantic import Field

from minebase.types._base import MinecraftDataModel


@final
class ParserModifier(MinecraftDataModel):
    """Additional metadata and constraints for a command parser.

    A modifier adjusts how a parser interprets or restricts the accepted input.
    Modifiers can enforce numeric ranges, specify special parsing modes, or point
    to a game registry for valid values.

    Attributes:
        amount: Indicates whether the parser consumes a single value or multiple values.
        max: Upper bound for numeric parsers, if applicable.
        min: Lower bound for numeric parsers, if applicable.
        type: Special parsing mode (e.g. entities, players, word, phrase).
        registry:
            Namespace key of a Minecraft registry that provides the set of valid inputs
            (e.g. "minecraft:entity_type", "minecraft:worldgen/biome").
    """

    amount: Literal["multiple", "single"] | None = None
    max: int | None = None
    min: int | None = None
    type: Literal["entities", "greedy", "phrase", "players", "word"] | None = None
    registry: str | None = None


@final
class CommandRootParserInfo(MinecraftDataModel):
    """Definition of a root-level command parser.

    Root parsers describe the set of available argument parsers
    that can be referenced by command argument nodes. Each parser
    may include example values and optional modifier constraints.

    Attributes:
        parser: Fully qualified parser identifier (e.g. "brigadier:integer" / "minecraft:vec3" / "minecraft:entity").
        modifier: Optional modifier object with constraints and extra behavior.
        examples: Example values accepted by the parser, used for hints or validation.
    """

    parser: str
    modifier: ParserModifier | None
    examples: list[str]


@final
class CommandInnerParserInfo(MinecraftDataModel):
    """Definition of a parser attached to a command argument node.

    Inner parsers describe how a specific argument should be interpreted when
    parsing a command. Unlike root parsers (which list all available parsers),
    inner parsers are embedded within `CommandArgumentNode` instances and
    specify the exact parser and optional modifier used for that argument.

    Examples of inner parsers include:
        - `minecraft:entity` with modifiers that distinguish between single/multiple
          entities or players.
        - `minecraft:resource` or `minecraft:resource_key` tied to specific registries
          such as `"minecraft:entity_type"` or `"minecraft:worldgen/structure"`.
        - Simple parsers like `minecraft:time`, `minecraft:vec3`, or `minecraft:uuid`
          without modifiers.

    Attributes:
        parser:
            Identifier of the parser used for this argument
            (e.g. "minecraft:entity", "minecraft:time", "minecraft:vec3").
        modifier:
            Optional modifier object that constrains or customizes parsing,
            such as limiting numeric ranges, specifying single vs. multiple
            entities, or binding to a registry of valid values.
    """

    parser: str
    modifier: ParserModifier | None


@final
class CommandArgumentNode(MinecraftDataModel):
    """Represents a typed argument in a Minecraft command tree (Java edition).

    Argument nodes define the structure and semantics of command parameters. Each
    argument specifies how input should be parsed, whether it can directly execute
    a command, and what further arguments or subcommands may follow.

    Examples include:
        - Numeric arguments with constraints (e.g. `fadeIn: brigadier:integer(min=0)`).
        - NBT or resource parsers (`value: minecraft:nbt_tag`, `loot_table: minecraft:resource_location`).
        - Entity and player selectors with modifiers
          (`player: minecraft:entity(type=players, amount=single)` or
           `entities: minecraft:entity(type=entities, amount=multiple)`).
        - Free-form string inputs (`name: brigadier:string(type=phrase)` or
          `action: brigadier:string(type=greedy)`).

    Attributes:
        type: Literal string identifying this as an `"argument"` node.
        name: The argument's identifier as it appears in the command (e.g. `"player"`, `"distance"`, `"fadeIn"`).
        executable:
            Whether this node can directly terminate a valid command path and trigger
            execution. If `False`, at least one child must be consumed.
        redirects:
            Optional list of alternative command paths this node may redirect to.
            Useful when arguments delegate parsing or execution to another node
            (e.g. `["execute"]`).
        children:
            Nested command nodes (both literal and argument) that may follow this
            argument. Defines branching in the command tree.
        parser:
            The parser that defines how to interpret this argument's value, wrapped
            in a `CommandInnerParserInfo`. This may include optional `ParserModifier`
            metadata such as numeric bounds, registry lookups, or selection mode.

    """

    type: Literal["argument"]
    name: str
    executable: bool
    redirects: list[str]
    children: list[CommandChildNode]
    parser: CommandInnerParserInfo | None = None


@final
class CommandLiteralNode(MinecraftDataModel):
    """Represents a fixed keyword in a Minecraft command tree (Java edition).

    Literal nodes define the constant words that form the structure of a command.
    They are used for command names (e.g. `/time`, `/teleport`) and for branching
    subcommands (e.g. `advancement from`, `advancement only <advancement>`).

    Unlike argument nodes, literal nodes do not accept user input. Instead, they
    specify exact keywords that must appear in the command. Each literal may be
    executable on its own or act as a prefix that leads to additional child nodes.

    Examples include:
        - Root-level commands:
            - `time`
            - `teleport`
            - `whitelist`
        - Nested subcommands:
            - `advancement from <advancement>`
            - `advancement only <advancement> <criterion>`

    Attributes:
        type: Literal string identifying this as a `"literal"` node.
        name: The keyword as it appears in the command (e.g. `"time"`, `"from"`).
        executable:
            Whether this node can directly terminate a valid command path and
            trigger execution (e.g. `/thunder`).
        redirects:
            Optional list of alternative command paths this node may redirect to.
            Most literals have no redirects, but some delegate execution (e.g.
            `"target" -> ["execute"]`).
        children:
            Nested command nodes (either literals or arguments) that may follow
            this literal. Defines branching and subcommands beneath this keyword.
    """

    type: Literal["literal"]
    name: str
    executable: bool
    redirects: list[str]
    children: list[CommandChildNode]


CommandChildNode = Annotated[Union[CommandLiteralNode, CommandArgumentNode], Field(discriminator="type")]


@final
class CommandRootNode(MinecraftDataModel):
    """Represents the root of the Minecraft command tree (Java edition).

    The root node serves as the single entry point for all commands. It does not
    correspond to any literal keyword typed by the player, nor a dynamic argument
    as a part of the command, it just acts as the invisible parent of every top-level
    command literal (e.g. `time`, `teleport`, `advancement`). From this node, parsing
    begins and branches into child `CommandLiteralNode` instances.

    Unlike literal or argument nodes, the root node:
        - Always has `type = "root"`.
        - Has a fixed `name = "root"`.
        - Cannot be executable (`executable = False`).
        - Cannot redirect to any other node (`redirects` is always empty).

    Attributes:
        type: Literal string identifying this as the `"root"` node.
        name: Always `"root"`, as there is only one root node in the tree.
        executable: Always `False`, since the root itself cannot represent a runnable command.
        redirects: Always an empty list, since the root cannot redirect to another node.
        children:
            List of all top-level command nodes of `CommandLiteralNode` instances corresponding
            to each command keyword available in the game.
    """

    type: Literal["root"]
    name: Literal["root"]
    executable: Literal[False]
    redirects: list[str] = Field(max_length=0)
    children: list[CommandLiteralNode] = Field(min_length=1)


@final
class CommandsData(MinecraftDataModel):
    """Minecraft-Data representing the full set of Minecraft commands (Java edition).

    This model encapsulates the complete command tree for the game, starting from the root node,
    all top-level and nested command literals and arguments, as well as the definitions of all
    root-level parsers used by arguments.

    Attributes:
        root: The root node of the command tree. All command parsing begins here.
        parsers:
            List of root-level parsers (`CommandRootParserInfo`) that describe the
            types of arguments used throughout the command tree, including examples
            and optional constraints.
    """

    root: CommandRootNode
    parsers: list[CommandRootParserInfo]
