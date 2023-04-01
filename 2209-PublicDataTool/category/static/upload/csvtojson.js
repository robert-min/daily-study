
// 파일 추가 버튼을 누르면 handleFileSelect 함수 호출
$(function init(){
    document.getElementById("formFileLg").addEventListener('change', handleFileSelect, false);
});

function handleFileSelect(event){
    const reader = new FileReader()
    // handleFileLoad 함수 호출
    reader.onload = handleFileLoad;
    reader.readAsText(event.target.files[0])
}

// csv 데이터를 json 형태로 변환
function csvJson(csv){
    var lines = csv.split("\n");
    var result = [];
    var headers = lines[0].split(",");
    for(var i=1; i < lines.length; i++){
        var obj = {};
        var cur_line = lines[i].split(",");
        for(var j=0; j < headers.length; j++){
            obj[headers[j]] = cur_line[j];
        }
        result.push(obj)
    }
    return JSON.stringify(result);
}

function handleFileLoad(event){

    let uploaded = event.target.result;
    // csvJson 함수 호출
    let upload_data = csvJson(uploaded)

    $.ajax({
        // 요청될 URL 주소
        url: 'ajax_method',
        type: "POST",
        dataType: "JSON",
        data: {
            'upload_data': upload_data,
            csrfmiddlewaretoken: "{{ csrf_token }}"
        },
        headers: { "X-CSRFToken": "{{ csrf_token }}"},

        success: function (data) {
            const port_data = JSON.stringify(data);
            var port_data_json = JSON.parse(port_data);
        },

        error : function (xhr, textStatus, thrownError) {
            alert("Error. Can't send URL to Django : " + xhr.status + ":" + xhr.responseText);
        }
    });
}