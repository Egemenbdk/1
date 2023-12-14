import discord
from discord import app_commands
import time

intents = discord.Intents.all()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

tickets = 1
reps = 0
lastedit = 0

class verify(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = None
        
    @discord.ui.button(label="Accept", style=discord.ButtonStyle.primary)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(1180898762621722657)
        await interaction.user.add_roles(role)
        button.label = "Accept"
        await interaction.response.edit_message(view=self)

class reason(discord.ui.Modal, title="Reason"):
    reason = discord.ui.TextInput(label="Reason", required=True, style=discord.TextStyle.short)
    
    async def on_submit(self, interaction: discord.Interaction):
        category = client.get_channel(1180898763116658705)
        channel = interaction.channel
        guild = interaction.guild
        user = None
        with open('tickets.txt', 'r') as file:
            for line in file:
                line = line.split()
                if line[0] == str(channel.id):
                    user = await guild.fetch_member(int(line[1]))
        await channel.set_permissions(user, view_channel=False)
        await channel.edit(category=category)
        with open("tickets.txt", "r") as file:
            lines = file.readlines()
        filtered_lines = [line for line in lines if not line.strip().lower().startswith(str(channel.id))]
        with open("tickets.txt", "w") as file:
            file.writelines(filtered_lines)
        await interaction.response.send_message(f"Successfully closed ticket by <@{interaction.user.id}>.\nReason: `{self.reason}`")
        await user.send(f"Your ticket has been closed by <@{interaction.user.id}>\nReason: `{self.reason}`")

class close(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = None
    @discord.ui.button(label="Close", style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = interaction.guild.get_role(1180898762621722659)
        if not role in interaction.user.roles:
            embed = discord.Embed(title="Insufficient Permission", description="You do not have permission to close this ticket.", color=0xFF0000)
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        await interaction.response.send_modal(reason())

class ticket(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = None
    @discord.ui.button(label="Ticket", style=discord.ButtonStyle.primary, emoji="✉️")
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open("tickets.txt", 'r') as file:
            for line in file:
                parts = line.split()
                if parts[1] == str(interaction.user.id):
                    embed = discord.Embed(title="Error", description=f"Uh oh! Seems like you already have a ticket open at <#{parts[0]}>", color=0xFF0000)
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
        category = client.get_channel(1180898763116658704)
        guild = interaction.guild
        global tickets
        if len(str(tickets)) == 1:
            newchannel = await guild.create_text_channel(f"ticket-000{tickets}", category=category)
        elif len(str(tickets)) == 2:
            newchannel = await guild.create_text_channel(f"ticket-00{tickets}", category=category)
        elif len(str(tickets)) == 3:
            newchannel = await guild.create_text_channel(f"ticket-0{tickets}", category=category)
        elif len(str(tickets)) == 4:
            newchannel = await guild.create_text_channel(f"ticket-{tickets}", category=category)
        tickets += 1
        
        await newchannel.set_permissions(interaction.user, 
                                          view_channel=True,
                                          read_messages=True,
                                          send_messages=True,
                                          embed_links=True,
                                          attach_files=True,
                                          add_reactions=True,
                                          use_external_emojis=True,
                                          use_external_stickers=True,
                                          read_message_history=True)
        
        embed = discord.Embed(title="Welcome", description="Hey there! Support will be with you soon, while they come please provide information about what you need.", color=0x3B3B3B)
        await newchannel.send(content=f"||<@&1178214644700172318>|| Hey <@{interaction.user.id}>", embed=embed, view=close())
        
        await interaction.response.send_message(f"Successfully opened a ticket at <#{newchannel.id}>.", ephemeral=True)
        
        with open("tickets.txt", "w") as file:
            file.write(f"{newchannel.id} {interaction.user.id}\n")

@client.event
async def on_message(message):
    if message.author.id in [1180283648247877653, 1180894880843694100]:
        return
    if message.channel.id == 1180898763116658702:
        if "discord.gg/" in message.content:
            await message.delete()
            with open('warns.json', 'r') as file:
                data = json.load(file)

            user_id = str(message.author.id)
            if user_id not in data:
                data[user_id] = 0

            data[user_id] += 1

            if data[user_id] >= 5:
                if data[user_id] >= 100:
                    await message.author.send("You have been banned for repeatedly spamming an invite link after being kicked.")
                    await message.author.ban(reason="Spamming invite links.")
                    return
                data[user_id] = 100

                await message.author.send("You have been kicked for spamming an invite link, if you continue you will be banned.\nJoin back at discord.gg/ziggyshop")
                await message.author.kick()
                
            with open('warns.json', 'w') as file:
                json.dump(data, file, indent=2)
            return
    if message.channel.id == 1180898763116658698:
        if message.content.startswith("+rep "):
            channel = client.get_channel(1180898763116658698)
            global reps
            reps += 1
            global lastedit
            if not time.time() > lastedit + 300:
                return
            await channel.edit(name=f"🤝┃reps-{reps}")
            lastedit = time.time()
            return

@client.event
async def on_member_join(member):
    channel = client.get_channel(1180898762894364799)
    await channel.send(f"Welcome to Our Shop <@{member.id}>!")
    time.sleep(4)
    role = member.guild.get_role(1180898762621722658)
    for role in member.roles:
        pass
    if role in member.roles:
        role = member.guild.get_role(1180898762621722657)
        await member.add_roles(role)
        channel = client.get_channel(1180898763116658698)
        message = await channel.send(f"<@{member.id}> Please rep")
        time.sleep(20)
        await message.delete()

@client.event
async def on_ready():
    channel = client.get_channel(1180898763116658699)
    await channel.purge()
    embed = discord.Embed(title="Create a ticket", description=f"Click the button below to create a ticket if you have an issue with the bot or if you need support.", color=0x3B3B3B)
    await channel.send(embed=embed, view=ticket())
    channel = client.get_channel(1180898762894364797)
    await channel.purge()
    embed = discord.Embed(title="Rules", description="- Follow [Discord's TOS](https://discord.com/terms)\n- Be respectful to staff\n- Don't be stupid", color=0x58BAFF)
    embed.set_footer(text="By verifying, you agree to our rules.")
    await channel.send(embed=embed, view=verify())
    print("Ready!")

client.run("MTE4MDg5NDg4MDg0MzY5NDEwMA.GBeSgn.dTfekVfDYQkGcN-DMMiTRWoQvn7bY5bjzmWwFU")
