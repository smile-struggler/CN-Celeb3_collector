var userinfo;
var userinfostr;
window.onload = function () {
    get_user_info();
}

function get_user_info() {
    data = { "username": username };
    $.ajax({
        url: '/userinfo',
        type: 'GET',
        data: data,
        success: function (ret) {
            if (ret == "error") {
                alert("用户未找到，请退出登录");
                username = null;
                return;
            }
            console.log(ret);
            userinfostr = ret;
            userinfo = JSON.parse(ret);
            var collected_num = 0;
            for (var key in userinfo['spk_collect']) {
                timeSplit = userinfo['spk_collect'][key]['total_dur'].split(":")
                temp = parseInt(timeSplit[0]) * 3600 + parseInt(timeSplit[1]) * 60 + parseInt(timeSplit[2])
                if (temp >= 4 * 3600) {
                    collected_num += 1;
                }
            }

            document.getElementById("userinfo_collect").innerHTML = `您已经采集了<b>${userinfo['video_count']}</b>条视频，原始数据总时长为<b>${userinfo['total_dur']}</b>，已采集完<b>${collected_num}</b>人`;
            document.getElementById("userinfo_todo").innerHTML = `您还需要标注<b>${userinfo['todo_count']}</b>条视频，原始数据总时长为<b>${userinfo['todo_dur']}</b>`;
            document.getElementById("userinfo_annotated").innerHTML = `您已经标注了<b>${userinfo['annotated']}</b>条视频，有效数据总时长为<b>${userinfo['annotated_dur']}</b>`;
            for (var key in userinfo['spk_collect']) {
                createSpeakerInfoTableRow('collect_list', key, userinfo['spk_collect'][key], 'video_count', 'total_dur', 0)
            }
            for (var key in userinfo['spk_todo']) {
                createSpeakerInfoTableRow('marktodo_list', key, userinfo['spk_todo'][key], 'todo_count', 'todo_dur', 1)
            }
            for (var key in userinfo['spk_annotate']) {
                createSpeakerInfoTableRow('marked_list', key, userinfo['spk_annotate'][key], 'annotated', 'annotated_dur', 2)
            }
            for (var key in userinfo['spk_genre']) {
                createGenreInfoTableRow('genre_list', key, userinfo['spk_genre'][key])
            }
        }
    })
}

function logout() {
    data = { "username": username };
    $.ajax({
        url: '/logout',
        type: 'GET',
        data: data,
        success: function (ret) {
            username = null;
            window.location.href = '/login';
        }
    })
}

function createSpeakerInfoTableRow(table_ID, name, meta, meta1, meta2, type) {
    var tb = document.getElementById(table_ID);
    var tr = document.createElement("tr");

    var td1 = document.createElement("td");
    var td2 = document.createElement("td");
    var td3 = document.createElement("td");

    var pa = document.createElement("a");
    var pb = document.createElement("a");
    var pc = document.createElement("a");

    pa.innerHTML = name;
    pb.innerHTML = meta[meta1];
    pc.innerHTML = meta[meta2];

    pb.style.fontWeight = "bolder"
    pc.style.fontWeight = "bolder"

    timeSplit = meta[meta2].split(":")
    temp = parseInt(timeSplit[0]) * 3600 + parseInt(timeSplit[1]) * 60 + parseInt(timeSplit[2])

    // 视频数量不少于10个
    // if (type == 0) {
    //     if (parseInt(meta[meta1]) < 10) {
    //         pb.style.color = "red"
    //         pc.style.color = "red"
    //     }
    //     else {
    //         pb.style.color = "green"
    //         pc.style.color = "green"
    //     }
    // }

    // 待标注统计
    // if (type == 1) {

    //     if (temp != 0) {
    //         pb.style.color = "red"
    //         pc.style.color = "red"
    //     }
    //     else {
    //         pb.style.color = "green"
    //         pc.style.color = "green"
    //     }
    // }

    // 已标注时间不少于2.5小时
    if (type == 2) {
        if (parseInt(meta[meta1]) < 10 || temp < 1.5 * 3600) {
            pb.style.color = "red"
            pc.style.color = "red"
        }
        else {
            pb.style.color = "green"
            pc.style.color = "green"
        }
    }

    td1.appendChild(pa);
    td2.appendChild(pb);
    td3.appendChild(pc);

    tr.appendChild(td1);
    tr.appendChild(td2);
    tr.appendChild(td3);
    tb.appendChild(tr);
}

let genre_list = [
    'Advertisement',
    'Drama',
    'Entertainment',
    'Interview',
    'Live_Broadcast',
    'Movie',
    'Play',
    'Recitation',
    'Singing',
    'Speech',
    'Vlog',
]

genre2id = {}
var genre_len = genre_list.length
for (var i = 0; i < genre_len; i++) {
    genre2id[genre_list[i]] = i;
}

function createGenreInfoTableRow(table_ID, name, meta) {
    genre_num = {}
    var td = []
    var p = []
    var genre_len = genre_list.length
    for (var i = 0; i < genre_len; i++) {
        genre_num[i] = 0;
        td.push(document.createElement("td"));
        p.push(document.createElement("a"))
        p[i].innerHTML = 0
        td[i].appendChild(p[i])
    }

    var tb = document.getElementById(table_ID);
    var tr = document.createElement("tr");

    var tdname = document.createElement("td");
    var pname = document.createElement("a");
    tdname.appendChild(pname)
    var tdnum = document.createElement("td");
    var pnum = document.createElement("a");
    tdnum.appendChild(pnum)

    pname.innerHTML = name;
    pnum.innerHTML = meta['genre_num'];

    pnum.style.fontWeight = "bolder";

    if (meta['genre_num'] < 3) {
        pnum.style.color = "red"
    }
    else {
        pnum.style.color = "green"
    }


    var temp_len = meta['genre_list'].length
    for (var i = 0; i < temp_len; i++) {
        var genre_id = genre2id[meta['genre_list'][i]]
        td[genre_id].style.backgroundColor = '#8fbc8f'
        p[genre_id].style.fontWeight = "bolder";
        genre_num[genre_id] += 1;
        p[genre_id].innerHTML = genre_num[genre_id];
    }

    tr.appendChild(tdname)
    for (var i = 0; i < genre_len; i++) {
        tr.appendChild(td[i]);
    }
    tr.appendChild(tdnum)
    tb.appendChild(tr);
}