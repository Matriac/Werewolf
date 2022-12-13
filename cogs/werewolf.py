import discord
from discord.ext import commands
from discord import app_commands
import random
import re
import asyncio
AVAILABLE_ROLES = ["Werewolf","Little girl","Hunter","Oridnary Townsfolk","Fortune Teller","Witch","Cupido","Mayor"]
games = {}
MINIMUM_PLAYER = 8
class Werewolf:
    def __init__(self,host:discord.Member):
        self.host = host
        self._roles = []
        self._players = {}
        self.hostMessage = None
        self._townChat = None
        self._werewolfChat = None
        self._littleGirlChat =None
        self._witchChat = None
        self._cupidoChat = None
        self._hunterChat = None
        self._fortuneChat =None
        self._guildRoles = {}
        self.running = False
        self.potions = [1,1]
        self._mayor = None
        self.saveByWitch = False
        self._alivePlayer = {}
        self._deadPlayer = []
        self._cupidoTarget = []
        self._votes = {}
        self._werewolfVotes ={}
        self._mayorVotes = {}
        self._chatCategory = None
        self._killedByWitch = None
        self._hunterTarget =None
        self._interactions = {}

    async def destroy(self):
        await self._townChat.category.delete(reason = "Game ended.")
        await self._townChat.delete(reason="Game ended.")
        await self._werewolfChat.delete(reason="Game ended.")
        await self._littleGirlChat.delete(reason="Game ended.")
        await self._witchChat.delete(reason="Game ended.")
        await self._cupidoChat.delete(reason="Game ended.")
        await self._fortuneChat.delete(reason="Game ended.")
        await self._hunterChat.delete(reason="Game ended.")
        for player in self._guildRoles:
            await player.remove_roles(self._guildRoles[player])
            await self._guildRoles[player].delete(reason="Game ended.")

        #await self._werewolfChat.delete(reason="Game ended.")
        
    def setLovers(self,user1,user2):
        for player in self._alivePlayer:
                if player.name == user1 or player.name == user2:
                    self._cupidoTarget.append(player)

    def add_player(self,user: discord.Member):
        if user not in self._players:
            self._players[user] = "None"
    
    def check_player(self,user:discord.Member):
        return user in self._players

    def remove_player(self,user: discord.Member):
        if user in self._players:
            del self._players[user]

    def setMayor(self,newMayor):
        for user in self._alivePlayer:
            if user.name == newMayor:
                self._mayor = user
                break

    def getMayor(self):
        return self._mayor

    def getCount(self):
        return len(self._players)
    def getPlayers(self):
        return self._players

    def getAlivePlayers(self):
        return self._alivePlayer

    def empty_vote(self):
        self._votes = {}
        self._werewolfVotes = {}

    def add_vote(self,voter,target) -> str:
        if voter in self._votes:
            self._votes[voter] = target
            return f"**{voter.name}** changed his mind and decided to lynch **{target}** instead !"
        self._votes[voter] = target
        return f"**{voter.name}** has decided to lynch **{target}** !"

    def add_mayor_vote(self,voter,target) -> str:
        if voter in self._mayorVotes:
            self._mayorVotes[voter] = target
            return f"**{voter.name}** changed his mind and decided to elect **{target}** instead !"
        self._mayorVotes[voter] = target
        return f"**{voter.name}** has decided to elect **{target}** !"

    def add_werewolf_vote(self,voter,target) -> str:
        if voter in self._werewolfVotes:
            self._werewolfVotes[voter] = target
            return f"**{voter.name}** changed his mind and decided to devour **{target}** instead !"
        self._werewolfVotes[voter] = target
        return f"**{voter.name}** has decided to devour **{target}** !"

    def getDescription(self,role):
        description= "Each night, the Werewolves bite, kill and devour one Townsperson.\nDuring the day they try to conceal their identity and vile deeds from the Townsfolk."
        if role == "Little girl":
            description = "The Little Girl is very curious. She can open her eyes during the night to spy on the Werewolves"
        elif role == "Witch":
            description = "This Townsperson knows how to make two very powerful potions:\n-The first is a healing potion, which can be used to prevent a player from being killed by a Werewolf.\n -The second is a poison, used during the night to eliminate one player.\nEach potion can only be used once per game. The Witch can use either potion on him/herself if he/she wishes."
        elif role == "Cupido":
            description = "“Cupido” is the town matchmaker. He/she received the nickname because of his/her ability to make any two people fall instantly in love.\n\n During the first night of the game, Cupido designates two players who will be in love with one another for the rest of the game.\nIf one of the lovers dies, the other immediately kills him/herself in a fit of grief."
        elif role == "Hunter":
            description = "If the hunter is killed by the Werewolves, or lynched by the Townsfolk, he/she can retaliate. With his/her dying breath, the hunter will shoot, thus eliminating, any one other player"
        elif role == "Fortune Teller":
            description = "Each night, the fortune teller can see the true personality of one player"
        elif role == "Townsfolk":
            description = "These folks have no abilities other than their own intuition."
        return description

    async def kill(self,name:str):
        toDelete = []
        for player in self._alivePlayer:
            if player.name == name:
                #if player.name == self._mayor.name:
                    #interaction = self.get_interaction(player.name)
                    #if interaction != None:
                        #await interaction.response.send_message(f"Please name a successor to the mayor position",view=MayorSuccessor(games[interaction.guild.id]))
                    #else:
                        #await self.send_message_town(f"Please choose the next mayor:",view=MayorSelect(games[interaction.guild.id]))
                    #await asyncio.sleep(15)
                if player.name == self._cupidoTarget[0].name:
                    await self.send_message_town(f"Seeing the death of his lover, **{self._cupidoTarget[1].name}** could not handle the pain and has commited suicide !\n\n {self._cupidoTarget[1].name} role was : **{self.getRole(self._cupidoTarget[1].name)}**\n")
                    for lover in self._alivePlayer:
                        if lover.name == self._cupidoTarget[1].name:
                            await self._townChat.set_permissions(self._guildRoles[lover],send_messages=False,read_messages=True)
                            #if lover.name == self._mayor.name:
                                #interaction = self.get_interaction(lover.name)
                                #if interaction != None:
                                    #await interaction.response.send_message(f"Please name a successor to the mayor position",view=MayorSuccessor(games[interaction.guild.id]))
                                #else:
                                    #await self.send_message_town(f"Please choose the next mayor:",view=MayorSelect(games[interaction.guild.id]))
                                #await asyncio.sleep(15)
                            toDelete.append(lover)
                elif player.name == self._cupidoTarget[1].name:
                    await self.send_message_town(f"Seeing the death of his lover, **{self._cupidoTarget[0].name}** could not handle the pain and has commited suicide !\n\n {self._cupidoTarget[0].name} role was : **{self.getRole(self._cupidoTarget[0].name)}**\n")
                    for lover in self._alivePlayer:
                        if lover.name == self._cupidoTarget[0].name:
                            #if lover.name == self._mayor.name:
                                #interaction = self.get_interaction(lover.name)
                                #if interaction != None:
                                    #await interaction.response.send_message(f"Please name a successor to the mayor position",view=MayorSuccessor(games[interaction.guild.id]))
                               # else:
                                    #await self.send_message_town(f"Please choose the next mayor:",view=MayorSelect(games[interaction.guild.id]))
                                #await asyncio.sleep(15)
                            await self._townChat.set_permissions(self._guildRoles[lover],send_messages=False,read_messages=True)
                            toDelete.append(lover)
                await self._townChat.set_permissions(self._guildRoles[player],send_messages=False,read_messages=True)
                toDelete.append(player)
            print("\n")
        for item in toDelete:
            del self._alivePlayer[item]

