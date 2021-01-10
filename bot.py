import os
import discord
import time
import datetime
import requests
import json
import threading
import sys
import asyncio
import argparse
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

start_time = time.time()

url = None
pages=1
session_cookie = None
channel_id = None
prevsolve=""
TOKEN = None

client = discord.Client()

def team(teamname):
  global url,session_cookie
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+"/api/v1/scoreboard", headers=headers, cookies=cookies,verify=False)
  data = response.json()['data']
  msg="Team Info "+"\n"
  for i in data:
    if i['name'].lower() == teamname.lower():
      msg+="**"+i['name']+"** => Current Score: " + str(i['score']) + ""+ "\n\n"
      msg+="Team Members" + "\n"
      for j in i['members']:
        msg+=j['name'] + "\n"
      return msg
  return {"Error":"Teamname Not found"}

def scoreboard():
  global url,session_cookie
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+"/api/v1/scoreboard", headers=headers, cookies=cookies,verify=False)
  data = response.json()['data']
  message="```"
  message+="\n"
  for i in data[:20]:
    message+="#"+str(i['pos'])+" : "+str(i['name'])+" ==> "+str(i['score'])+" points"+"\n"
  message+="```"
  return message

def descchall(challname):
  global url,session_cookie
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+"/api/v1/challenges", headers=headers, cookies=cookies,verify=False)
  data = response.json()['data']
  category = []
  for i in data :
    category.append(i['category'])
    if i['name'].lower() == challname.lower():
      return {"name":i['name'],'points':i['value'],'type':i['type'],'category':i['category']}
  
  if challname in category:
    challs=[]
    for i in data :
      if i['category'].lower() == challname.lower():
        challs.append(i['name'])
    return challs

  return {"Error":"Challenge or Category Name Not found"}

def challenge():
  global url,session_cookie
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+"/api/v1/challenges", headers=headers, cookies=cookies,verify=False)
  data = response.json()['data']
  chall={i['id']:i['name'] for i in data}
  return chall

def submission():
  global session_cookie,url,pages
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+'/api/v1/submissions?page={}'.format(pages), headers=headers, cookies=cookies,verify=False)
  data = response.json()['data']
  data = data[len(data)-1]
  pages=response.json()['meta']['pagination']['pages']
  if data['type'] !="incorrect":
    response = requests.get(url+'/api/v1/users', headers=headers, cookies=cookies,verify=False)
    users = {i["id"]:i["name"] for i in response.json()['data']}
    return [users[data["user_id"]],data['challenge_id'],data['date']]
  else:
    return []

def author():
  global url,session_cookie
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+"/api/v1/challenges", headers=headers, cookies=cookies,verify=False)
  data = response.json()['data']
  authors = {}
  for i in data:
    try:
      tag = i['tags'][0]['value'].split(":")[1].strip()
      authors[tag] = []
      for j in data:
        if j['tags'][0]['value'].split(":")[1].strip() == tag:
          authors[tag].append(j['name'])
    except:
      pass
  return authors

def position(user):
  global session_cookie,url
  headers = {
      'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
      'Connection': 'keep-alive',
      'Upgrade-Insecure-Requests': '1',
  }
  cookies =  {
    'session': str(session_cookie)
  }
  response = requests.get(url+"/api/v1/scoreboard", headers=headers, cookies=cookies,verify=False)
  data = response.json()['data']
  
  for i in data:
    for j in i['members']:
      if j['name'] == user:
        return [i['pos'],i['score']]
  
  return {"Error":"User not Found"}

