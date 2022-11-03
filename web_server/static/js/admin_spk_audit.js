function get_result() {
    // data = { "username": username };
    var mytable = document.getElementById('spk_audit');
    for (var i = 1, rows = mytable.rows.length; i < rows; i++) {
        mytable.removeChild(mytable.rows[1])
    }

    $.ajax({
        url: '/admin/get_result',
        type: 'GET',
        success: function (ret) {
            console.log(ret)
            ret_json = JSON.parse(ret)
            console.log(ret_json['ans'])
            result_list = JSON.parse(ret_json['ans']);
            document.getElementById('new').innerText = "新增完成目标说话人数量：" + ret_json['new_spk_num']
            document.getElementById('total').innerText = "所有完成目标说话人数量：" + ret_json['total_spk_num']
            createTable('spk_audit', result_list);
        }
    })
}

function createTable(tableID, meta) {
    var tb = document.getElementById(tableID);
    for(var i = 0 ;i < meta['采集人'].length;i++){
        var tr = document.createElement("tr");
        var td1 = document.createElement("td");
        var td2 = document.createElement("td");
        var td3 = document.createElement("td");
        var pa = document.createElement("a");
        var pb = document.createElement("a");
        var pc = document.createElement("a");

        size_num = 18
        pa.style.fontSize = size_num+'px'
        pb.style.fontSize = size_num+'px'
        pc.style.fontSize = size_num+'px'

    
        pa.innerHTML = meta['采集人'][i];
        pb.innerHTML = meta['目标说话人'][i];
        pc.innerHTML = meta['审核率'][i];
    
        td1.appendChild(pa);
        td2.appendChild(pb);
        td3.appendChild(pc);
    
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        tb.appendChild(tr);   
    }
}