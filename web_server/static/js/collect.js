var currentTime;
var userinfo;
var duration;
var second_set = new Set();
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
let genre_list_desc = [
    "广告",
    "舞台剧、歌剧、戏剧",
    "综艺、自制游戏",
    "多人采访",
    "直播",
    "电影、纪录片",
    "电视剧、自制剧",
    "朗诵",
    "唱歌",
    "演讲、讲课",
    "记录生活短片",
]
const COMMAND_ENROLLNEXT = 'ENROLLNEXT|';
const COMMAND_DURATION = 'DURATION'
let collected_data = [];
function init_html() {
    let div = document.getElementById('genre_checkbox');
    div.setAttribute('style', 'display:flex;flex-direction:column;width:50%;height:100%;')
    let desc_div = document.getElementById('genre_desc');
    desc_div.setAttribute('style', 'display:flex;flex-direction:column;width:50%;justify-content:space-around;')
    for (let i = 0; i < genre_list.length; i++) {
        let p = document.createElement('div');
        p.setAttribute('style', 'flex: 0 0 auto;display:flex;flex-direction:row');
        let choose = document.createElement('input');
        choose.setAttribute('type', 'checkbox');
        choose.setAttribute('id', 'genre_' + i.toString());
        choose.setAttribute('style', "vertical-align:middle;zoom:150%");
        choose.setAttribute('name', "genre");
        choose.setAttribute('value', genre_list[i]);
        let choose_text = document.createElement('a');
        choose_text.setAttribute('style', 'flex:0 0 1;text-align:right');
        choose_text.text = genre_list[i];
        let desc = document.createElement('a');
        desc.setAttribute('style', 'flex:0 0 1;text-align:left');
        desc.text = genre_list_desc[i];
        p.append(choose);
        p.append(choose_text);
        div.appendChild(p);
        desc_div.append(desc);
    }
    
    get_user_info();
    current_url = window.location.href.toString()
    if(current_url.indexOf("?")==-1){
        console.log("collect")
    }
    else{
        document.getElementById('bvid').value = bv
        load_video()
        load_data()
    }
}

function load_data(){
    var second_temp_set;
    bv = document.getElementById('bvid').value.trim();
    $.ajax({
        async: false,//同步
        url: `/annotate/video/get_collectres_by_bvid?bvid=${bv}`,
        success: function (ret) {
            res = JSON.parse(ret)
            if (res['status'] === 'success') {
                var content = res['res'].toString().split(' ');
                second_temp_set = content[3].split(",")
                document.getElementById('bvid').value = bv
                document.getElementById("speaker").value = content[1]
                genre_temp_list = content[2].split(",")

                for(var i = 0 ;i < genre_temp_list.length; i++){
                    for(var j = 0;j < genre_list.length; j++){
                        if(genre_temp_list[i] == genre_list[j]){
                            document.getElementById('genre_' + j.toString()).checked = true;
                            break;
                        }
                    }
                }
            }
        }
    }
    )

    FilePond.find(inputElement).addFile(`/static/media/image/${bv}.png?`+new Date().getTime())
    

    $.ajax({
        async: false,//同步
        url: `/annotate/video/get_duration_by_bvid?bvid=${bv}`,
        success: function (ret) {
            res = JSON.parse(ret)
            duration = parseInt(res['res'][0])
        }
    }
    )

    console.log(second_temp_set)
    for(var pp = 0;pp < second_temp_set.length; pp++){
        //创建各个结点
        //得到表对象
        var tb = document.getElementById("tab1");
        //创建行对象
        var tt = document.createElement("tr");
        //创建列对象
        var td1 = document.createElement("td");

        var td2 = document.createElement("td");
        //创建a对象
        var pa = document.createElement("a");

        var pb = document.createElement("a");

        //设置td的操作a超链接
        pa.setAttribute("onclick", "del(this)");
        pa.setAttribute("href", "javascript:void(0)");//"javascript:void(0)"设置当前超链接不跳转，因为跳转了就还是跳转到了当前界面，
        //那就会刷新当前页面所以会没有效果，就像你写的代码没有反应一样
        pa.innerHTML = "删除";

        pb.setAttribute("onclick", "goto_time(" + second_temp_set[pp].toString() + ")");
        pb.setAttribute("href", "javascript:void(0)");
        pb.innerHTML = second_temp_set[pp];

        //把获取到的值付给td元素
        // td1.innerHTML = tempTime;
        //将各个td加入到tr中
        td1.appendChild(pb);
        tt.appendChild(td1);
        //超链接放入td4
        td2.appendChild(pa);
        tt.appendChild(td2);

        //tr加入到table
        tb.appendChild(tt);

        second_set.add(second_temp_set[pp].toString())
        document.getElementById('status').innerHTML = "状态：成功添加！";
        document.getElementById('chooseNum').innerText = "已选" + second_set.size.toString() + "/10秒！";
    }
}