# RIGHT THERE NOOB
    async def create_channels(self,guild):
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages = False), #change this to false to make them private again. thanks
            guild.me:discord.PermissionOverwrite(read_messages=True)
            
        }
        self._chatCategory = await guild.create_category_channel("Werewolf")
        self._townChat = await guild.create_text_channel(f"Town",reason="Werewolf game",overwrites=overwrites,category=self._chatCategory)
        self._littleGirlChat = await guild.create_text_channel(f"Little Girl",reason="Werewolf game",overwrites=overwrites,category=self._chatCategory)
        self._cupidoChat = await guild.create_text_channel(f"Cupido",reason="Werewolf game",overwrites=overwrites,category=self._chatCategory)
        self._werewolfChat = await guild.create_text_channel(f"Werewolves",reason="Werewolf game",overwrites=overwrites,category=self._chatCategory)
        self._witchChat = await guild.create_text_channel(f"Witch",reason="Werewolf game",overwrites=overwrites,category=self._chatCategory)
        self._fortuneChat = await guild.create_text_channel(f"Fortune teller", reason="Werewolf game", overwrites=overwrites,category=self._chatCategory)
        self._hunterChat = await guild.create_text_channel(f"Hunter",reason="Werewolf game",overwrites=overwrites,category=self._chatCategory)
        for player in self._guildRoles:
            await self._townChat.set_permissions(self._guildRoles[player],read_messages=True)
        
    async def create_guildRoles(self,guild):
        print("hello")
        for player in self._players:
            self._guildRoles[player] = await guild.create_role(name="town",reason ="Werewolf game")
            await player.add_roles(self._guildRoles[player])

    async def loadDayPerm(self):
        for player in self._guildRoles:
            if player in self._alivePlayer:
                await self._townChat.set_permissions(self._guildRoles[player],send_messages=True,read_messages=True)
                if self._players[player] == "Werewolf":
                    await self._werewolfChat.set_permissions(self._guildRoles[player],send_messages=False,read_messages=False)
                elif self._players[player] == "Witch":
                    await self._witchChat.set_permissions(self._guildRoles[player],read_messages=False)
                elif self._players[player] == "Little girl":
                    await self._littleGirlChat.set_permissions(self._guildRoles[player],read_messages=False)
                elif self._players[player] == "Fortune teller":
                    await self._fortuneChat.set_permissions(self._guildRoles[player],read_messages=False)
                elif self._players[player] == "Hunter":
                    await self._hunterChat.set_permissions(self._guildRoles[player],read_messages=True,send_messages=False)
        
    async def loadNightPerm(self):
        for player in self._guildRoles:
            if player in self._alivePlayer:
                await self._townChat.set_permissions(self._guildRoles[player],send_messages=False,read_messages=True)
                if self._players[player] == "Werewolf":
                    await self._werewolfChat.set_permissions(self._guildRoles[player],send_messages=True,read_messages=True)
                elif self._players[player] == "Witch":
                    await self._witchChat.set_permissions(self._guildRoles[player],read_messages=True)
                elif self._players[player] == "Little girl":
                    await self._littleGirlChat.set_permissions(self._guildRoles[player],read_messages=True)
                elif self._players[player] == "Fortune teller":
                    await self._fortuneChat.set_permissions(self._guildRoles[player],read_messages=True)

    async def send_message_werewolf(self,message,*,view =None,embed= None):
        await self._werewolfChat.send(message,view=view,embed=embed)

    async def send_message_witch(self,message,*,view = None,embed = None):
        await self._witchChat.send(message,view=view,embed=embed)

    async def send_message_fortune(self,message,*,view =None,embed = None):
        await self._fortuneChat.send(message,view=view,embed=embed)
    
    async def send_message_hunter(self,message,*,view=None,embed=None):
        await self._hunterChat.send(message,view=view,embed=embed)

    def get_werewolf_chat(self):
        return self._werewolfChat

    async def send_message_littleGirl(self,message):
        message = "**Werewolf :** " + message
        await self._littleGirlChat.send(message)

    async def startGame(self,game):
        guild = self.hostMessage.guild
      
        self.loadRoles()
       
        self._alivePlayer = self._players.copy()
        await self.create_guildRoles(guild)
        await asyncio.sleep(0.5)
        await self.create_channels(guild)
        for player in self._players:
            channel = await player.create_dm()
            tmp = random.randint(0,len(self._roles) -1)
            role = self._roles[tmp]
            self._roles.remove(role)
            self._players[player] = role

            await channel.send(f"",embed=RoleEmbed(role,self.getDescription(role)))
        self._alivePlayer = self._players.copy()
        await self._cupidoChat.send(f"As Cupido you can designate 2 players that will fall in love. You may choose yourself if you want. If one of the lover die, the other will kill him/herself in a fit of grief.",view=CupidoView(game))
        await asyncio.sleep(30)
        if len(self._cupidoTarget) == 0:
            firstIndex = random.randint(0,len(self._alivePlayer) -1)
            while True:
                secondIndex = random.randint(0,len(self._alivePlayer) -1)
                if secondIndex != firstIndex or len(self._alivePlayer) == 1:
                    break
            cnt = 0
            for player in self._alivePlayer:
                if cnt == firstIndex:
                    first = player
                elif cnt == secondIndex:
                    second = player
                cnt += 1
            self.setLovers(first.name,second.name)
            await self._cupidoChat.send(f"You have not chosen anyone so 2 people will be randomly selected.\n The 2 lovers will be **{first.name}** and **{second.name}**")
        channel = await self._cupidoTarget[0].create_dm()
        await channel.send(f"You have been chosen as a lover !\n You are in love with **{self._cupidoTarget[1].name}**. If one of you die, the other will die as well! Protect your loved one.\nYou cannot vote against your loved one. You win if the both of you survive the game.")
        channel = await self._cupidoTarget[1].create_dm()
        await channel.send(f"You have been chosen as a lover !\n You are in love with **{self._cupidoTarget[0].name}**. If one of you die, the other will die as well! Protect your loved one.\nYou cannot vote against your loved one. You win if the both of you survive the game.")
        await asyncio.sleep(10)

    def get_werewolf_target(self):
        result = {}
        for vote in self._werewolfVotes:
            if self._werewolfVotes[vote] in result:
                result[self._werewolfVotes[vote]] += 1
            else:
                result[self._werewolfVotes[vote]] = 1
        max_votes = [key for key,value in result.items() if value == max(result.values())]
        if len(max_votes) > 1:
            return max_votes[0]
        elif len(max_votes) == 1:
            return max_votes[0]
        return None

    def getRole(self,name:str):
        for player in self._players:
            if player.name == name:
                return self._players[player]
        return "?_?"

    def get_interaction(self,name):
        if name in self._interactions:
            return self._interactions[name]
        else:
            return None
    
    def set_interaction(self,name,interaction):
        self._interactions[name] = interaction

    def loadRoles(self):
        count = self.getCount()
        if count < 11:
            self._roles.append("Werewolf")
            self._roles.append("Werewolf")
        else:
            self._roles.append("Werewolf")
            self._roles.append("Werewolf")
            self._roles.append("Werewolf")
        self._roles.append("Little girl")
        self._roles.append("Hunter")
        self._roles.append("Witch")
        self._roles.append("Fortune teller")
        self._roles.append("Cupido")
        while len(self._roles) < len(self._players):
            self._roles.append("Townsfolk")

    def get_state(self):
        ww = 0
        town = 0
        lover = 0
        for player in self._alivePlayer:
            if player in self._cupidoTarget:
                lover = lover+1
            if self._alivePlayer[player] == "Werewolf":
                ww = ww +1
            else:
                town = town +1
        if ww >0 and town == 0:
            return "WW"
        elif town >0 and ww == 0:
            return "TOWN"
        elif lover == 2 and town + ww == 2:
            return "LOVER"
        elif town == 0 and ww == 0:
            return "DRAW"
        else:
            return "RUNNING"

    async def send_message_town(self,message: str,*,embed = None,view=None):
        if view == None:
            await self._townChat.send(message,embed=embed,view=view)
        else:
            view.message = await self._townChat.send(message,embed=embed,view=view)

    def getLynched(self):
        votes = {}
        votingPower =1
        for user in self._votes:
            if user == self._mayor:
                votingPower =2
            else:
                votingPower = 1
            tmp = self._votes[user]
            if tmp in votes:
                votes[tmp] += votingPower
            else:
                votes[tmp] = votingPower
        max_votes = [key for key, value in votes.items() if value == max(votes.values())]
        if len(max_votes) > 1:
            return None
        elif len(max_votes) == 1:
            return max_votes[0] 
        return None

    def getMayorVote(self):
        votes = {}
        for user in self._mayorVotes:
            tmp = self._mayorVotes[user]
            if tmp in votes:
                votes[tmp] += 1
            else:
                votes[tmp] = 1
        max_votes = [key for key,value in votes.items() if value == max(votes.values())]
        return max_votes[0]

    def useLifePotion(self):
        self.saveByWitch = True
        self.potions[0] = 0

    def witch_kill(self,target):
        self.potions[1] = 0
        self._killedByWitch  = target

    def get_witch_target(self):
        return self._killedByWitch

    def setHunterTarget(self,target):
        self._hunterTarget = target

    def getHunterTarget(self):
        if self._hunterTarget != None:
            return self._hunterTarget
        else:
            rd = random.randint(0,len(self._alivePlayer)-1)
            return self._alivePlayer[rd].name


