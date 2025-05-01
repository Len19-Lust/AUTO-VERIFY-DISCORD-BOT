import discord
from discord.ext import commands
from discord.utils import get
from PIL import Image
import pytesseract
import asyncio
import os
import re  # Import regex for improved text matching

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize intents for the bot
intents = discord.Intents.default()
intents.message_content = True  # Enable message content intent
intents.members = True  # Enable member access if needed

# Initialize bot with intents
bot = commands.Bot(command_prefix="/", intents=intents)

# Alliance and role mappings
ALLIANCE_ROLE_MAPPING = {
    "Eternal Oblivion God": "O51G",
    "EternalSpirit Legion": "E51S",
    "ETERNAL BASTARDS": "E51B",
    "Eternal Gods Of War": "EGO#",
    "ETERNAL Flame": "E51F",
    # Add more alliances and roles here if needed
}


# Event triggered when the bot is ready
@bot.event
async def on_ready():
    print(f"Bot successfully logged in as {bot.user}")

    # Sync slash commands with the Discord server
    try:
        synced = await bot.tree.sync()
        print(f"Successfully synchronized {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Failed to synchronize commands: {e}")


# Helper function to extract alliance name
def extract_alliance_name(ocr_text):
    """Extract alliance name using regex from the OCR result."""
    # Match text in the format [TAG] Alliance Name
    match = re.search(r"\[.*?\]\s*[\w\s]+", ocr_text)
    if match:
        return match.group(0)  # Return the matched string
    return None


# Slash Command: Verify
@bot.tree.command(name="verify", description="Upload your game profile.")
async def verify(interaction: discord.Interaction,
                 attachment: discord.Attachment):
    # Display a custom "thinking" message with an enhanced interface
    embed_loading = discord.Embed(
        title="🔍 Verifying Your Profile...",
        description=
        ("✨ Please wait while I process your profile image and verify your alliance membership.\n\n"
         "This won't take long! ⏳"),
        color=discord.Color.blue())
    embed_loading.set_thumbnail(
        url="https://cdn-icons-png.flaticon.com/512/189/189792.png"
    )  # Loading icon
    embed_loading.set_footer(
        text="Powered by Lust Store • Thank you for your patience! 🚀")

    # Send the "thinking" embed
    await interaction.response.send_message(embed=embed_loading)

    # Check if an attachment is provided
    if not attachment:
        await interaction.followup.send(embed=discord.Embed(
            title="Error",
            description="❌ Please upload your profile image for verification.",
            color=discord.Color.red()).set_footer(text="Powered by Lust Store")
                                        )
        return

    # Save the attachment and process it
    file_path = f"temp_{interaction.user.id}.png"
    await attachment.save(file_path)

    try:
        # Process the image using OCR
        image = Image.open(file_path)
        ocr_result = pytesseract.image_to_string(image)

        # Extract alliance name (custom logic can go here)
        alliance_name = extract_alliance_name(ocr_result)
        if alliance_name:
            role_name = None
            for alliance, role in ALLIANCE_ROLE_MAPPING.items():
                if alliance in alliance_name:
                    role_name = role
                    break

            if role_name:
                # Check if the user already has the correct role
                current_roles = [role.name for role in interaction.user.roles]
                if role_name in current_roles:
                    await interaction.followup.send(embed=discord.Embed(
                        title="Already Verified",
                        description=
                        (f"✅ You've already been verified as a member of '{alliance}' "
                         f"with the role '{role_name}'."),
                        color=discord.Color.green()).set_footer(
                            text="Powered by Lust Store"))
                else:
                    # Remove old alliance roles
                    old_roles = [
                        role for role in interaction.user.roles
                        if role.name in ALLIANCE_ROLE_MAPPING.values()
                        and role.name != role_name
                    ]
                    for old_role in old_roles:
                        await interaction.user.remove_roles(old_role)

                    # Assign new role
                    role = get(interaction.guild.roles, name=role_name)
                    if role:
                        await interaction.user.add_roles(role)
                        await interaction.followup.send(embed=discord.Embed(
                            title="Verification Successful",
                            description=
                            (f"✅ Congratulations! You have been verified as a member of '{alliance}' "
                             f"and the role '{role_name}' has been assigned to you."
                             ),
                            color=discord.Color.green()
                        ).set_thumbnail(
                            url=
                            "https://cdn-icons-png.flaticon.com/512/190/190411.png"
                        )  # Success icon
                                                        .set_footer(
                                                            text=
                                                            "Powered by Lust Store"
                                                        ))
                    else:
                        await interaction.followup.send(embed=discord.Embed(
                            title="Role Not Found",
                            description=
                            f"⚠️ The role '{role_name}' could not be found on this server.",
                            color=discord.Color.orange()).set_footer(
                                text="Powered by Lust Store"))
            else:
                await interaction.followup.send(embed=discord.Embed(
                    title="Verification Failed",
                    description=
                    (f"⚠️ The alliance '{alliance_name}' does not match any registered alliances. "
                     "Please check the image or contact an administrator."),
                    color=discord.Color.orange()).set_footer(
                        text="Powered by Lust Store"))
        else:
            await interaction.followup.send(embed=discord.Embed(
                title="No Alliance Found",
                description=(
                    "⚠️ No alliance name could be detected in the image. "
                    "Please check the image or contact an administrator."),
                color=discord.Color.orange()).set_footer(
                    text="Powered by Lust Store"))
    except Exception as e:
        await interaction.followup.send(embed=discord.Embed(
            title="Error",
            description=f"❌ An unexpected error occurred: {e}",
            color=discord.Color.red()).set_footer(text="Powered by Lust Store")
                                        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

# Run the bot
TOKEN = ("TOKEN")  # Replace with your bot's token
bot.run(TOKEN)
