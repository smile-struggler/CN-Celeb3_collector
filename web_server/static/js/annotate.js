
// let BVlist = [];// raw information in txt
// let BV_clip_count = [];// raw information in txt
// let BV_clips_statu = [];
// let BV_clips_av_statu = [];
// let BV_clips_score_rank = [];
let current_video = 0;
let current_clips = 0;
let clip_count = 0;
let clip_statu = [];//0:undetermained, 1:retain, 2:delete
let video_length = [];

let audio_idx2rank = [];
let video_idx2rank = [];
let audio_rank2idx = [];
let video_rank2idx = [];
let audio_status = [];
let video_status = [];


let current_time_readed = 0;

let audio_embeddings = [];
let segment_length = 5;
let zoom_length = 3; //[idx-3, idx+3]
let canvas_border = 3;
let tolerance = 5;
let stop = true;
const AUTO_DELETE_COLOR = '#f0e130';
const DELETE_COLOR = '#b31b1b';
const CURRENT_COLOR = '#00FFFF';
const TODO_COLOR = '#848482';
const SAVE_COLOR = '#8DB600';
const HIGHLIGHT_COLOR = '#9966cc';

const STATU_AUTO_DELETE = -5;
const STATU_AUTO_DELETE_AUDIO = -3;
const STATU_AUTO_DELETE_VIDEO = -2;
const STATU_DELETE = -1;
const STATU_RETAIN_AUDIO = 1;
const STATU_RETAIN_VIDEO = 2;
const STATU_RETAIN_BOTH = 3;
const STATU_TOCHECK = 0;

const COMMAND_SEEK = 'SEEK|';
const COMMAND_BEGIN = 'begin';
const COMMAND_SETT = 'SETT|';

window.onload = function () {
    load_video();
}

function neighbour(rank) {
    min_rank = rank - tolerance + 1;
    max_rank = rank + tolerance - 1;
    min_rank = min_rank < 0 ? 0 : min_rank;
    max_rank = max_rank < clip_statu.length ? max_rank : clip_statu.length;
    return { min_rank: min_rank, max_rank: max_rank }
}

function auto_delete_video() {
    for (let i = 0; i < clip_statu.length - tolerance + 1; i++) {
        let flag = 0;
        for (let j = i; j < i + tolerance; j++) {
            if (have_no_video(video_rank2idx[j]) == 0) {
                flag = 1;
                break;
            }
        }
        if (flag == 0) {
            return i;
        }
    }
    return video_delete_rank;
}

function auto_delete_audio(idx) {
    for (let i = 0; i < clip_statu.length - tolerance + 1; i++) {
        let flag = 0;
        for (let j = i; j < i + tolerance; j++) {
            if (have_no_audio(audio_rank2idx[j]) == 0) {
                flag = 1;
                break;
            }
        }
        if (flag == 0) {
            return i;
        }
    }
    return audio_delete_rank;
}

function have_no_audio(clip_idx) {
    if (clip_statu[clip_idx] == STATU_RETAIN_VIDEO ||
        clip_statu[clip_idx] == STATU_DELETE ||
        audio_idx2rank[clip_idx] >= audio_delete_rank) { return 1; }
    return 0;
}

function have_no_video(clip_idx) {
    if (clip_statu[clip_idx] == STATU_RETAIN_AUDIO ||
        clip_statu[clip_idx] == STATU_DELETE ||
        video_idx2rank[clip_idx] >= video_delete_rank) { return 1; }
    return 0;
}

function update_according_to_score() {
    // delete
    video_delete_clip = auto_delete_video();
    audio_delete_clip = auto_delete_audio();
    for (let i = 0; i < clip_statu.length; i++) {
        if (clip_statu[i] == STATU_AUTO_DELETE) {
            clip_statu[i] = STATU_TOCHECK;
        }
    }
    for (let i = 0; i < clip_statu.length; i++) {
        if (video_idx2rank[i] >= video_delete_clip && audio_idx2rank[i] >= audio_delete_clip && clip_statu[i] == STATU_TOCHECK) {
            clip_statu[i] = STATU_AUTO_DELETE;
        }
    }
}