class WerewolfView(discord.ui.View):
    def __init__(self,game):
        super().__init__()
        self.add_item(WerewolfSelect(game))

class WerewolfSelect(discord.ui.Select):
    def __init__(self,game) -> None:
        options = []
        self.game = game
        for player in game.getAlivePlayers():
            if game.getRole(player.name) != "Werewolf":
                options.append(discord.SelectOption(label=player.name))
        super().__init__(options=options,min_values=1,max_values=1)

    async def callback(self,interaction:discord.Interaction):
        await interaction.response.send_message(self.game.add_werewolf_vote(interaction.user,self.values[0]))

class VoteSelect(discord.ui.Select):
    def __init__(self,game) -> None:
        options = []
        self.game = game
        for player in game.getAlivePlayers():
            options.append(discord.SelectOption(label=player.name))
        super().__init__(options=options,min_values=1,max_values=1)

    async def callback(self,interaction:discord.Interaction):
        self.game.set_interaction(interaction.user.name,interaction)
        if interaction.user.name == self.values[0]:
            await interaction.response.send_message("You cannot vote for yourself!",ephemeral =True)
        else:
            await interaction.response.send_message(self.game.add_vote(interaction.user,self.values[0]))

class CupidoSelect(discord.ui.Select):
    def __init__(self,game) -> None:
        options = []
        self.game = game
        for player in game.getAlivePlayers():
            options.append(discord.SelectOption(label=player.name))
        super().__init__(options=options,min_values=2,max_values=2)

    async def callback(self,interaction:discord.Interaction):
        self.game.setLovers(self.values[0],self.values[1])
        original = interaction.message
        await interaction.response.send_message(f"{self.values[0]} and {self.values[1]} are now lovers !")
        await original.delete()
        
