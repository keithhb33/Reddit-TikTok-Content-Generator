import moviepy.editor as mpe
import math
import os.path
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
from ffmpeg import *
import ffmpeg
from moviepy.audio.io.AudioFileClip import AudioFileClip
import time
import json
import random
import pyttsx3
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from moviepy.editor import *
from os import path
import numpy
from numpy import *
import speech_recognition as sr
from pydub import *
import pydub


r = sr.Recognizer()




counter = 0

with open('dataset/comments.json', 'r', encoding="utf-8") as json_comments_file:
	json_comments_load = json.load(json_comments_file)
comments = json_comments_load['comments']

with open('dataset/submissions.json', 'r', encoding="utf-8") as json_submissions_file:
    json_submissions_load = json.load(json_submissions_file)
submissions = json_submissions_load['submissions']

json_comments_length = len(comments[0])
json_submissions_length = len(submissions[0])

comment_number = random.randint(0, json_comments_length-1)
submission_number = random.randint(0, json_submissions_length-1)

count=0

files_to_be_removed = []
    
def toBeRemoved(file):
    files_to_be_removed.append(file)
    with open("results/duplicates.txt", "w") as txt_file:
        for line in files_to_be_removed:
            txt_file.write("".join(line) + "\n")
    return files_to_be_removed

def combine_audio(vidname, audname, outname, fps=60):
    my_clip = mpe.VideoFileClip(vidname)
    audio_background = mpe.AudioFileClip(audname)
    final_clip = my_clip.set_audio(audio_background)
    final_clip.write_videofile(outname, fps=fps)

def textToSpeech(title, comment1, comment2, comment3, vid):
    global count
    global counter
    
    text = str(title) + ". " + str(comment1) + ". " + str(comment2) + ". " + str(comment3)
    engine = pyttsx3.init()
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.setProperty("rate", 176)
    engine.save_to_file(text, 'text.mp3')
    engine.runAndWait()

    mp3_length = int(math.ceil(AudioFileClip("text.mp3").duration))
    mp4_length = int(math.ceil(AudioFileClip("footage.mp4").duration))
    
    start_time = random.randint(10, mp4_length-30)
    ffmpeg_extract_subclip("footage.mp4", start_time, (mp3_length + start_time), targetname="tempfootage.mp4")
    temp_mp4_length = int(math.ceil(AudioFileClip("tempfootage.mp4").duration))
        
   
    for o in range (-(7-1), (7-1)):
        if temp_mp4_length != mp3_length:
            ffmpeg_extract_subclip("footage.mp4", start_time, (mp3_length + start_time + (o)), targetname="tempfootage.mp4")
            temp_mp4_length = int(round(AudioFileClip("tempfootage.mp4").duration))
        else:
            ffmpeg_extract_subclip("footage.mp4", start_time, (mp3_length + start_time), targetname="tempfootage.mp4")
    
           
    if mp3_length >= 14:
        combine_audio("tempfootage.mp4", "text.mp3", "results/final" + str(int((counter+1))) + ".mp4")  # i create a new file
    
        video_file = "results/final" + str(int((counter+1))) + ".mp4"
        audio_file = "final" + str(int((counter+1))) + "_audio" + ".mp3"
        
        video = VideoFileClip(os.path.join(video_file))
        video.audio.write_audiofile(os.path.join(audio_file))
        
        audio_file_wav = "final" + str(int((counter+1))) + "_audio.wav"
        
        AudioSegment.from_mp3(audio_file).export(audio_file_wav, format="wav")
        audio_file = audio_file_wav
        
        with sr.AudioFile(audio_file) as source:
            audio = r.record(source)
            transcript = r.recognize_google(audio)
        
        print(transcript)
        
        #WRITE CODE THAT COMPARES THIS TRANSCRIPT TO THE TRANSCRIPTS OF ALL OF THE !!OTHER!! VIDEOS IN THE RESULTS DIRECTORY. IF THEY MATCH AND ARE DIFFERENT TITLES, DELETE THEM
        dir_path = r'results'
        number_of_videos = (len([entry for entry in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, entry))]))

        if number_of_videos > 1 and (counter+1) > 1:
                    
            video_file_compared = "results/final" + str(int((counter))) + ".mp4"
            audio_file_compared = "final" + str(int((counter))) + "_audio.mp3"

            vid = VideoFileClip(os.path.join(video_file_compared))
            if not os.path.exists(audio_file_compared):
                vid.audio.write_audiofile(os.path.join(audio_file_compared))
        
            audio_file_wav_compared = "final" + str(int((counter+1))) + "_audio.wav"
        
            AudioSegment.from_mp3(audio_file_compared).export(audio_file_wav_compared, format="wav")
            audio_file_compared = audio_file_wav_compared
        
            with sr.AudioFile(audio_file_compared) as source:
                audio_compared = r.record(source)
                try:
                    transcript_compared = r.recognize_google(audio_compared)
                except:
                    print("")
                
            if transcript == transcript_compared and counter != (counter+1) and (counter+1) != 2:
                print("DUPLICATE DETECTED")
                time.sleep(1)
                toBeRemoved("results/final" + str(int((counter+1))) + ".mp4")
                
        counter+=1
        

        
def getCommentData(id, title, vid):
    for p in range(0, json_comments_length, 3):
        for t in comments:
            comment_id = t[p]['submission_id']
            comment_body = t[p]['body']
            if p < (json_comments_length / 3):
                comment_2_id = t[p+1]['submission_id']
                comment_2_body = t[p+1]['body']
                
                comment_3_id = t[p+2]['submission_id']
                comment_3_body = t[p+2]['body']
            else:
                comment_2_id = t[p]['submission_id']
                comment_2_body = t[p]['body']
    
                comment_3_id = t[p]['submission_id']
                comment_3_body = t[p]['body']

            try:    
                if (id == comment_id and id == comment_2_id and id == comment_3_id and ("PLEASE READ THIS MESSAGE IN ITS ENTIRETY BEFORE TAKING ACTION" not in comment_body) and ("PLEASE READ THIS MESSAGE IN ITS ENTIRETY BEFORE TAKING ACTION" not in comment_2_body)):
                    textToSpeech(title, comment_body, comment_2_body, comment_3_body, vid)
            except ValueError:
                getCommentData(id, title, vid)

def getSubmissionData(vid):#Must stay within this loop
    for w in range(json_submissions_length):
        for i in submissions:
            submission_id = i[w+vid]['id']
            submission_title = i[w+vid]['title']
            getCommentData(submission_id, submission_title, vid)


vid_number = int(input("Enter video # to start from: "))
counter = counter + vid_number
getSubmissionData(int(vid_number))

for l in files_to_be_removed:
    os.remove(l)



#separate the title and comment methods
#create mp3 with just title
#create mp3 with three comments
#combine respective
    #ADD r/CONFESSIONS