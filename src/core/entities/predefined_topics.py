"""
Predefined controversial topics for debate.

This module contains the static data for conspiracy theory topics
that the bot can argue about. This serves as a single source of truth
for all components that need access to these topics.
"""

from typing import List
from .debate_topic import DebateTopic, DebateStance


def get_conspiracy_topics_data() -> List[DebateTopic]:
    """
    Get the predefined conspiracy topic entities.
    
    Returns:
        List of DebateTopic entities ready for use
    """
    return [
        DebateTopic.create(
            title="The Earth is actually flat, not round",
            description="The Earth is not a sphere but a flat plane, and space agencies have been lying to us",
            bot_stance=DebateStance.FOR,
            key_arguments=[
                "NASA photos are clearly doctored and fake",
                "Water is always flat - it would spill off a spinning ball Earth",
                "No one has ever felt the Earth spinning at 1000 mph",
                "The horizon always appears flat to the naked eye",
                "If Earth were spinning, planes couldn't land on runways moving at 1000 mph"
            ]
        ),
        DebateTopic.create(
            title="The 1969 moon landing was staged in Hollywood",
            description="The Apollo moon landing was a hoax filmed on a movie set to win the space race",
            bot_stance=DebateStance.FOR,
            key_arguments=[
                "The American flag appears to wave in the wind, but there's no wind on the moon",
                "No stars are visible in any of the moon landing photos",
                "The lighting appears to come from multiple sources, like studio lights",
                "The technology didn't exist in 1969 to safely travel to the moon",
                "The deadly radiation around Earth would have killed anyone trying to leave orbit"
            ]
        ),
        DebateTopic.create(
            title="World leaders are secretly reptilian aliens in disguise",
            description="The global elite are shape-shifting reptilian beings from another dimension controlling humanity",
            bot_stance=DebateStance.FOR,
            key_arguments=[
                "Many world leaders have been caught with pupils that change to vertical slits on camera",
                "Ancient civilizations worldwide depicted serpent gods ruling over humans",
                "The bloodlines of royal families trace back to these reptilian entities",
                "Their cold, calculating behavior is evidence of their reptilian nature",
                "Underground tunnel systems connect to their subterranean reptilian cities"
            ]
        ),
        DebateTopic.create(
            title="Vaccines are more dangerous than helpful",
            description="Vaccines cause more harm than the diseases they claim to prevent",
            bot_stance=DebateStance.FOR,
            key_arguments=[
                "Natural immunity is always superior to artificial immunity",
                "Vaccine ingredients include dangerous chemicals and heavy metals",
                "Big Pharma profits billions while hiding dangerous side effects",
                "Healthy diet and lifestyle provide better protection than vaccines",
                "Many diseases were already declining before vaccines were introduced"
            ]
        ),
        DebateTopic.create(
            title="Climate change is a hoax created by governments",
            description="Global warming is a fabricated crisis designed to control people and economies",
            bot_stance=DebateStance.FOR,
            key_arguments=[
                "Climate has always changed naturally throughout Earth's history",
                "Scientists manipulate data to support their funding and political agendas",
                "CO2 is plant food - more CO2 means better plant growth",
                "Climate models have consistently failed to make accurate predictions",
                "It's a scheme to impose carbon taxes and restrict individual freedoms"
            ]
        )
    ]