class CupidoView(discord.ui.View):
    def __init__(self,game):
        super().__init__()
        self.add_item(CupidoSelect(game))

class DayVote(discord.ui.View):
    def __init__(self,game) -> None:
        super().__init__(timeout=30)
        self.add_item(VoteSelect(game))
    
    async def on_timeout(self):
        await self.message.delete()

class MayorSelect(discord.ui.Select):
    def __init__(self,game) -> None:
        options = []
        self.game = game
        for player in game.getAlivePlayers():
            options.append(discord.SelectOption(label=player.name))
        super().__init__(options=options,min_values=1,max_values=1)
    
    async def callback(self,interaction:discord.Interaction):
        self.game.set_interaction(interaction.user.name,interaction)
        if interaction.user.name == self.values[0]:
            await interaction.response.send_message("You cannot vote for yourself!",ephemeral=True)
        else:
            await interaction.response.send_message(self.game.add_mayor_vote(interaction.user,self.values[0]))

class MayorVote(discord.ui.View):
    def __init__(self,game):
        super().__init__(timeout=30)
        self.add_item(MayorSelect(game))

    async def on_timeout(self):
        await self.message.delete()

class HunterSelect(discord.ui.Select):
    def __init__(self,game,disabled) -> None:
        options = []
        self.game = game
        for player in game.getAlivePlayers():
            if game.getRole(player.name) != "Hunter":
                options.append(discord.SelectOption(label=player.name))
        super().__init__(options=options,min_values=1,max_values=1,disabled=disabled)

    async def callback(self,interaction:discord.Interaction):
        self.game.setHunterTarget(self.values[0])
        original = interaction.message
        await interaction.response.send_message(f"The hunter retaliated and killed **{self.values[0]}** before dying.")
        await original.edit(view=HunterView(self.game,True))