@client.event
async def on_ready():
  global channel_id,prevsolve
  await client.change_presence(activity=discord.Game(name="Type /help for help"))
  await client.wait_until_ready()
  channel = client.get_channel(channel_id)
  
  #Clear all history Message
  async with channel.typing():
    await channel.purge(limit=None)
  
    print('{} is connected\n'.format(client.user))
    await client.get_channel(channel_id).send("""```bash
  "Hey forks!, This is **DisCTF** who joined your channel. Bot will keep you updated on live scoreboard and Live valid submission and their respective rank with score of the player who solved the challenge recently. For More info and help Type /help."
  ```""")  
  
  score = scoreboard()
  em2 = discord.Embed(title="ScoreBoard",description=score,colour=0x080f5d)
  message = await channel.send(embed=em2)
  await message.pin()
  
  while 1:
    score=scoreboard()
    chall = challenge()
    try:
      check = submission()
      temp = " ".join(str(v) for v in check)
      if check!= None and temp!=prevsolve:
        prevsolve=temp
        pos,score=position(check[0])
        check = "**"+check[0]+"**"+" Has Solved Challenge "+"**"+chall[int(check[1])]+"**" +" (Current Rank: "+str(pos)+", Total score: "+str(score)+")" +" Solved at " + datetime.datetime.strptime(check[2],"%Y-%m-%dT%H:%M:%S.%f%z").strftime("%b %d %Y %H:%M:%S") #+ time.strftime("%H:%M:%S", time.localtime())
        channel = client.get_channel(channel_id)
        em1 = discord.Embed(title="Kudos",description=check,colour=0x46befa)
        await channel.send(embed=em1)
      
      hours, rem = divmod(time.time()-start_time, 3600)
      minutes, seconds = divmod(rem, 60)

      if minutes%1 == 0 and int(seconds)==0 and (seconds-int(seconds))<=1:
        channel = client.get_channel(channel_id)
        em2 = discord.Embed(title="ScoreBoard",description=score,colour=0x080f5d)
        message = await channel.send(embed=em2)
        
        #Remove all pinned message and Add new one
        await channel.purge(limit=None,check=lambda msg: msg.pinned)
        await message.pin()
        
    except Exception as e:
      #print(e)
      pass
    await asyncio.sleep(0.5)

