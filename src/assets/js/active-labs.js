/*
 * JavaScript for viewing the currently active lab.
 */

function check_lab_status(status_url) {
    // let el = document.getElementsByName("csrfmiddlewaretoken");
    // let csrf_token = el[0].getAttribute("value");

    $.ajax({
        type: "GET",
        url: status_url,
        complete: function(response) {
            let results = response.responseJSON;
            if ( results.labs.length == 0 ) {
                show_no_active_labs();
            }
            else {
                alert("TODO");
            }
        },
    });
}

function show_no_active_labs() {
    /* Tell the user that there are currently no lab environments
     * up and running. */
    let spinner = document.getElementById("active-lab-waiting");

    // Fade the spinner out, and replace it with the status card saying
    // that there are no active labs.
    $(spinner).fadeOut(500, function () {
        $(this).remove();
        $(document.getElementById("no-active-lab")).fadeIn(500);
    });
}

/*
 * Wait until jQuery is loaded. Once it is, start running Javascript.
 */
window.onload = function () {
    $(document).ready(function () {
        check_lab_status("/labs/lab-status");
    });
}