function parse_process_res(line) {
    clip_statu = [];
    audio_idx2rank = [];
    video_idx2rank = [];
    audio_rank2idx = [];
    video_rank2idx = [];
    audio_status = [];
    video_status = [];

    content = line.split(' ');
    audio_rank = content[1].split(',');
    video_rank = content[2].split(',');
    // init status

    clip_count = audio_rank.length;
    Video_length = video_rank.length;
    video_clip_count = video_rank.length;
    for (let i = 0; i < audio_rank.length; i++) {
        audio_idx2rank.push(0);
        video_idx2rank.push(video_clip_count);
        audio_status.push(STATU_TOCHECK);
        video_status.push(STATU_TOCHECK);
        clip_statu.push(STATU_TOCHECK);
    }
    // set rank
    for (let i = 0; i < audio_rank.length; i++) {
        audio_rank2idx.push(parseInt(audio_rank[i]));
        audio_idx2rank[parseInt(audio_rank[i])] = i;
    }
    for (let i = 0; i < audio_rank.length; i++) {
        if (i < video_rank.length) {
            video_rank2idx.push(parseInt(video_rank[i]));
            video_idx2rank[parseInt(video_rank[i])] = i;
        }
    }
    // fix video clips
    let j = video_rank.length
    for (let i = 0; i < audio_rank.length; i++) {
        if (video_idx2rank[i] == video_rank.length) {
            video_idx2rank[i] = j;
            j += 1;
            video_rank2idx.push(i);
            video_status[i] = STATU_TOCHECK;
        }
    }
}

function pre_retain_delete() {
    audio_delete_rank = clip_statu.length - parseInt(delete_ratio * clip_statu.length)
    video_delete_rank = video_length - parseInt(delete_ratio * video_length)

    for (let i = 0; i < clip_statu.length; i++) {
        // if (video_idx2rank[i] <= video_retain_rank && audio_idx2rank[i] <= audio_retain_rank) {
        //     clip_statu[i] = STATU_RETAIN_BOTH;
        //     console.log(i+"!!")
        // }
        if (video_idx2rank[i] >= video_delete_rank && audio_idx2rank[i] >= audio_delete_rank) {
            clip_statu[i] = STATU_DELETE;
            console.log(i + "??")
        }
    }
}
// load video and init canvas
function load_video() {
    document.getElementById('spkj').src = "https://player.bilibili.com/player.html?bvid=" + bvid + "&page=1&danmaku=0"
    let img_file = `/static/media/image/${bvid}.png?`+new Date().getTime();
    document.getElementById("speaker").src = img_file;

    $.ajax({
        async: false,//同步
        url: `/annotate/video/get_process_res?bvid=${bvid}&username=${username}`,
        success: function (ret) {
            res = JSON.parse(ret)
            if (res['status'] === 'success') {
                console.log(res['res']);
                parse_process_res(res['res'].toString());
            }
        }
    }
    )

    retain_ratio = 0
    delete_ratio = 0.15
    pre_retain_delete()

    update_canvas(0);
    let i = 0;

    while (i < clip_statu.length) {
        if (clip_statu[i] == STATU_TOCHECK) {
            current_clips = i;
            seek_to_clip();
            break;
        }
        i++;
    }
    update_count();
    update_canvas(current_clips * segment_length);
}
let temp_begin_times = 0;
window.addEventListener('message', e => {
    if (e.data == "get_begin") {
        temp_begin_times = 1;
        seek_to_clip();
    }
    else {
        currentTime = e.data;
        current_time_readed = e.data;
        update_canvas(currentTime);
    }
    if (temp_begin_times == 0) {
        document.getElementById('spkj').contentWindow.postMessage(COMMAND_BEGIN, '*');
    }

})
// add onclick to canvas to control video player
let canvas = document.getElementById('myCanvas');
canvas.addEventListener('click', function (e) {
    var x, y;
    if (e.layerX || e.layerX == 0) {
        x = e.layerX;
        y = e.layerY;
    } else if (e.offsetX || e.offsetX == 0) {
        x = e.offsetX;
        y = e.offsetY;
    }
    var percent = x / canvas.width;
    var time = percent * clip_count * segment_length;
    command = COMMAND_SETT + time.toString();
    document.getElementById('spkj').contentWindow.postMessage(command, '*');
}, false);
let zoom = document.getElementById('zoomCanvas');
zoom.addEventListener('click', function (e) {
    var x, y;
    if (e.layerX || e.layerX == 0) {
        x = e.layerX;
        y = e.layerY;
    } else if (e.offsetX || e.offsetX == 0) {
        x = e.offsetX;
        y = e.offsetY;
    }
    var percent = x / zoom.width;
    boundaries = get_current_zoom_boundary(current_time_readed);
    var time = (percent * (2 * zoom_length + 1) + boundaries[0]) * segment_length;
    command = COMMAND_SETT + time.toString();
    document.getElementById('spkj').contentWindow.postMessage(command, '*');
}, false);

