import os
import shutil
import numpy as np

# 功能函数总结
# 1.递归获取文件夹和文件
# get_file_path(root_path, file_list, dir_list)

# 2.重建文件夹 
# remake_dir(out_dirPath)

# 3.计算EER 
# compute_eer(target_scores, nontarget_scores)

# 4.时间转换
# get_time(x):
# 使用方法：
# start = time.time()
# Time = my_utils.get_time(time.time() - start)

# 5.读取npy文件
# get_npy(npyName)

# 6.得到按维度平均特征
# get_dim_avg(embedding)

# 1.递归获取文件夹和文件
def get_file_path(root_path, file_list, dir_list):
    #获取该目录下所有的文件名称和目录名称
    dir_or_files = os.listdir(root_path)
    for dir_file in dir_or_files:
        #获取目录或者文件的路径
        dir_file_path = os.path.join(root_path, dir_file)
        #判断该路径为文件还是路径
        if os.path.isdir(dir_file_path):
            dir_list.append(dir_file_path)
            #递归获取所有文件和目录的路径
            get_file_path(dir_file_path, file_list, dir_list)
        else:
            file_list.append(dir_file_path)

# 2.重建文件夹
def remake_dir(out_dirPath):
    if os.path.exists(out_dirPath):
        shutil.rmtree(out_dirPath)
        print(f"已重新生成{out_dirPath}文件夹")
    os.makedirs(out_dirPath)

# 3.计算EER
def compute_det_curve(target_scores, nontarget_scores):

    n_scores = target_scores.size + nontarget_scores.size
    all_scores = np.concatenate((target_scores, nontarget_scores))
    labels = np.concatenate((np.ones(target_scores.size), np.zeros(nontarget_scores.size)))

    # Sort labels based on scores
    indices = np.argsort(all_scores, kind='mergesort')
    labels = labels[indices]

    # Compute false rejection and false acceptance rates
    tar_trial_sums = np.cumsum(labels)
    nontarget_trial_sums = nontarget_scores.size - (np.arange(1, n_scores + 1) - tar_trial_sums)

    frr = np.concatenate((np.atleast_1d(0), tar_trial_sums / target_scores.size))  # false rejection rates
    far = np.concatenate((np.atleast_1d(1), nontarget_trial_sums / nontarget_scores.size))  # false acceptance rates
    thresholds = np.concatenate((np.atleast_1d(all_scores[indices[0]] - 0.001), all_scores[indices]))  # Thresholds are the sorted scores

    return frr, far, thresholds

def compute_eer(target_scores, nontarget_scores):
    """ Returns equal error rate (EER) and the corresponding threshold. """
    frr, far, thresholds = compute_det_curve(target_scores, nontarget_scores)
    abs_diffs = np.abs(frr - far)
    min_index = np.argmin(abs_diffs)
    eer = np.mean((frr[min_index], far[min_index]))
    return eer, thresholds[min_index]

# 4.时间转换
def get_time(x):
    hour,minute,second=0,0,0
    if x>3600:
        hour=x//3600
        x%=3600
    if x>60:
        minute=x//60
        x%=60
    second=x
    return "{}小时{}分{}秒".format(hour,minute,second)

# 5.读取npy文件
def get_npy(npyName):
    return np.load(npyName, allow_pickle=True).tolist()

# 6.得到按维度平均特征
def get_dim_avg(embedding):
    for i in embedding.keys():
        temp = np.array(embedding[i])
        embedding[i] = np.average(temp, axis = 0)
    return embedding

if __name__ == '__main__':
    #  get_dim_avg
    a = {}
    a[1] = [[1,2,3],[4,5,1]]
    a[2] = [[6,4],[4,5]]
    print(get_dim_avg(a))