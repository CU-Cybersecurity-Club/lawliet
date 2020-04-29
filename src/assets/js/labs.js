/*
 * Front-end code for starting, deleting, and otherwise managing lab environments
 */

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

/*
 * Function definitions
 */

function generate_lab(lab_id) {
  /* Start a new lab with the given environment ID. */
  console.log("Generating lab with id " + lab_id);

  const url = "/labs/generate?create=" + lab_id;
  axios.post(url)
    .then(function (response) {
      // Success
    })
    .catch(function (error) {
      // Error
      console.log(error);
    });
}

function delete_lab(conn_name) {
  /* Delete the running lab */
  console.log("Deleting lab");

  const url = "/labs/delete?id=" + encodeURIComponent(conn_name);
  axios.post(url)
    .then(function (response) {
      console.log("Successfully deleted lab");
      console.log(response);
    })
    .catch(function (error) {
      console.log("Error deleting lab");
      console.log(error);
    });
  window.location.reload();
}

function create_notification(message) {
  create_notification(message, {});
}

function create_notification(message, opts) {
  console.log("Creating notification with message '" + message + "'");
  return UIkit.notification(
    // "<lab-notification message='" + message + "'></lab-notification>",
    message,
    opts
  );
}

/*
 * Vue components
 */

const _notification_template = `
<div class="uk-alert-success" uk-alert>
  [[ message ]]
</div>
`;

Vue.component("lab-notification", {
  props: ["message"],
  template: _notification_template
});

/*
 * Vue apps
 */

new Vue({
  el: "#body",
});

new Vue({
  el: "#labenvs"
});

new Vue({
  el: "#delete-button"
});
