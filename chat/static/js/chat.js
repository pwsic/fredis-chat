var prefix = $(location).attr("origin").replace(/^http/, "ws").concat("/websocket")
var query_strings = $(location).attr("href").replace($(location).attr("origin"), "").split("/")
var url = prefix.concat("/").concat(query_strings[1]).concat("/").concat(query_strings[2])
var ws = new WebSocket(url)

$(document).ready(function() {

    $("#message-form").submit(function(e) {
        postData($(this));
        e.preventDefault();
    })

    var message_input = $('#message-form').find("input[type=text]")
    message_input.focus()
    message_input.attr("disabled")

    ws.on_open = function () {
        message_input.removeAttr("disabled")
    }

    ws.onmessage = function(e) {
        data = JSON.parse(e.data)
        console.log(data)
        $("#messages-list").append(data.from.concat(": ").concat(data.text) + "</br>")
    }

    ws.onclose = function() {
        message_input.attr("disabled");
    }
})

function postData(form) {
    data = {
        'from': form.find("input[type=hidden]").val(),
        'text': form.find("input[type=text]").val()
    }
    ws.send(JSON.stringify(data));
}