//Button function
// let todo_flag = 0;
// for (let i = 0; i < clip_statu.length; i++) {
//     if (clip_statu[i] == STATU_TOCHECK) {
//         todo_flag = 1;
//         break;
//     }
// }
// if(todo_flag == 1){
//     alert("仍有未标注的段！请完成标注后再到下一个视频！");
//     back_clip();
//     return;
// }

function goto_current(clip_idx) {
    current_clips = parseInt(current_time_readed / segment_length)
    command = COMMAND_SEEK + (current_clips).toString();
    document.getElementById('spkj').contentWindow.postMessage(command, '*');
    stop = true;
}
function seek_to_clip() {
    command = COMMAND_SEEK + (current_clips).toString();
    document.getElementById('spkj').contentWindow.postMessage(command, '*');
    stop = true;
}
function next_clip() {
    let old_clip = current_clips;
    current_clips++;
    // skip clips that need no check
    while (current_clips < clip_count) {
        if (clip_statu[current_clips] != STATU_TOCHECK) {
            current_clips++;
        } else {
            break;
        }
    }
    if (current_clips < clip_count) {
        seek_to_clip();
        update_count();
    } else {
        current_clips = old_clip;
        alert("已到达该视频最后一段~如果已完成全部标注请按“上传标注信息”按钮！");
    }
}

function next_clip_no_skip() {
    let old_clip = current_clips;
    current_clips++;
    
    // skip clips that need no check
    while (current_clips < clip_count) {
        if (clip_statu[current_clips] == STATU_AUTO_DELETE) {
            current_clips++;
        } else {
            break;
        }
    }

    if (current_clips < clip_count) {
        seek_to_clip();
        update_count();
    } else {
        current_clips = old_clip;
        alert("已到达该视频最后一段~如果已完成全部标注请按“上传标注信息”按钮！");
    }
}

function last_clip() {
    let old_clip = current_clips;
    current_clips--;
    
    // skip clips that need no check
    while (current_clips >= 0) {
        if (clip_statu[current_clips] == STATU_AUTO_DELETE) {
            current_clips--;
        } else {
            break;
        }
    }

    if (0 <= current_clips) {
        seek_to_clip();
        update_count();
    }
    else {
        current_clips = old_clip;
        alert("already first clip!");
    }
}

function back_clip() {
    for (let i = 0; i < clip_statu.length; i++) {
        if (clip_statu[i] == STATU_TOCHECK) {
            current_clips = i;
            break;
        }
    }
    command = COMMAND_SEEK + (current_clips).toString();
    document.getElementById('spkj').contentWindow.postMessage(command, '*');
    stop = true;
}

