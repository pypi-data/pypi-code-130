''' Constants to be used in the organizer package. '''

SOFTWARE_EXT = [".exe",".msi", ".com,",".bat",".bin",".cmd",".ps1",".vbs"]
AUDIO_EXT = [".mp3",".m4a",".wav",".wma",".aac",".flac"]
DOC_EXT = [".txt",".doc",".pdf",".html",".xls",".xlsx",".ppt",".pptx"]
IMAGE_EXT = [".jpg",".jpeg",".png",".webp",".webm",".flv",".ogg"]
VIDEO_EXT = [".mp4",".webm",".flv",".ogg",".avi",".mkv",".wmv",".mpg",".mpeg"]
FILE_EXT_IGNORE = [".git", ".py", '.md']
FILE_IGNORE = [".DS_Store", ".gitignore", "audio", "doc", "image", "other", "software", "video",
                "__pycache__", "env", ".git"]

FILE_TYPE = {
    "software": SOFTWARE_EXT,
    "audio": AUDIO_EXT,
    "doc": DOC_EXT,
    "image": IMAGE_EXT,
    "video": VIDEO_EXT,
    "other": []
}
