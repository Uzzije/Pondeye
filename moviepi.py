import os
import subprocess
from moviepy.editor import VideoFileClip, concatenate_videoclips, TextClip, CompositeVideoClip

def convert_video_to_mp4(non_mp4_file, output_filename):
    process = subprocess.Popen(['ffmpeg', '-i', non_mp4_file, output_filename], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    process.stdin.write('Y')
    has_error = process.communicate()[0]
    if has_error:
        return False
    return True

'''
#clip_ = VideoFileClip("http://img.wennermedia.com/social/rs-becky-g-ff479bcd-2818-44f0-8ca9-0cbfc79bb11c.jpg")
#clip = VideoFileClip("http://uzzije.pythonanywhere.com/media/video/progressvideo/2017/07/03/tempgkztsuskqrrj.mp4")
clip = VideoFileClip("https://pondeye.s3-us-west-1.amazonaws.com/media/video/progressvideo/2017/08/30/temperwwayblhlza.mov")
print clip.start, " ", clip.end
#clip2 = VideoFileClip("Hashtag - 8343.mp4")
clip2 = VideoFileClip("https://pondeye.s3-us-west-1.amazonaws.com/media/video/progressvideo/2017/08/30/tempotyjuhjsspgs.mov")
print clip2.duration
clip3 = VideoFileClip("https://pondeye.s3-us-west-1.amazonaws.com/media/video/progressvideo/2017/08/30/temperwwayblhlza.mov")
#clip3 = VideoFileClip("http://uzzije.pythonanywhere.com/media/video/progressvideo/2017/07/03/tempgkztsuskqrrj.mp4")
print clip3.duration
txt_clip = TextClip("Hello how are you doing", fontsize=20, color='white')
txt_clip = txt_clip.set_pos(('right','top')).set_duration(clip.duration)
video = CompositeVideoClip([clip, txt_clip])
txt_clip = TextClip("Stop", fontsize=20, color='white')
txt_clip = txt_clip.set_pos(('right','top')).set_duration(clip2.duration)
video2 = CompositeVideoClip([clip2, txt_clip])
txt_clip = TextClip("go ahead", fontsize=20, color='white')
txt_clip = txt_clip.set_pos(('right','top')).set_duration(clip3.duration)
video3 = CompositeVideoClip([clip3, txt_clip])
final_clip = concatenate_videoclips([video, video2, video3], method="compose")
final_clip.write_videofile('test_concatanates.mp4', codec='mpeg4', audio=False)
#video.write_videofile('text-test-file.mp4', codec='mpeg4', audio=False)
did_convert = convert_video_to_mp4('test_concatanates.mp4', 'new_fileb.mp4')
'''
convert_video_to_mp4('test_concatanates.mp4', 'new_fileb.mp4')


"""
def make_timeline_video(progress_set):
	video_clips = []
	for each_prog in progress_set.list_of_progress_videos.all():
		file_ = VideoFileClip(each_prog.video.url)
		txt_clip = TextClip(each_prog.name_of_progress, fontsize=20, color='white')
		txt_clip = txt_clip.set_pos(('right','bottom')).set_duration(10)
		video = CompositeVideoClip([file_, txt_clip])
		video_clips.append(video)
	final_clips = concatenate_videoclips(video_clips)
	final_clips_name = each_prog.name_of_progress + randomword(12) + ".mp4"
	final_clips.write_videofile(final_clips_name, codec='mpeg4', audio=False)
	f = open(final_clips_name)
	progress_set.video_timeline.save(final_clips_name, File(f))


import imageio
imageio.plugins.ffmpeg.download()

import numpy as np
import cv2
import os

# this two lines are for loading the videos.
# in this case the video are named as: cut1.mp4, cut2.mp4, ..., cut15.mp4
videofiles = [n for n in os.listdir('.') if n[0]=='c' and n[-4:]=='.mp4']
videofiles = ["http://uzzije.pythonanywhere.com/media/video/progressvideo/2017/07/03/tempgqfxwfvqkwlm.mp4", "http://uzzije.pythonanywhere.com/media/video/progressvideo/2017/07/03/tempgkztsuskqrrj.mp4"]

video_index = 0
cap = cv2.VideoCapture(videofiles[0])

# video resolution: 1624x1234 px
out = cv2.VideoWriter("video.avi", 
                      cv2.VideoWriter_fourcc(*'XVID'), 
                      15, (1624, 1234), 1)

while(cap.isOpened()):
    ret, frame = cap.read()
    if frame is None:
        print "end of video " + str(video_index) + " .. next one now"
        video_index += 1
        if video_index >= len(videofiles):
            break
        cap = cv2.VideoCapture(videofiles[ video_index ])
        ret, frame = cap.read()
    #cv2.imshow('frame',frame)
    out.write(frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
out.release()
#cv2.destroyAllWindows()

print "end."
"""
"""
import numpy as np
import cv2
cap = cv2.VideoCapture("ttp://uzzije.pythonanywhere.com/media/video/progressvideo/2017/07/03/tempgqfxwfvqkwlm.mp4")
video = cv2.VideoWriter('new records.avi', cv.CV_FOURCC('M', 'J', 'P', 'G'), 32, (640,360), 1)
while True:
	#capture frame by frame
	ret, frame = cap.read()
	cv2.imshow("video output", frame)

	#write the frames
	video.write(frame)
	k=cv2.waitKey(10)&0xFF
	if k == 27:
		break
cap.release()
video.release()
cv2.destroyAllWindows()

videofiles = ["http://uzzije.pythonanywhere.com/media/video/progressvideo/2017/07/03/tempgqfxwfvqkwlm.mp4", "http://uzzije.pythonanywhere.com/media/video/progressvideo/2017/07/03/tempgkztsuskqrrj.mp4"]

cap = cv2.VideoCapture(videofiles[0])

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        frame = cv2.flip(frame,0)

        # write the flipped frame
        out.write(frame)

        #cv2.imshow('frame',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
"""