class HunterView(discord.ui.View):
    def __init__(self,game):
        super().__init__()
        self.add_item(HunterSelect(game,False))

class MayorSuccessor(discord.ui.View):
    def __init__(self,game):
        super().__init__(timeout=30)
        self.add_item(MayorSelect(game))

    async def on_timeout(self):
        await self.message.delete()

class MayorSuccessorSelect(discord.ui.Select):
    def __init__(self,game) -> None:
        options = []
        self.game = game
        for player in game.getAlivePlayers():
            if player.name != game.getMayor().name:
                options.append(discord.SelectOption(label=player.name))
        super().__init__(options=options,min_values=1,max_values=1)
    
    async def callback(self,interaction:discord.Interaction):
        self.game.set_interaction(interaction.user.name,interaction)
        self.game.setMayor(self.values[0])
        message = interaction.message
        await message.delete()
        await interaction.response.send_message(f"**{self.values[0]}** has been chosen as the new mayor !")


async def day_loop(game: Werewolf,firstLoop):
    
    await game.loadDayPerm()
    print("this is the day")
    if firstLoop is False:
        victim = game.get_werewolf_target()
        witchVictim = game.get_witch_target()

        if victim != None:
            if game.saveByWitch == True:
                message= f"**{victim}** was attacked by werewolves during the night but was saved by a witch !"
                game.saveByWitch = False
                await game.send_message_town(message)
            else:
                role = game.getRole(victim)
                message= f"The Village wakes up and as everyone gather, they realise someone is missing...\n**{victim}** was killed!\n\n {victim} role was : **{role}**\n\n"
                await game.send_message_town(message)
                await game.kill(victim)
                if role == "Hunter":
                    await asyncio.sleep(5)
                    await game.send_message_town(f"Before dying, the hunter in a last effort try to retaliate...")
                    await game.send_message_hunter(f"@everyone\nChoose the person you want to kill:\n You have 20 seconds",view=HunterView(game) ) 
                    await asyncio.sleep(20)
                    hunterVictim = game.getHunterTarget()    
                    role = game.getRole(hunterVictim)
                    message=f"The hunter has shot **{hunterVictim}**! {hunterVictim} is dead ! {hunterVictim} role was : **{role}**"
                    await game.send_message_town(message)
                    await game.kill(hunterVictim)
                
                if witchVictim != None and witchVictim != victim:
                    role = game.getRole(witchVictim)
                    message= f"**{witchVictim}** was founded poisoned by a witch !\n **{witchVictim}** is dead !\n {witchVictim} role was **{role}**\n\n"
                    game.witch_kill(None)
                    await game.send_message_town(message)
                    if role == "Hunter":
                        await asyncio.sleep(5)
                        await game.send_message_town(f"Before dying, the hunter in a last effort try to retaliate...")
                        await game.send_message_hunter(f"@everyone\nChoose the person you want to kill:\n You have 20 seconds",view=HunterView(game) )
                    await asyncio.sleep(20)
                    await game.kill(witchVictim)
                    hunterVictim = game.getHunterTarget()    
                    role = game.getRole(hunterVictim)
                    message=f"The hunter has shot **{hunterVictim}**! {hunterVictim} is dead ! {hunterVictim} role was : **{role}**"
                    await game.send_message_town(message)
                    await game.kill(hunterVictim)
                    

        else:
            if witchVictim != None:
                role = game.getRole(witchVictim)
                message= f"**{witchVictim}** was founded poisoned by a witch !\n **{witchVictim}** is dead !\n {witchVictim} role was **{role}**\n\n"
                game.witch_kill(None)
                if role == "Hunter":
                    await asyncio.sleep(5)
                    await game.send_message_town(f"Before dying, the hunter in a last effort try to retaliate...")
                    await game.send_message_hunter(f"@everyone\nChoose the person you want to kill:\n You have 20 seconds",view=HunterView(game) )
                    await asyncio.sleep(20)
                    hunterVictim = game.getHunterTarget()    
                    role = game.getRole(hunterVictim)
                    message=f"The hunter has shot **{hunterVictim}**! {hunterVictim} is dead ! {hunterVictim} role was : **{role}**"
                    await game.send_message_town(message)
                    await game.kill(hunterVictim)
                else:
                    await game.send_message_town(message)
                await game.kill(witchVictim)
            else:
                message = f"The Village wakes up and while everyone is there, some people heard werewolves during the night !"
                await game.send_message_town(message)
        if game.get_state() == "RUNNING":
            await asyncio.sleep(30)
            message=f"After discussing for a while, The villager has decided to lynch someone!\n You may vote now for who you want to lynch !\nYou have 30 seconds to vote!\n\n"
            await game.send_message_town(message,view=DayVote(game))
            await asyncio.sleep(30)
            lynch = game.getLynched()
            if lynch != None:
                if game.getRole(lynch) == "Hunter":
                    message=f"The Village has decided to lynch **{lynch}** !\n\n **{lynch}** take his gun in a last effort and decide who to bring in the other world."
                    await game.send_message_town(message)
                    await game.send_message_hunter(f"@everyone\nChoose the person you want to kill:\n You have 20 seconds",view=HunterView(game) )
                    await asyncio.sleep(20)
                    hunterVictim = game.getHunterTarget()    
                    role = game.getRole(hunterVictim)
                    message=f"The hunter has shot **{hunterVictim}**! {hunterVictim} is dead ! {hunterVictim} role was : **{role}**"
                    await game.send_message_town(message)
                    await game.kill(hunterVictim)
                message=f"The Village has decided to lynch **{lynch}** !\n\n **{lynch}** was killed! \n\n {lynch} role was : **{game.getRole(lynch)}**"
                await game.send_message_town(message)
            else:
                message=f"The Village could not come to an agreement on who to lynch..."
                await game.send_message_town(message)
            if lynch != None:
                await game.kill(lynch)
            await asyncio.sleep(8)
            if game.get_state() == "RUNNING":
                message=f"The village is now going back to sleep, hoping to survive one more night..."
                await game.send_message_town(message)
    else:
        #message = f"The Village wakes up on this beautiful day. Just a regular day in this peaceful town.\nThey realise something is wrong, they do not have a mayor !\nThey decided to elect one!\nThe mayor vote count as 2 votes."
        message = f"The Village wakes up on this beautiful day. Just a regular day. Everyone goes back to sleep"
        await game.send_message_town(message)
        #await game.send_message_town(message,view = MayorVote(game))
        #await asyncio.sleep(30)
        #mayor = game.getMayorVote()
        #game.setMayor(mayor)
        #await game.send_message_town(f"The new mayor is **{mayor}**! \nEveryone celebrate and then go back to sleep.")
        await asyncio.sleep(7)
    await asyncio.sleep(3)


    