function get_user_info() {
    data = { "username": username };
    $.ajax({
        async: false,
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
            document.getElementById("userinfo_collect").textContent = `您已经采集了${userinfo['video_count']}条视频，原始数据总时长为${userinfo['total_dur']}`;
        }
    })
}
document.getElementById('bvid').onchange = function () {
    let bv = document.getElementById('bvid').value.trim();
    bv_begin_idx = bv.search('bilibili.com/video/BV')
    if (bv_begin_idx == -1) {
        console.log('not full url, maybe bvid alone')
    } else {
        bv = bv.slice(bv_begin_idx + 19, bv_begin_idx + 19 + 12)
    }
    
    $.ajax({
        async: false,
        url: '/collect_video/check_bvid?bvid=' + bv + '&username=' + username,
        type: 'GET',
        success: function (ret) {
            console.log(ret);
            if (ret == 'allow') {
                alert('您已收集过此视频 ' + bv + ' ，您可通过再次提交来覆盖之前的记录')
                load_video()
                load_data()
            } else if (ret == 'forbid') {
                alert('其他用户已收集过此视频 ' + bv + ' ，您无法进行提交，请修改')
                document.getElementById('speaker').value = "";
                document.getElementById('bvid').value = "";
                document.getElementById("userinfo_collect").textContent = "";
            }
        }
    })
}
function update_speaker_information() {
    let spk = document.getElementById('speaker').value.trim();
    console.log(spk)
    res = check_spkname();
    console.log(res)
    if (res == 0) {
        document.getElementById('speaker').value = "";
        document.getElementById('bvid').value = "";
        document.getElementById("userinfo_collect").textContent = "";
        return;
    }
    if (spk == null) {
        document.getElementById("userinfo_collect").textContent = "";
        return;
    }
    $.ajax({
        async: false,
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
            if (!(spk in userinfo['spk_collect'])) {
                if (spk === "" || spk == null) {
                    document.getElementById("userinfo_collect").textContent = "";
                } else {
                    document.getElementById("userinfo_collect").innerHTML = `您已经采集了 <a style="color:red">${spk} </a>共<a style="color:red">
                        0 </a>条视频，原始数据总时长为 <a style="color:red">0:00:00</a> `;
                }
            } else {
                timeSplit = userinfo['spk_collect'][spk]['total_dur'].split(":")
                temp = parseInt(timeSplit[0]) * 3600 + parseInt(timeSplit[1]) * 60 + parseInt(timeSplit[2])
                if (temp < 4 * 3600 || parseInt(userinfo['spk_collect'][spk]['video_count']) < 10) {
                    document.getElementById("userinfo_collect").innerHTML = `您已经采集了 <a style="color:red">${spk} </a>共<a style="color:red">
                        ${userinfo['spk_collect'][spk]['video_count']} </a>条视频，原始数据总时长为 <a style="color:red">${userinfo['spk_collect'][spk]['total_dur']}</a>`;
                }
                else {
                    document.getElementById("userinfo_collect").innerHTML = `您已经采集了 <a style="color:green">${spk} </a>共<a style="color:green">
                        ${userinfo['spk_collect'][spk]['video_count']} </a>条视频，原始数据总时长为 <a style="color:green">${userinfo['spk_collect'][spk]['total_dur']}</a>`;
                }

            }

        }
    })
}
document.getElementById('speaker').onchange = function () {
    update_speaker_information();
}
function check_spkname() {
    let spk = document.getElementById('speaker').value.trim();
    var check_spkname_res = 1;
    $.ajax({
        url: '/collect_video/check_spk?spk=' + spk + '&username=' + username,
        type: 'GET',
        async: false,
        success: function (ret) {
            console.log(ret);
            if (ret == 'allow') {
                console.log('允许收集');
            } else if (ret == 'forbid') {
                alert('其他用户已收集过 ' + spk + ' 的视频，您将无法进行提交，请修改');
                check_spkname_res = 0;
            }
        }
    })
    return check_spkname_res;
}
function collect_information() {
    let speaker = document.getElementById('speaker').value.trim();
    let bv = document.getElementById('bvid').value.trim();
    bv_begin_idx = bv.search('bilibili.com/video/BV')
    if (bv_begin_idx == -1) {
        console.log('not full url, maybe bvid alone')
    } else {
        bv = bv.slice(bv_begin_idx + 19, bv_begin_idx + 19 + 12)
    }
    let genre = [];
    for (let i = 0; i < genre_list.length; i++) {
        if (document.getElementById('genre_' + i.toString()).checked) {
            genre.push(document.getElementById('genre_' + i.toString()).value);
        }
    }
    if (bv.length != 12 || genre.length < 1 || speaker.length < 1) {
        console.log('invalid bv number or no genre checked')
        return { bv: bv, genre: genre, speaker: speaker, status: -1 };
    } else {
        return { bv: bv, genre: genre, speaker: speaker, status: 0 };
    }
}
function load_video() {
    let data = collect_information();
    console.log(data);
    if (data['bv'].length != 12) {
        alert('BVid或URL不正确');
    }
    else {
        if (document.getElementById('spkj').src == "" || document.getElementById('spkj').src == null) {
            second_List = new Set();
        } else if (document.getElementById('spkj').src.match("bvid=(.*?)&page=1") == null) {
            second_List = new Set();
        } else if (data['bv'] != document.getElementById('spkj').src.match("bvid=(.*?)&page=1")[1]) {
            second_List = new Set();
        }
        document.getElementById('spkj').src = "https://player.bilibili.com/player.html?bvid=" + data['bv'] + "&page=1&danmaku=0"
        document.getElementById("mention").innerHTML = "友情提示：注意检查<b>speaker name</b>是否需要修改~";
    }
}
function choose() {
    let data = collect_information();
    var iframeUrl = document.getElementById('spkj').src.match("bvid=(.*?)&page=1")[1];
    if (data['status'] == -1) {
        alert('BVid或URL不正确，或者没有选择任何场景，或者没有输入说话人姓名');
    }
    else if (iframeUrl != data['bv']) {
        alert('播放器中视频与所填不一致，请确定是否Load video!');
    }
    else if (second_set.size == 10) {
        alert('已选10秒，请在按下Add按钮后采集下一段视频');
    }
    else if (parseInt(FilePond.find(inputElement).getFiles().length) == 0) {
        alert('请先上传注册人脸~');
    }
    else {
        var tempTimeNum = currentTime - 1;
        var tempTime = tempTimeNum.toFixed(5)
        console.log(tempTime)
        if (tempTime < 0) {
            document.getElementById('status').innerText = "状态：还未到一秒！";
            return;
        }
        document.getElementById('spkj').contentWindow.postMessage(COMMAND_DURATION, '*');
        for (let second of second_set) {
            // console.log("!!")
            // console.log(Math.abs(tempTimeNum - second))
            if (Math.abs(tempTimeNum - second) < 1) {
                document.getElementById('status').innerText = "状态：选择的两个时间不能重叠！";
                return;
            }
        }
        //创建各个结点
        //得到表对象
        var tb = document.getElementById("tab1");
        //创建行对象
        var tt = document.createElement("tr");
        //创建列对象
        var td1 = document.createElement("td");

        var td2 = document.createElement("td");
        //创建a对象
        var pa = document.createElement("a");

        var pb = document.createElement("a");

        //设置td的操作a超链接
        pa.setAttribute("onclick", "del(this)");
        pa.setAttribute("href", "javascript:void(0)");//"javascript:void(0)"设置当前超链接不跳转，因为跳转了就还是跳转到了当前界面，
        //那就会刷新当前页面所以会没有效果，就像你写的代码没有反应一样
        pa.innerHTML = "删除";

        pb.setAttribute("onclick", "goto_time(" + tempTime.toString() + ")");
        pb.setAttribute("href", "javascript:void(0)");
        pb.innerHTML = tempTime;

        //把获取到的值付给td元素
        // td1.innerHTML = tempTime;
        //将各个td加入到tr中
        td1.appendChild(pb);
        tt.appendChild(td1);
        //超链接放入td4
        td2.appendChild(pa);
        tt.appendChild(td2);

        //tr加入到table
        tb.appendChild(tt);

        second_set.add(tempTime.toString())
        document.getElementById('status').innerHTML = "状态：成功添加！";
        document.getElementById('chooseNum').innerText = "已选" + second_set.size.toString() + "/10秒！";


    }
}
function del(obj) {

    // var judge = confirm("确认删除吗?")
    // if (judge = true) {
    tdNode = obj.parentNode;//得到td
    trNOde = tdNode.parentNode;//得到tr
    tbNOde = trNOde.parentNode;//得到table
    second_set.delete(trNOde.firstElementChild.innerText)
    document.getElementById('status').innerHTML = "状态：成功删除！";
    document.getElementById('chooseNum').innerText = "已选" + second_set.size.toString() + "/10秒！";
    tbNOde.removeChild(trNOde);
    // }


    // second_set.delete(tempTime)
    // document.getElementById('status').innerText = "状态：成功删除！";
    // document.getElementById('chooseNum').innerText = "已选" + second_set.size() + "/10秒！";

}

