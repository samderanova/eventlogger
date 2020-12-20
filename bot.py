from collections import defaultdict
from dotenv import load_dotenv
import os
import discord
import pymongo

load_dotenv()
client = discord.Client()
mongo_client = pymongo.MongoClient(os.getenv('ATLAS_URI'))

@client.event
# TESTING
async def on_ready():
    # Print this string when bot has logged in
    print(f'Logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    # Parse message only if the message content starts with '$'
    if message.content.startswith('$'):
        split_message = message.content.strip().split()
        events = mongo_client.event_logs.posts
        user = message.author.name + '#' + message.author.discriminator
        search = events.find_one({"member": user})
        
        # $addevent adds an event to a MongoDB collection
        if split_message[0] == '$addevent':
            new_event = ' '.join(split_message[1:])
            # Add to MongoDB
            if not search:
                events.insert_one({
                    "member": user,
                    "events": [new_event]
                })
            elif not search['events']:
                events.find_one_and_update(
                    { "member": user },
                    { "$set": {
                            "events": [new_event]
                        }
                    }
                )
            else:
                search['events'].append(new_event)
                events.find_one_and_update(
                    { "member": user },
                    { "$set": {
                            "events": search['events']
                        }
                    }
                )
            # Notify the user that the event was added
            await message.channel.send('Event added successfully!')
        
        # $printevents sends a message to the channel with all the events a user attended
        elif split_message[0] == '$printevents':
            # Check MongoDB
            if not search:
                await message.channel.send(f'<@{message.author.id}> has not attended any events!')
            else:
                str_events = '\n'.join(search['events'])
                await message.channel.send(f'Events attended for <@{message.author.id}>:\n{str_events}')

client.run(os.getenv('TOKEN'))