async def night_loop(game : Werewolf):
    game.empty_vote()
    await game.loadNightPerm()
    await game.send_message_littleGirl("@everyone You can see what the werewolves discuss about here.")
    await game.send_message_werewolf("@everyone Choose who you will devour tonight:\nYou have 1 minute",view=WerewolfView(game))
    await game.send_message_fortune("@everyone You can use your divination power to examine another person and discover their true nature.",view=FortuneView(game,False))
    await asyncio.sleep(45)
    await game.send_message_werewolf("You have 15 seconds remaining.")
    await asyncio.sleep(15)
    await game.send_message_witch(f"@everyone The werewolves wants to kill : {game.get_werewolf_target()}. \n What are you going to do?\n You can only do each action once in the game\nYou can also do nothing\nYou have 20 seconds to choose ",view=WitchView(game))
    await asyncio.sleep(20)
    print("this is the night")
    


async def werewolfLoop(id):
    game = games[id]
    await asyncio.sleep(5)
    firstLoop = True
    while game.get_state() == "RUNNING":
        print("This is the game loop")
        await day_loop(game,firstLoop)
        if game.get_state() == "RUNNING":
            await night_loop(game)
        if firstLoop == True:
            firstLoop = False

    winner = game.get_state()
    if winner == "WW":
        winner = "the Werevolves"
        await game.send_message_town("The winner is **" + winner + "**, Congrats ! This channel will now be destroyed in 30 seconds.")
    elif winner == "LOVER":
        winner = "the lovers"
        await game.send_message_town("The winner is **" + winner + "**, Congrats ! This channel will now be destroyed in 30 seconds.")
    elif winner == "DRAW":
        await game.send_message_town("The game ends in a draw ! This channel will now be destroyed in 30 seconds.")
    elif winner == "TOWN":
        winner = "the town"
        await game.send_message_town("The winner is **" + winner + "**, Congrats ! This channel will now be destroyed in 30 seconds.")
    
    await asyncio.sleep(30)
    await game.destroy()
    del games[id]
    print(games)
    
