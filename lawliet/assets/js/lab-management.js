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

function fadeOut(node, interval) {
    setTimeout(function () {
        node.style.WebKitTransition = "opacity 1s ease-in-out";
        node.style.opacity = "0";
    }, interval);
}

function clean_notifications() {
    // Remove notifications once we get past the maximum number of
    // allowed notifications.
    const FADE_OUT_INTERVAL = 500; // ms
    const FADE_OUT_STEPS = 25;
    let notification_list = document.querySelector("#notification-list");

    for ( let ii = MAX_NOTIFICATIONS; ii < notification_list.children.length; ++ii ) {
        let child = notification_list.children[ii];
        if ( child.style.opacity ) {
            child.style.opacity = 1;
        }
        let opacity_step = child.style.opacity / FADE_OUT_STEPS;

        // Fade out over 500ms
        setInterval(function () {
            child.style.opacity -= opacity_step;
        }, FADE_OUT_INTERVAL / 50);

        // Remove completely after 500ms
        setTimeout(function () {
            child.remove();
        }, FADE_OUT_INTERVAL);
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