function delete_current_clip() {
    console.log("delete_current_clip");
    clip_statu[current_clips] = STATU_DELETE;
    update_according_to_score();
    next_clip();
}
function retain_current_clip_both() {
    console.log("retain_current_clip_both");
    clip_statu[current_clips] = STATU_RETAIN_BOTH;
    update_according_to_score();
    next_clip();
}
function finish() {
    let todo_flag = 0;
    for (let i = 0; i < clip_statu.length; i++) {
        if (clip_statu[i] == STATU_TOCHECK) {
            todo_flag = 1;
            break;
        }
    }
    if (todo_flag == 1) {
        alert("仍有未标注的段！请完成标注后再上传！");
        back_clip();
        return;
    }
    content = bvid;
    for (let j = 0; j < clip_count; j++) {
        if (clip_statu[j] == STATU_RETAIN_BOTH) {
            content = content + " " + j.toString();
        }
    }
    $.ajax({
        url: '/annotate/video/meta',
        type: 'POST',
        async: false,
        data: JSON.stringify({
            'username': username,
            'bvid': bvid,
            'annotation': content,
        }),
        success: function (ret) {
            // console.log(ret);
            alert("已成功上传" + bvid + "的标注信息!");
            window.location.href = '/annotate';
        }
    })

}
// update display functions
function update_count() {
    document.getElementById("count").innerHTML = "Current clip index: " + (current_clips + 1).toString() + " / " + clip_count.toString();
}
function get_current_playing_clip_seq(current_time) {
    // let current_idx = Math.floor(current_time * 1.0 / segment_length);
    return current_clips;
}
function get_current_zoom_boundary(current_time) {
    let mid_idx = get_current_playing_clip_seq(current_time);
    let left_idx = mid_idx - zoom_length;
    let right_idx = mid_idx + zoom_length;
    if (left_idx < 0) {
        right_idx = right_idx - left_idx;
        left_idx = 0;
    }
    let max_clip = clip_count - 1;
    if (max_clip <= right_idx) {
        left_idx -= right_idx - max_clip;
        right_idx = max_clip;
    }
    return [left_idx, right_idx];
}
function update_canvas(current_time) {
    let totalDuration = clip_count * segment_length;
    current_time = current_time < totalDuration ? current_time : totalDuration;
    // update zoomCnavas
    let zoom = document.getElementById('zoomCanvas');
    let zxt = zoom.getContext('2d');
    zxt.clearRect(0, 0, zoom.width, zoom.height);
    let boundaries = get_current_zoom_boundary(current_time);
    for (let i = boundaries[0]; i <= boundaries[1]; i++) {
        left = (i - boundaries[0]) / (2 * zoom_length + 1) * zoom.width;
        length = 1 / (2 * zoom_length + 1) * zoom.width;
        if (clip_statu[i] == STATU_TOCHECK) {
            zxt.fillStyle = TODO_COLOR;
            if (current_clips == i) zxt.fillStyle = HIGHLIGHT_COLOR;
        } else if (clip_statu[i] == STATU_RETAIN_VIDEO || clip_statu[i] == STATU_RETAIN_AUDIO || clip_statu[i] == STATU_RETAIN_BOTH) {
            zxt.fillStyle = SAVE_COLOR;
        } else if (clip_statu[i] == STATU_DELETE) {
            zxt.fillStyle = DELETE_COLOR;
        } else if (clip_statu[i] == STATU_AUTO_DELETE) {
            zxt.fillStyle = AUTO_DELETE_COLOR;
        }
        zxt.fillRect(left, canvas_border, length, zoom.height - 2 * canvas_border);
    }
    let current_idx = get_current_playing_clip_seq();

    let zoom_total_seconds = (2 * zoom_length + 1) * segment_length;
    current_percentage = (current_time - boundaries[0] * segment_length) / zoom_total_seconds;
    let current_pix = Math.round(current_percentage * zoom.width);
    zxt.strokeStyle = CURRENT_COLOR;
    zxt.lineWidth = 3;
    zxt.strokeRect(current_pix, 0, 2, zoom.height);

    current_pix = Math.round((current_clips - boundaries[0]) / (2 * zoom_length + 1) * zoom.width);
    // console.log(current_pix)
    zxt.strokeStyle = CURRENT_COLOR;
    zxt.lineWidth = 3;
    zxt.strokeRect(current_pix, canvas_border, zoom.width / (2 * zoom_length + 1), zoom.height - 2 * canvas_border);

    // update wholeCnavas
    let canvas = document.getElementById('myCanvas');
    let cxt = canvas.getContext('2d');
    cxt.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = 0; i < clip_count; i++) {
        left = i / clip_count * canvas.width;
        length = 1 / clip_count * canvas.width;
        if (clip_statu[i] == STATU_TOCHECK) {
            if (current_clips == i) cxt.fillStyle = HIGHLIGHT_COLOR;
            else cxt.fillStyle = TODO_COLOR;
        } else if (clip_statu[i] == STATU_RETAIN_VIDEO || clip_statu[i] == STATU_RETAIN_AUDIO || clip_statu[i] == STATU_RETAIN_BOTH) {
            cxt.fillStyle = SAVE_COLOR;
        } else if (clip_statu[i] == STATU_DELETE) {
            cxt.fillStyle = DELETE_COLOR;
        } else if (clip_statu[i] == STATU_AUTO_DELETE) {
            cxt.fillStyle = AUTO_DELETE_COLOR;
        }
        cxt.fillRect(left, canvas_border, length, canvas.height - 2 * canvas_border);
    }
    let zoom_left = boundaries[0] / clip_count * canvas.width;
    let zoom_canvas_length = (2 * zoom_length + 1) / clip_count * canvas.width;
    cxt.strokeStyle = CURRENT_COLOR;
    cxt.lineWidth = 3;
    cxt.strokeRect(zoom_left, canvas_border, zoom_canvas_length, canvas.height - 2 * canvas_border);
    // draw whole canvas progress
    let current_canvas_percentage = current_time / totalDuration;
    current_pix = Math.round(current_canvas_percentage * canvas.width);
    cxt.strokeStyle = CURRENT_COLOR;
    cxt.lineWidth = 3;
    cxt.strokeRect(current_pix, 0, 2, canvas.height);
}