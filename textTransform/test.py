from textTransform.transform import transform

FILENAME = "spotkanie_RND_IT.mp3"
KEYWORDS = ["RND","Chołda","KiK"]
transform("./test/inputs","./test/transcripts","./test/notes", FILENAME,KEYWORDS)