function goto_time(target_time) {
    command = COMMAND_ENROLLNEXT + target_time.toString();
    document.getElementById('spkj').contentWindow.postMessage(command, '*');
}

function add_video() {
    let data = collect_information();
    if (data['status'] == -1) {
        alert('BVid或URL不正确，或者没有选择任何场景，或者没有输入说话人姓名');
    }
    else if (second_set.size != 10) {
        alert('还未选到10秒!');
    }
    else if (parseInt(FilePond.find(inputElement).getFiles().length) == 0) {
        alert('注册人脸仍未上传！');
    }
    else if (duration > 30 * 60) {
        alert('视频长度不能超过30分钟！');
    }
    else {
        pushback_data(data);
        data['username'] = username;
        data['txt'] = dict_to_string(data);
        data['dur'] = duration;
        console.log(data)
        allow_upload = false
        $.ajax({
            url: 'collect_video/check_image_upload' + '?bvid=' + data['bv'],
            type: 'GET',
            async: false,
            success: function (ret) {
                allow_upload = ret === 'success'
            }
        })
        if (!allow_upload) {
            alert('未检测到人脸图片，请确保人脸的图片已经上传！');
        }
        else {
            // upload to server
            lines = JSON.stringify(data);
            $.ajax({
                url: '/collect_video/meta',
                type: 'POST',
                data: lines,
                async: false,
                success: function (ret) {
                    console.log(ret);
                    // get_user_info();
                    update_speaker_information();
                    FilePond.destroy(inputElement);
                    FilePond.create(inputElement, {
                        labelIdle: `Drag & Drop your picture or Copy, Click & Paste`,
                    });
                    document.getElementById('bvid').value = "";
                    document.getElementById("mention").innerText = "";
                    // document.getElementById('speaker').value = "";
                    for (let i = 0; i < genre_list.length; i++) {
                        document.getElementById('genre_' + i.toString()).checked = false;
                    }

                    var mytable = document.getElementById('tab1');
                    for (var i = 1, rows = mytable.rows.length; i < rows; i++) {
                        mytable.removeChild(mytable.rows[1])
                    }
                    second_set = new Set();
                    document.getElementById('status').innerHTML = "状态：";
                    document.getElementById('chooseNum').innerText = "已选" + second_set.size.toString() + "/10秒！";
                    document.getElementById('spkj').src = "";

                    alert(data['bv'] + "添加完成！")
                }
            })
        }
        current_url = window.location.href.toString()
        if(current_url.indexOf("?")!=-1){
            window.location.href = '/annotate';
        }
    }
}
function pushback_data(data) {
    let insert = true;
    data['second'] = [];
    var mytable = document.getElementById('tab1');
    for (var i = 1, rows = mytable.rows.length; i < rows; i++) {
        var temp = mytable.rows[i].cells[0].innerHTML.toString().match(">(.*?)</a>")[1]
        data['second'].push(temp);
    }

    for (let i = 0; i < collected_data.length; i++) {
        if (collected_data[i]['bv'] == data['bv']) {
            collected_data[i] = data;
            insert = false;
            break;
        }
    }
    if (insert) {
        collected_data.push(data);
    }
}
window.addEventListener('message', e => {
    var eFirst = e.data.toString().charAt(0)
    if (eFirst == 'D') {
        command = e.data.split('|');
        duration = parseInt(command[1])
        console.log(duration)
    }
    else {
        currentTime = e.data
    }


})
function dict_to_string(dict) {
    let str = dict['bv'] + ' ' + dict['speaker'] + ' ' + dict['genre'] + " " + dict['second'];
    return str;
}