class FortuneSelect(discord.ui.Select):
    def __init__(self,game,disabled) -> None:
        options = []
        self.game = game
        for player in game.getAlivePlayers():
            if game.getRole(player.name) !=  "Fortune Teller":
                options.append(discord.SelectOption(label=player.name))
        super().__init__(options=options,min_values=1,max_values=1,disabled=disabled)
    
    async def callback(self,interaction:discord.Interaction):
        original = interaction.message
        await original.edit(view=FortuneView(self.game,True))
        await interaction.response.send_message(f"You use your power to find out {self.values[0]} role.... He is a **{self.game.getRole(self.values[0])}**")


class FortuneView(discord.ui.View):
    def __init__(self,game,disabled):
        super().__init__()
        self.add_item(FortuneSelect(game,disabled))

class RoleEmbed(discord.Embed):
    def __init__(self,role,description):
        super().__init__()
        self.title=f"Your role is {role}"
        self.description=f"{description}"


class HostGameEmbed(discord.Embed):
    def __init__(self,host: discord.Member,players,started:bool):
        super().__init__()
        self.title=f"{host.name} is hosting a Werewolf game!"
        self.description= f"**For the Townsfolk**: Kill all of the Werewolves.\n**For the Werewolves**: Kill all the Townsfolk\n**Current player count : ** {str(len(players))}\n**Players :** "
        for player in players:
            self.description += player.name + ', '
        if started:
            self.description += "\n\nThe game is about to start in 1 minute! You can still join/leave for the next 30 seconds."
        
class JoinGameButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.primary,label="Join! / Leave!",emoji="🐺")

    async def callback(self,interaction:discord.Interaction):
        if games[interaction.guild.id].check_player(interaction.user):
            games[interaction.guild.id].remove_player(interaction.user)
            await interaction.response.send_message(f"You have left the game!",ephemeral=True)
            await updateMessage(interaction)
            
        else:
            games[interaction.guild.id].add_player(interaction.user)
            await updateMessage(interaction)
            await interaction.response.send_message(f"You have joined the game!",ephemeral=True)
            
            
class StartGameButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger,label= "Start Game!!",emoji="⚰️")

    async def callback(self,interaction:discord.Interaction):
        
        
        await interaction.response.send_message(f"The game will start in 1 minute! Please take a look at your dm to find out your role!")
        games[interaction.guild.id].running = True
        await updateMessage(interaction)
        await asyncio.sleep(30)
        if len(games[interaction.guild.id].getPlayers()) < MINIMUM_PLAYER:
            await interaction.channel.send("Oh, It looks like that some people left while the game was starting... We are not enough to start ! back to square one.")
            games[interaction.guild.id].running = False
            await updateMessage(interaction)
        else:
            await games[interaction.guild.id].startGame(games[interaction.guild.id])
            await updateMessage(interaction,started=True)
            asyncio.create_task(werewolfLoop(interaction.guild.id))
           
    

