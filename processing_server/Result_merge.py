def run(Audio_Driven_BV, Video_Driven_BV):
    result = []

    audio_dic = {}
    for audio_line in Audio_Driven_BV:
        audio_line = audio_line.strip().split()
        num = len(audio_line)
        audio_dic[audio_line[0]] = []
        for i in range(1, num):
            audio_dic[audio_line[0]].append(audio_line[i])
    
    for video_line in Video_Driven_BV:
        video_line = video_line.strip().split()
        BV_number = video_line[0]
        num = len(audio_dic[BV_number])

        ans_string = BV_number + ' ' + audio_dic[BV_number][0]
        
        for i in range(1, num):
            ans_string = ans_string + ',' + audio_dic[BV_number][i]

        ans_string = ans_string + ' ' + video_line[1]

        num = len(video_line)
        for i in range(2, num):
            ans_string = ans_string + ',' + video_line[i]
        
        result.append(ans_string)
    
    return result

Data_root_path = './DEMO_DATA'
# The path for Audio_Driven
Path_Audio_Driven_BV = '%s/audio_driven.txt'%Data_root_path
# Path_Audio_Driven_Result = './Data/Audio_Driven_Result'

# The path for Video_Driven
Path_Video_Driven_BV = '%s/video_driven.txt'%Data_root_path

Path_Result = '%s/result.txt'%Data_root_path