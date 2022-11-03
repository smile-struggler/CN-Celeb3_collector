function resend() {
    $.ajax({
        url: `/resend_do`,
        type: 'POST',
    })
}
function clear_processres() {
    $.ajax({
        url: `/clear_processres`,
        type: 'POST',
    })
}