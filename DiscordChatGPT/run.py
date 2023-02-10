from App.DiscordLib.DiscordAPI import client, discord_token

if __name__ == "__main__":
    print("DiscordBot is running...")
    client.run(discord_token)