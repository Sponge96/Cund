Cund is a game project based on Evennia.

Current no longer working on this as I ended up being sick with tonsilitis for 5 months straight and prior to this hadn't kept notes on the project (lesson learned).



Combat: The current system is triggered with the "fight" command which check if the room has any valid targets (if they have the "hp" attribute and it's not currently set to 0) to fight with. It then pools the players and rolls for initiative and creates a turn order. Each player has a set amount of time to take their actions before it automatically tries to disengage them from combat. Each player is given a set amount of actions to take. 



![image](https://user-images.githubusercontent.com/20257044/122903152-0b42d480-d347-11eb-9ac1-d1d7da5f3594.png)



Combat Menu: The combat menu uses Evennia's EvMenu as a basis and opens on the start of your turn. You are given a number of options each costing an action to do.



Attack - Simply uses your current weapons damage value to preform an attack.



Skills - Current have healing skills and attack skill working each. Depending on the skill chosen it can be used again everyone in the room, a single target or multiple targets.

*These skills also have cooldowns as well as a resource cost to the player ensuring they have to think about their actions.*



Items - Was working on this when I became sick.



Disengage - Uses all action points to attempt to leave combat (this can only be achieved if everyone in combat attempts to disengage in the same turn)



End - Uses all remaining points and ends turn.



Most of my work was centred around the combat system and trying to make it as enjoyable as possible as well as clear and easy to use. My inspiration for this project was the MUD genre of games which sadly I didn't grow up playing but have since dabbled in them; I found that most didn't really age well in the clarity department, they all have very steep learning curves when it came to even simple systems so I wanted to change that for my project. I think anyone with minimal gaming experience can look at the screenshot and below and understand what is happening and what they're options are for the next step.



![image](https://user-images.githubusercontent.com/20257044/122904661-73de8100-d348-11eb-8a98-f74543efeff9.png)



I had also been working on a number of other systems but as I stated, as a novice who got a bit too excited by their first big scale project I didn't keep notes and thus when I fell ill it became a real unenjoyable experience picking up the pieces of what made total sense to me months prior but now was a jumbled mess of different ideas and concepts. I really enjoyed my time working on this project and learned a metric tonne of new skills (keeping good documentation being the main one). I think I'll definitly try to revist this concept at a later time.


Example of gameplay:

https://user-images.githubusercontent.com/20257044/122907665-48a96100-d34b-11eb-969a-feafb48f089e.mp4

Gameplay was set to 1 second delay between actions and only single action for quicker recording.


