/*
 * JavaScript for managing labs (creation, deletion, etc.).
 */

function create_lab(generation_url) {
    let el = document.getElementsByName("csrfmiddlewaretoken");
    let csrf_token = el[0].getAttribute("value");
    let data = {csrfmiddlewaretoken: csrf_token}
    
    $.ajax({
        type: "POST",
        url: generation_url,
        data: data,
        complete: function(response) {
            let results = response.responseJSON;
            if ( results.created ) {
                create_notification("Success! Lab created.", "success");
            }
            else {
                create_notification("Failed to start lab.", "fail");
            }
        }
    });
}

function delete_lab(deletion_url) {
    let el = document.getElementsByName("csrfmiddlewaretoken");
    let csrf_token = el[0].getAttribute("value");
    let data = {csrfmiddlewaretoken: csrf_token}
    
    $.ajax({
        type: "POST",
        url: deletion_url,
        data: data,
        complete: function(response) {
            let results = response.responseJSON;
            if ( results.created ) {
                create_notification("Deleted lab.", "success");
            }
            else {
                create_notification("Failed to delete lab.", "fail");
            }
        }
    });
}

/*********************************************
 * Pop-up notifications
 *********************************************/

// Maximum number of pop-up notifications we'll allow to be displayed
// at any given time
const MAX_NOTIFICATIONS = 6;

function get_notification_colors(type) {
    /* Get background / font colors for a given notification type.
     * Supported values of 'type' are
     * - info
     * - success
     * - warn
     * - fail
     * - normal
     *
     * Returns an array with two values:
     * - A CSS class for the background color
     * - A style specification for 'color'
     */
    switch (type) {
        case "info":
            return ["bg-info", "white"];
        case "success":
            return ["bg-success", "white"];
        case "warn":
            return ["bg-warning", "black"];
        case "fail":
            return ["bg-danger", "white"];
        default:
            console.log("Unknown notification type '" + type + "'.");
            console.log("Defaulting to type 'normal'.")
        case "normal":
            return ["bg-light", "black"];
    }
}

function delete_notification(node, interval) {
    // Delete a notification node over a given interval
    // We fade out the notification at a rate of 50 steps / second
    let fade_out_steps = Math.ceil(interval / 1000 * 50);

    if ( !node.style.opacity ) {
        node.style.opacity = 1;
    }
    let opacity_step = node.style.opacity / fade_out_steps;
    let time_step = interval / fade_out_steps;

    let handler = setInterval(function () {
        node.style.opacity -= opacity_step;
    }, time_step);

    // At the end of the interval, remove the node entirely. We add
    // a few extra time steps just to ensure that we get enough time
    // to completely remove the notification.
    setTimeout(function () {
        node.remove();
        clearInterval(handler);
    }, interval + 5 * time_step);
}

function clean_notifications() {
    // Remove notifications once we get past the maximum number of
    // allowed notifications.
    let notification_list = document.querySelector("#notification-list");

    for ( let ii = MAX_NOTIFICATIONS; ii < notification_list.children.length; ++ii ) {
        let child = notification_list.children[ii];
        delete_notification(child, 300);
    }
}

function create_notification(msg) {
    return create_notification(msg, "normal");
}

function create_notification(msg, type) {
    // Use HTML from the notification template
    let template = document.querySelector("#notification-template");
    let clone = document.importNode(template.content, true);

    // Set the clone's header, time, and body
    let header = clone.querySelector(".notification-header");
    let time   = clone.querySelector(".notification-time");
    let body   = clone.querySelector(".notification-body");

    header.innerText = "Lawliet";
    time.innerText = (new Date()).toLocaleTimeString();
    body.innerText = msg;

    // Set color of notification background and text
    let notification_colors = get_notification_colors(type);
    let bg_type = notification_colors[0];
    let font_color = notification_colors[1];
    clone.firstElementChild.classList.add(bg_type);
    body.style.color = font_color;

    let notification_list = document.querySelector("#notification-list");
    notification_list.prepend(clone);

    // Delete the notification after one minute
    let child = notification_list.firstElementChild;
    setTimeout(function () {
        delete_notification(child, 300);
    }, 1000 * 60);

    $(".toast").toast("show");
    clean_notifications();
}

$(document).on("click", ".notification-close-button", function () {
    /* When the close button is clicked on a notification, make the notification
     * fade out and then remove it. */
    $(this).closest(".notification").fadeOut(500, function () {
        $(this).remove();
    });
});
