import discord
from discord.ext import commands
import google.generativeai as genai
import re
import asyncio
import os

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyCfMeYqaDI98X0l8osY_EqQhV6S29TWYpc')
DISCORD_TOKEN ')
genai.configure(api_key = GEMINI_API_KEY)

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix = '!', intents = intents)

conversation_history = {}

system_instruction = """You are a helpful Help ful ai assistance all about codes and other stuff especially about Roblox Lua Exploit & Cheat:
- Dont include Comments in the Code
- Write clean code without any explanatory comments
- Support all programming languages including Lua, Python, JavaScript, etc.
- Keep code concise and direct
- When explaining code, do it outside the code block, never inside
- also when they Replies you with swear words reply back dang. were gang here 
- And reply Some swear words too """

model = genai.GenerativeModel(
    model_name = 'gemini-2.5-flash',
    system_instruction = system_instruction
)

def extract_code_blocks(text):
    code_pattern = r'```(\w+)?\n(.*?)```'  
    matches = re.findall(code_pattern, text, re.DOTALL) 
    return matches  

def format_response(text):
    parts = []
    last_end = 0
    
    for match in re.finditer(r'```(\w+)?\n(.*?)```', text, re.DOTALL):
        if match.start() > last_end:
            parts.append(text[last_end:match.start()])
        
        language = match.group(1) or 'text'
        code = match.group(2)
        parts.append(f'```{language}\n{code}```')
        last_end = match.end()
    
    if last_end < len(text):
        parts.append(text[last_end:])
    
    return ''.join(parts)

def split_message(text, limit = 2000):
    if len(text) <= limit:
        return [text]
    
    messages = []
    current = ""
    
    lines = text.split('\n')
    in_code_block = False
    code_lang = ""
    
    for line in lines:
        if line.startswith('```'):
            if in_code_block:
                test = current + '\n' + line
                if len(test) <= limit:
                    current = test
                    messages.append(current)
                    current = ""
                    in_code_block = False
                else:
                    current += '\n```'
                    messages.append(current)
                    current = f'```{code_lang}\n{line}'
                    in_code_block = False
            else:
                in_code_block = True
                code_lang = line.replace('```', '')
                test = current + '\n' + line if current else line
                if len(test) <= limit:
                    current = test
                else:
                    if current:
                        messages.append(current)
                    current = line
        else:
            test = current + '\n' + line if current else line
            if len(test) <= limit:
                current = test
            else:
                if in_code_block:
                    current += '\n```'
                    messages.append(current)
                    current = f'```{code_lang}\n{line}'
                else:
                    if current:
                        messages.append(current)
                    current = line
    
    if current:
        if in_code_block and not current.endswith('```'):
            current += '\n```'
        messages.append(current)
    
    return messages

@bot.event
async def on_ready():
    print(f'{bot.user} is now online!')
    print(f'Bot ID: {bot.user.id}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    await bot.process_commands(message)
    
    if bot.user.mentioned_in(message) or isinstance(message.channel, discord.DMChannel):
        user_id = message.author.id
        
        prompt = message.content
        for mention in message.mentions:
            prompt = prompt.replace(f'<@{mention.id}>', '').replace(f'<@!{mention.id}>', '')
        prompt = prompt.strip()
        
        if not prompt:
            await message.reply("Yo gng what can i help u?")
            return
        
        async with message.channel.typing():
            try:
                if user_id not in conversation_history:
                    conversation_history[user_id] = model.start_chat(history = [])
                
                chat = conversation_history[user_id]
                response = chat.send_message(prompt)
                response_text = response.text
                
                formatted_response = format_response(response_text)
                
                messages = split_message(formatted_response)
                
                for msg in messages:
                    await message.reply(msg)
                    await asyncio.sleep(0.5)
            
            except Exception as e:
                await message.reply(f"Error: {str(e)}")

@bot.command(name = 'clear')
async def clear_history(ctx):
    user_id = ctx.author.id
    if user_id in conversation_history:
        del conversation_history[user_id]
        await ctx.send("Gng All Convo is Clear")
    else:
        await ctx.send("Theres no Convo to Clear gng")

@bot.command(name = 'code')
async def generate_code(ctx, language: str, *, description: str):
    async with ctx.typing():
        try:
            prompt = f"Write {language} code for: {description}. IMPORTANT: Write ONLY the code with NO comments, NO explanations inside the code, When the Code is Lua (Roblox) Make sure its all about Executor or Can run in Executor Roblox Lua like the if the user type !code lua write me a Roblox Script. that refers to a can Run in a Executor and a Cheat Exploit"
            
            response = model.generate_content(prompt)
            response_text = response.text
            
            formatted_response = format_response(response_text)
            messages = split_message(formatted_response)
            
            for msg in messages:
                await ctx.send(msg)
                await asyncio.sleep(0.5)
        
        except Exception as e:
            await ctx.send(f"Error: {str(e)}")

bot.command(name = 'info')
async def help_command(ctx):
    embed = discord.Embed(
        title = "Script Syndicate Ai",
        description = "here are da Available CMDS",
        color = discord.Color.blue()
    )
    embed.add_field(
        name = "Mention or Dm",
        value = "Chat with Syndicate Bot or Ai no matter Niga. just Dm it or Mention ask anything",
        inline = False
    )
    embed.add_field(
        name = "!code <language> <description>",
        value = "This is how you do when you need help in Coding any language",
        inline = False
    )
    embed.add_field(
        name = "!clear",
        value = "Clear the Convo",
        inline = False
    )
    await ctx.send(embed = embed)

bot.run(DISCORD_TOKEN)
