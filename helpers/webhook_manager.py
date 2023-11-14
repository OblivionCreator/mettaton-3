import json
import aiohttp
import disnake.ext.commands
from disnake import Webhook
import validators

c_webhooks = []

# finally i get to reuse some fucking code
# "hey i'll convert mtt2 to use Cogs & modules and just reuse most of the code"
# THAT WAS A LIE
# this is literally the FIRST BIT OF CODE that ISN'T NEW

async def send(ctx, name, message, custom_img=None):
    if isinstance(ctx, disnake.ext.commands.Context) or isinstance(ctx, disnake.Thread):
        message_obj = ctx.message
    elif isinstance(ctx, disnake.Message):
        message_obj = ctx
    if message_obj.attachments:
        attachment = message_obj.attachments[0]
        img = attachment.url
    elif custom_img:
        img = custom_img
    else:
        img = message_obj.author.display_avatar

    channel = message_obj.channel

    await send_webhook(name=name, img=img, message=message, channel=channel, author=ctx.author)
    try:
        await message_obj.delete()
    except Exception as e:
        print(f"Unable to delete message due to exception:\n{e}")


async def send_webhook(name, img, message, channel, author):
    webhook = False
    is_thread = False
    current_webhooks = get_webhook_cache()

    if isinstance(channel, disnake.Thread):
        is_thread = channel
        channel = channel.parent

    async with aiohttp.ClientSession() as session:
        if current_webhooks:
            for c, w in current_webhooks:
                if c == channel.id:
                    webhook = Webhook.from_url(w, session=session)
                    break
        else:
            current_webhooks = []

        if not webhook:
            webhook = await channel.create_webhook(name='MTT3 Generated Webhook',
                                                   reason=f'{author} ({author.id}) used MTT3 to send a message in {channel}')
            current_webhooks.append((channel.id, webhook.url))
            setWebhookCache(c_w=current_webhooks)

        if is_thread:
            await webhook.send(message, username=name, avatar_url=img, thread=is_thread)
        else:
            await webhook.send(message, username=name, avatar_url=img)


def get_webhook_cache() -> str | bool:  # Gets cache of webhooks.
    try:
        with open("./config/webhooks.json", 'r') as file:
            try:
                c_w = json.loads(file.read())
                return c_w
            except Exception:
                return False
    except FileNotFoundError:
        return False


def setWebhookCache(c_w):  # Saves webhook cache.
    with open("./config/webhooks.json", 'w+') as file:
        file.write(json.dumps(c_w))