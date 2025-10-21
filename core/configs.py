import os
from dotenv import load_dotenv

load_dotenv()

ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")


test_request = {
  "task_name": "test_task_3blocks_with_audio",

  "video_blocks": {
    "block1": [
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/8081_O_GL_v1%20(1).mp4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/43r43.mp4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/2025-09-14%2016.02.30.mp4"
    ],
    "block2": [
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/8849_1.mp4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/IMG_5170.MP4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/Untitled%20design%20(5).mp4"
    ],
    "block3": [
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/Untitled%20design%20(8).mp4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/img_Asset_8320b1e5-fa98-4df0-876a-8b109b7b0969_dace9d4f-ab36-4c10-bd5d-b74fa58cbca3.mp4",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/img_test3242task_7c062ef2-e570-43c6-9f0e-d92399e08282.mp4"
    ]
  },

  "audio_blocks": {
    "audio1": [
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/audiobible1.mp3",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/audiobible2.mp3",
      "https://storage.googleapis.com/walkfit/SF/008_e1d1bf5e-9b7b-4fad-95dc-7205693bf215/audiobible3.mp3"
    ]
  },

  "voice_blocks": {
    "voice1": [
      {
        "text": "Welcome to Plink — the ultimate platform for gamers who want to find perfect teammates. Whether you’re into competitive shooters, massive online RPGs, or just casual matches after work, Plink instantly connects you with players who match your skill level, playstyle, and favorite games. Say goodbye to random toxic lobbies, and hello to a team that shares your goals and passion for gaming.",
        "voice": "Sarah"
      },
      {
        "text": "Plink makes finding the right teammates effortless. With advanced matchmaking, personalized recommendations, and a growing global community, you’ll never play alone again. Discover players who speak your language, share your schedule, and complement your strengths in-game. Build real connections that last beyond a single match, and turn every session into a winning experience.",
        "voice": "George"
      },
      {
        "text": "Join millions of gamers who already use Plink to level up their experience. Track your stats, showcase your highlights, and let the algorithm introduce you to teammates who truly fit your vibe. From quick ranked queues to epic weekend marathons, Plink ensures you always have the right squad. Download today and see how gaming feels when you’re never alone in the lobby again.",
        "voice": "Will"
      }
    ]
  }
}
