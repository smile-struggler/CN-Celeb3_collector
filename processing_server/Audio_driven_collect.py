# This script is for Audio_driven_collect

# Get the enroll embedding through the enroll video. Divide the segments according to windows_size and segment_size, each segment gets the embedding separately, score by enroll embedding, 
# and retain the reserved_ratio * segment number with the highest score.
from random import sample
from tokenize import Double
import torchaudio
import torch
import numpy as np
from tqdm import tqdm
import os

from speechbrain.pretrained import EncoderClassifier
classifier = EncoderClassifier.from_hparams(source="speechbrain/spkrec-ecapa-voxceleb",run_opts={"device":"cuda:0"})

def Get_result(Audio_path, BV_number, window_size, segment_size, Audio_enroll_dict):
    file_path = os.path.join(Audio_path, BV_number + '.wav')
    signal, sample_rate = torchaudio.load(file_path)
    length = signal.size()[1]

    # Get enroll embedding
    enroll_embedding_list = []
    for enroll_second in Audio_enroll_dict[BV_number]:
        start = int(enroll_second * sample_rate)
        seg_audio = signal[ : , start : start + 1 * sample_rate]
        enroll_embedding_list.append(classifier.encode_batch(seg_audio)[0][0]) 

    sum = torch.stack(enroll_embedding_list)
    enroll_embedding = sum.mean(dim = 0)

    
    # Get test embedding
    temp_list = {}
    end_number = int((length - sample_rate * segment_size) / (window_size * sample_rate))

    for seg_number in range(end_number + 1):
    # while seg_number * window_size * sample_rate +  segment_size * sample_rate <= length:
        start = seg_number * window_size * sample_rate
        seg_audio = signal[ : , start : start + segment_size * sample_rate]
        seg_embedding = classifier.encode_batch(seg_audio)[0][0]
        
        score = float(torch.cosine_similarity(enroll_embedding, seg_embedding, dim = 0))
        temp_list[seg_number] = score
        seg_number += 1

        
    temp_list_sort = sorted(temp_list.items(), key = lambda kv:(kv[1], kv[0]), reverse = True)

    # determine the number of segments
    ans_len = int(len(temp_list_sort))
    
    audio_driven_result = BV_number
    for i in range(ans_len):
        audio_driven_result = audio_driven_result + " " + str(temp_list_sort[i][0])
    return audio_driven_result

    # with open('./Data/Audio_score/%s.txt'%BV_number,'w') as score_writer:
    #     for i in range(ans_len):
    #         score_writer.write('%d, %s\n' % (i, str(temp_list_sort[i])))
    
def run(Audio_path, BV_list, window_size, segment_size, Audio_enroll_dict):
    Audio_Driven_BV = []
    for BV_number in tqdm(BV_list, desc='Getting audio score'):
        Audio_Driven_BV.append( Get_result(Audio_path, BV_number, window_size, segment_size, Audio_enroll_dict) )
    return Audio_Driven_BV
