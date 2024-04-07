# discord news reporter
meh, one of the bots I created for my personal discord server with friends, thought I make
the code more generate and share it

## what is it?
make the bot a news reported with the system promp, the bot will send
reports to the given `REPORT_CHANNEL`, also every 7 hours the bot will create
"breaking news" and notify other text channels about it.

we mostly use it to generate stupid reports that include us in it.

## system
prompt gpt with system message, by creating in the root of the project `system.txt` file

## env
`pipenv` supports `.env` files
```sh
DISCORD_TOKEN = <discord bot token>
OPENAI_API_KEY = <openai api key>

REPORT_CHANNEL = <discord text channel id>
```

## run
```sh
>>> pipenv run serve
```