var inputElement = document.querySelector('input[type="file"]');
FilePond.registerPlugin(
    FilePondPluginFileValidateType,
    FilePondPluginFileEncode,
    FilePondPluginFileRename,
    FilePondPluginImagePreview,
);
FilePond.setOptions({
    server: {
        url: '/collect_video/image',
    },
    acceptedFileTypes: ['image/png'],
    allowBrowse: false,
    fileRenameFunction: (file) => {
        var bv = document.getElementById('bvid').value.trim();
        bv_begin_idx = bv.search('bilibili.com/video/BV')
        if (bv_begin_idx == -1) {
            console.log('not full url, maybe bvid alone')
        } else {
            bv = bv.slice(bv_begin_idx + 19, bv_begin_idx + 19 + 12)
        }
        spk = document.getElementById('speaker').value.trim();
        return `${bv}${file.extension}`;
    },
});
FilePond.create(inputElement, {
    labelIdle: `Drag & Drop your picture or Copy, Click & Paste`,
});
// let seq = 0;
// setInterval(function () {
//     data = {
//         "username": username,
//         "bv": "BV1ZB4y147ao",
//         "genre": ["Singing", "Vlog"],
//         "speaker": "泥芳草", "status": 0,
//         "second": ["3.12913", "4.55156", "5.57923", "6.59064", "8.36014", "9.64944", "11.18955", "12.46964", "13.56006", "15.31964"],
//         "txt": "BV1ZB4y147ao 泥芳草 Singing,Vlog 3.12913,4.55156,5.57923,6.59064,8.36014,9.64944,11.18955,12.46964,13.56006,15.31964",
//         "dur": seq,
//     }
//     lines = JSON.stringify(data);
//     $.ajax({
//         url: '/collect_video/meta',
//         type: 'POST',
//         data: lines,
//         success: function (ret) {
//             console.log(ret);
//         }
//     })
//     seq++;
// }, 5000)
