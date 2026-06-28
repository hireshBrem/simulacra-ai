# Sapiaverse

Sapiaverse models human-like social behaviour through simulated people who act, remember, and interact inside a shared world.

## Language

**Agent**:
A simulated person with identity, memory, goals, and behaviour. An **Agent** may be represented visually by one **Avatar**.
_Avoid_: Bot, NPC, character, player

**Avatar**:
The visual representation of an **Agent** inside the simulation world. An **Avatar** is not the source of behaviour; it only shows where and how the Agent appears.
_Avoid_: Agent, character, sprite

**Role**:
The stable identity, personality, communication style, beliefs, and behavioural constraints of one **Agent**.
_Avoid_: Profile, prompt, persona

**Memory Stream**:
The chronological record of experiences and observations belonging to one **Agent**. An **Agent** has one Memory Stream.
_Avoid_: Log, chat history, transcript

**Social Space**:
A shared place where **Agents** can move, encounter each other, and attach meaning to locations. A Social Space contains zones and boundaries that shape possible interactions.
_Avoid_: Map, grid, level

**Simulation Model**:
The source of truth for the state of **Agents** and the **Social Space**. The Simulation Model determines where Agents are and what actions have occurred.
_Avoid_: Renderer, game scene, UI state

**Encounter**:
A moment when two or more **Agents** are close enough in a **Social Space** to notice or interact with each other. An Encounter may lead to a **Conversation**, but does not require one.
_Avoid_: Collision, trigger, chat

**Conversation**:
An exchange between **Agents** during an **Encounter**. The participating Agents decide whether to speak and what to say.
_Avoid_: Script, dialogue tree, cutscene

## Example Dialogue

Developer: "Should the Agent decide where to go, or should the Avatar?"

Domain expert: "The Agent decides. The Avatar only displays the Agent's position in the world."

Developer: "If the Avatar is blocked by a wall, did the Agent fail?"

Domain expert: "The Agent attempted an action, and the world rejected or adjusted it. The Avatar shows the result."

Developer: "Where do we find an Agent's personality?"

Domain expert: "In its Role. The Memory Stream should record what happened to that Agent over time."

Developer: "Are Agents just moving on an abstract grid?"

Domain expert: "No. They move through a Social Space where locations can matter socially."

Developer: "Who decides where an Agent moves next?"

Domain expert: "The Simulation Model. The Avatar only renders the resulting position."

Developer: "When two Agents meet, should the map decide what they say?"

Domain expert: "No. The Encounter creates the opportunity, and the Agents decide whether a Conversation happens."
