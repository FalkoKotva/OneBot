# Derby College Bot
 A custom bot for the student-run Derby College Discord server

## Setup

### Token

To run this bot, you will need to provide it with a token to use. This can be done by creating a file called `TOKEN` in the root directory of the project, and putting the token in here. The bot will then read the token from that file.

### Database

Run the file at 'src/db_setup.py' to create the database file.

### FFMPEG

Download ffmpeg from [here](https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z), then take the files from the 'downloaded folder/bin' and drop them into a new directory: 'ffmpeg/' at the root of the project directory.

## Development Plans

- [ ] Add a command to allow users to add their own roles
- [ ] Add a cog that will pull memes from Reddit daily to keep certain channels active
- [ ] Implement music playback for voice channels
- [x] Create a ticket system for users to request help from staff
- [x] Create a ticket system for users to suggest new server features
- [ ] Refine the ticket system to be cleaner and easy to use