class HostGameView(discord.ui.View):
    def __init__(self,start:bool):
        super().__init__(timeout=None)
        self.add_item(JoinGameButton())
        if start:
            self.add_item(StartGameButton())

class WitchView(discord.ui.View):
    def __init__(self,game):
        super().__init__()
        self.add_item(WitchLifeButton(game))
        self.add_item(WitchDeathButton(game))
    
class WitchLifeButton(discord.ui.Button):
    def __init__(self,game):
        if game.potions[0] == 1:
            available = False
        else:
            available = True
        super().__init__(style = discord.ButtonStyle.green,label = "Use the life potion to save the victim",disabled=available)

    async def callback(self,interaction:discord.Interaction):
        games[interaction.guild.id].useLifePotion()
        original = interaction.message
        await interaction.response.send_message(f"You have saved the victim!",ephemeral =True)
        await original.delete()

class WitchDeathView(discord.ui.View):
    def __init__(self,game):
        super().__init__()
        self.add_item(WitchDeathSelect(game))


class WitchDeathButton(discord.ui.Button):
    def __init__(self,game):
        if game.potions[1] == 1:
            available = False
        else:
            available = True
        super().__init__(style = discord.ButtonStyle.danger,label = "Use the death potion to kill someone",disabled=available)

    async def callback(self,interaction:discord.Interaction):
        original = interaction.message
        await original.edit(content=f"Choose the person you want to kill : ",view=WitchDeathView(games[interaction.guild.id]))


class WitchDeathSelect(discord.ui.Select):
    def __init__(self,game):
        options = []
        self.game = game
        for player in game.getAlivePlayers():
            if game.getRole(player.name) !=  "Witch":
                options.append(discord.SelectOption(label=player.name))
        super().__init__(options=options,min_values=1,max_values=1)
    
    async def callback(self,interaction:discord.Interaction):
        if interaction.user.name == self.values[0]:
            await interaction.response.send_message("You cannot vote for yourself!",ephemeral=True)
        else:
            original = interaction.message
            await interaction.channel.send(f"You have chosen to kill {self.values[0]}")
            self.game.witch_kill(self.values[0])
            await original.delete()

class WerewolfCog(commands.Cog):
    def __init__(self,bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="play")
    async def play(self,interaction: discord.Interaction) -> None:
        """Host a game of Werewolf!"""
        tmp = []
       
        tmp.append(interaction.user)
        embed = HostGameEmbed(interaction.user,tmp,False)
        view = HostGameView(False)
        if interaction.guild.id not in games:
            category = None
            for channel in interaction.guild.channels:
                if channel.category != None:
                    if channel.category.name == "Werewolf" and channel.name in ["town","fortune-teller","little-girl","werewolves","witch","cupido","hunter"]:
                        category = channel.category
                        await channel.delete()
            if category != None:
                await category.delete()
            games[interaction.guild.id] = Werewolf(interaction.user)
            games[interaction.guild.id].add_player(interaction.user) 
            await interaction.response.send_message(embed=embed,view=view)
            games[interaction.guild.id].hostMessage = await interaction.original_response()
        else:
            await interaction.response.send_message("A game is already running. Please wait for it to finish before starting a new one.")

        

    @commands.Cog.listener()
    async def on_message(self,message):
        content = message.content
        mention_regex = re.compile(r"<@!?(\d+)>")
        mention = re.sub(mention_regex,"", content)
        try:
            if games[message.guild.id] != None:
                if games[message.guild.id].get_werewolf_chat() != None:
                    if message.channel.id == games[message.guild.id].get_werewolf_chat().id and message.author.id != 1050087296747184150:
                        await games[message.guild.id].send_message_littleGirl(mention)
        except:
            pass

       


    

        
async def updateMessage(interaction: discord.Interaction,started = False) -> None:
    count = games[interaction.guild.id].getCount()
    host = games[interaction.guild.id].host
    players=  games[interaction.guild.id].getPlayers()
    if started == True:
        await games[interaction.guild.id].hostMessage.edit(content="The game has started ! Spectate button coming soon!")
    else:
        if count < MINIMUM_PLAYER or games[interaction.guild.id].running:
            await games[interaction.guild.id].hostMessage.edit(embed=HostGameEmbed(host,players,games[interaction.guild.id].running),view=HostGameView(False))
        else:
            await games[interaction.guild.id].hostMessage.edit(embed=HostGameEmbed(host,players,False),view=HostGameView(True))

async def setup(bot:commands.Bot) -> None:

    print("Adding werewolf Cog...")
    await bot.add_cog(WerewolfCog(bot))

    