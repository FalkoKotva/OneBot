"""Custom ui for the bot"""

import logging

from discord import Status, Colour, Member, File
from easy_pil import (
    Editor,
    Canvas,
    Font,
    Text,
    load_image_async
)
from PIL.Image import ANTIALIAS


log = logging.getLogger(__name__)

def get_status_colour(status:Status) -> Colour:
    """Get the colour that corresponds to the given status

    Args:
        status (discord.Status): The status to get the colour for

    Returns:
        discord.Colour: The colour that corresponds to the given
        status
    """

    log.debug("Getting colour for status %s", status)

    match status:
        case Status.online:
            return Colour.green()
        case Status.idle:
            return Colour.yellow()
        case Status.dnd:
            return Colour.red()
        case Status.offline:
            return Colour.light_grey()
        case Status.invisible:
            return Colour.blue()
        case _:
            return Colour.blurple()

async def get_levelboard(
    member:Member,
    level:int,
    exp:int,
    next_exp:int,
    rank:int
) -> File:
    """Creates a levelboard for the given member

    Args:
        member (discord.Member): The member to create the levelboard for
        level (int): The current level of the member
        exp (int): The current exp of the member
        next_exp (int): The exp required for the next level

    Returns:
        discord.File: The levelboard as a file
    """

    log.debug(
        "Creating levelboard for %s, level %s, exp %s, next_exp %s, rank %s",
        member, level, exp, next_exp, rank
    )

    # Define the colours
    bg1_colour = "#141414"  # black
    bg2_colour = "#2F2F2F"  # dark grey
    fg1_colour = "#F9F9F9"  # white
    fg2_colour = "#9F9F9F"  # light grey
    accent_colour = member.colour.to_rgb()
    status_colour = get_status_colour(member.status).to_rgb()

    # Define the fonts
    poppins = Font.poppins(size=80)
    poppins_small = Font.poppins(size=60)

    log.debug("Drawing levelboard background")

    # Create the levelboard
    levelboard = Editor(Canvas((1800, 420), color=bg1_colour))
    levelboard.rounded_corners(20)

    log.debug("Drawing the avatar")

    # Create the avatar image
    avatar_outline = Editor(Canvas((340, 340), color=bg1_colour)).circle_image()
    avatar_img = await load_image_async(member.avatar.url)
    avatar = avatar_outline.paste(
        Editor(avatar_img).resize((300, 300)).circle_image(),
        (20, 20)
    )

    log.debug("Drawing accent polygon behind avatar")

    # Create a pattern behind the avatar
    levelboard.polygon(
        (
            (100, 0),  # top left
            (0, 100),  # bottom left
            (180, 180),  # bottom right
            (360, 0)  # top right
        ),
        fill=accent_colour
    )
    levelboard.polygon(
        ((0, 100), (100, 0), (180, 180), (0, 360)),
        fill=accent_colour
    )
    levelboard.rectangle(
        position=(0, 0),
        width=200, height=200,
        fill=accent_colour,
        radius=20
    )

    log.debug("Pasting the avatar")

    # Add the avatar to the levelboard
    levelboard.paste(avatar, (40, 40))

    log.debug("Drawing the status indicator")

    # Create a status indicator to go over the avatar
    status_outline = Editor(Canvas((110, 110), color=bg1_colour)).circle_image()
    status = status_outline.paste(
        Editor(Canvas((70, 70), color=status_colour)).circle_image(),
        (20, 20)
    )

    log.debug("Pasting the status indicator")

    # Add the status indicator to the levelboard
    levelboard.paste(status, (260, 260))

    log.debug("Drawing the level bar")

    # The percentage of the way to the next level
    percentage = (exp / next_exp) * 100
    percentage = max(percentage, 10)  # less than 10 causes visual issues

    # Create the experience bar
    levelboard.rectangle(
        (420, 280), width=1320, height=80, color=bg2_colour, radius=40
    )
    levelboard.bar(
        (420, 280), max_width=1320, height=80, color=accent_colour,
        radius=40, percentage=percentage
    )

    log.debug("Drawing the name text")

    # Add the member's name to the levelboard
    name_texts = (
        Text(member.display_name, font=poppins, color=fg1_colour),
        Text(f'#{member.discriminator}', font=poppins_small, color=fg2_colour)
    )
    levelboard.multi_text((420, 220), texts=name_texts)

    log.debug("Drawing the exp/next_exp text")

    # Add the member's experience count to the levelboard
    exp_texts = (
        Text(str(exp), font=poppins_small, color=fg1_colour),
        Text(f"/ {next_exp} XP", font=poppins_small, color=fg2_colour)
    )
    levelboard.multi_text((1740, 225), texts=exp_texts, align="right")

    log.debug("Drawing the rank/level text")

    # Add the member's level and rank to the levelboard
    level_texts = (
        Text("RANK", font=poppins_small, color=fg2_colour),
        Text(f"#{rank} ", font=poppins, color=fg1_colour),
        Text("LEVEL", font=poppins_small, color=fg2_colour),
        Text(str(level+1), font=poppins, color=fg1_colour)
    )
    levelboard.multi_text((1700, 80), texts=level_texts, align="right")

    log.debug("Antialiasing the levelboard")

    # Resize the image to apply antialiasing
    levelboard = levelboard.image
    width, height = levelboard.size
    levelboard = levelboard.resize((width//2, height//2), resample=ANTIALIAS)
    levelboard = Editor(levelboard)

    log.debug("Done, returning the levelboard!")

    return File(fp=levelboard.image_bytes, filename="levelboard.png")