@client.event
async def on_message(message):
  channel = message.channel

  if str(client.user) != str(message.author):
    if message.content.startswith('/'):
      cmd=message.content.replace("/","").split(" ",1)
      if cmd[0].lower() == "help":
        embed=discord.Embed(
          title="Help",
          description="DisCTF bot monitors real-time solves and submission, filters out valid ones, sends notifications on each solves with current rank and score of the person along with timestamp. We have a live scoreboard that notifies the people on interval of 1 minute with ranks of the top 20 players. It has custom commands to get information or detail from CTFd framework and notify with handly flost messages",
          colour=0x46befa
          )
        embed.set_author(name="DisCTF", url="https://disctf.live")
        embed.set_thumbnail(url="https://i.imgur.com/352sSJI.png")
        embed.add_field(name="/team teamname", value="Display Team with Members and team point ", inline=False)
        embed.add_field(name="/user username", value="Team rank with your individual contribution score ", inline=False)
        embed.add_field(name="/scoreboard", value="Scoreboard with Top 20 teams ", inline=True)
        embed.add_field(name="/scoreboard full", value="Return link for Full Scoreboard ", inline=True)
        embed.add_field(name="/challenge list", value="List out all active challenges", inline=False)
        embed.add_field(name="/challenge challenge_name", value="Challenge Complete Info ", inline=True)
        embed.add_field(name="/challenge category", value="Challenge all under category", inline=True)
        embed.add_field(name="/author list", value="Return all list of challenge Authors ", inline=False)
        embed.add_field(name="/author Challenge_Name", value="Return Which Author for Respective Challenge ", inline=True)
        embed.add_field(name="/author Author_name", value="Return list of challenge by Author ", inline=True) 
        await channel.send(embed=embed)
      
      elif cmd[0].lower() == "author":
        authors = author()
        challs = [j for i in authors.values() for j in i]
        
        try:
          if cmd[1].lower() == "list":#Return list of authors
            msg= "Here is the List of Authors \n\n"
            for i in authors.keys():
              msg += str(i) + "\n"
            await channel.send(msg)

          else:
            if cmd[1] in authors.keys(): #return challenge list
              msg = "List of Challenges Created by {} \n\n".format(cmd[1])
              for i in authors[cmd[1]]:
                msg += str(i) + "\n"
              await channel.send(msg)

            elif cmd[1].strip() in challs: #return author for author 
              for auth,chall in authors.items():
                if cmd[1].strip() in chall:
                  auth_id = auth
                  break
              await channel.send("<@{}> Ping at @{} for challenge Queries".format(message.author.id,auth_id))

            else:
              raise Exception
          
        except:
          await channel.send("Challenge name or Author name Not Found")

      elif cmd[0].lower() == "user":
        data = position(cmd[1])
        if type(data) == type(list()):
          pos,score=data
          msg="""```ini
  -Your Current Rank: {} and Total score: {}
  ```""".format(str(pos),str(score))
          await channel.send(msg)
        else:
          await channel.send(data['Error'])

      elif cmd[0].lower() == "challenge":
        challenges=challenge()
        chall = [name for id,name in challenges.items()]
        msg="List of Active challenge"+"\n"
        if cmd[1] == "list":
          for i in range(len(chall)):
            msg+="> "+str(i+1)+". "+chall[i] +"\n"
          await channel.send(msg)
        else:
          chall = descchall(cmd[1])
          if type(chall) == type(list()):
            msg="List of "+cmd[1]+" Challenges \n"
            for i in range(len(chall)):
              msg+="> "+str(i+1)+". "+chall[i] +"\n"
            await channel.send(msg)

          elif "Error" not in chall.keys():
            embed=discord.Embed(title="Challenge Description")
            embed.add_field(name="Name", value=chall['name'], inline=True)
            embed.add_field(name="Category", value=chall['category'], inline=True)
            embed.add_field(name="Points", value=chall['points'], inline=True)
            embed.add_field(name="Type", value=chall['type'], inline=True)
            await channel.send(embed=embed)
          else:
            await channel.send(chall['Error'])
      
      elif cmd[0].lower() == "scoreboard":
        try:
          if cmd[1].lower() == "full":
            await channel.send("Checkout the link for Full Scoreboard: "+url+"/scoreboard")
          else:
            raise Exception
        except:
          score = scoreboard()
          em2 = discord.Embed(title="ScoreBoard",description=score,colour=0x080f5d)
          await channel.send(embed=em2)
        
        #Remove all pinned message and Add new one
        await channel.purge(limit=None,check=lambda msg: msg.pinned)
        await message.pin()

      elif cmd[0].lower() == "team":
        teaminfo = team(cmd[1])
        if type(teaminfo) == type(str()):
          await channel.send(teaminfo)
        else:
          await channel.send(teaminfo['Error'])

      else:
        await channel.send('Invalid command')
  
if __name__ == "__main__":
  if TOKEN == None:
    print("ERROR : Required Discord bot TOKEN")
    exit()

  parser = argparse.ArgumentParser()
  parser.add_argument("-s","--session",action='store',help="Takes argumnet of Session Cookie",required=True)
  parser.add_argument("-u","--url",action='store',help="Takes CTFd platform URL",required=True)
  parser.add_argument("-c","--channel",action='store',help="Takes discord channel ID",required=True)
  args = parser.parse_args()
  
  channel_id = int(args.channel)
  url = args.url
  if url[-1] == "/":
    url = "".join([i for i in url[:-1]])

  session_cookie = args.session
  
  headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
  }
  cookie =  {
    'session': str(session_cookie)
  }
  
  resp = requests.get(url+"/api/v1/users",headers=headers,cookies=cookie,verify=False)                    
  if int(resp.status_code)!=200:
    print("ERROR : Either Session cookie is not correct or Does not have privilege as admin")
    exit()
  
  client.run(TOKEN)