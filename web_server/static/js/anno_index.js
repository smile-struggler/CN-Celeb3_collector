var video_list;
var userinfo;

window.onload = function () {
    get_video_info();
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
            userinfo = JSON.parse(ret);
            document.getElementById("userinfo_todo").textContent = `您还需要标注${userinfo['todo_count']}条视频，原始数据总时长为${userinfo['todo_dur']}`;
            document.getElementById("userinfo_annotated").textContent = `您已经标注了${userinfo['annotated']}条视频，有效数据总时长为${userinfo['annotated_dur']}`;
        }
    })
}

function createTableRow(tableID, meta) {
    var tb = document.getElementById(tableID);
    var tr = document.createElement("tr");
    var td1 = document.createElement("td");
    var td2 = document.createElement("td");
    var td3 = document.createElement("td");
    var td4 = document.createElement("td");
    var td5 = document.createElement("td");
    var td6 = document.createElement("td");
    var pa = document.createElement("a");
    var pb = document.createElement("a");
    var pc = document.createElement("a");
    var pd = document.createElement("button");
    var pe = document.createElement("button");
    var pf = document.createElement("button");

    pa.innerHTML = meta['bvid'];
    pb.innerHTML = meta['spkname'];
    pc.innerHTML = meta['status'];
    bvid = meta['bvid'];

    if (meta['status'] === '暂时无法标注') {
        pd.setAttribute("onclick", "window.location.href='/annotate'");
        pd.setAttribute("style", "width:30px;height:30px;background-color:red");
        pc.setAttribute("style", "color:orange")
    } else {
        pd.setAttribute("onclick", `window.location.href='/annotate_video?bvid=${bvid}&username=${username}'`);
        pd.setAttribute("style", "width:30px;height:30px;background-color:green");
        if (meta['status'] === '需要标注') {
            pc.setAttribute("style", "color:red")
        } else {
            pc.setAttribute("style", "color:green")
        }
    }

    // 修改
    pe.setAttribute("style", "width:30px;height:30px;background-color:#21abcd");
    pe.setAttribute("onclick", `window.location.href='/collect_modify?bv=${bvid}&username=${username}'`);


    //删除
    pf.setAttribute("style", "width:30px;height:30px;background-color:red");
    pf.setAttribute("onclick", "del(this)");

    td1.appendChild(pa);
    td2.appendChild(pb);
    td3.appendChild(pc);
    td4.appendChild(pd);
    td5.appendChild(pe);
    td6.appendChild(pf);

    tr.appendChild(td1);
    tr.appendChild(td2);
    tr.appendChild(td3);
    tr.appendChild(td4);
    tr.appendChild(td5);
    tr.appendChild(td6);
    tb.appendChild(tr);
}

function del(obj){
    tdNode = obj.parentNode;//得到td
    trNOde = tdNode.parentNode;//得到tr
    tbNOde = trNOde.parentNode;//得到table
    bvid = trNOde.firstElementChild.innerText
    spkname = trNOde.children[1].innerText
    var msg = "你确定要删除 " + spkname + " 的 " + bvid + " 吗？"
    if(confirm(msg) == true){
        $.ajax({
            url: '/delete/video/bv',
            type: 'POST',
            async: false,
            data: JSON.stringify({
                'username': username,
                'bvid': bvid,
            }),
            success: function (ret) {
                // console.log(ret);
                alert("已成功删除" + bvid + "!");
                window.location.href = '/annotate';
            }
        })
    }
}

function annotate_video(bv) {
    data = { "username": username, "bv": bv };
    $.ajax({
        url: '/annotate_video',
        type: 'GET',
        data: data
    })
}


function get_video_info() {
    data = { "username": username };
    $.ajax({
        url: '/annotate/get_video_list',
        type: 'GET',
        data: data,
        success: function (ret) {
            if (ret == "error") {
                alert("用户未找到，请退出登录");
                username = null;
                return;
            }
            video_list = JSON.parse(ret);
            for (let meta in video_list) {
                createTableRow("anntate_list", video_list[meta]);
            }
        }
    })
}