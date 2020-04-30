/* JavaScript for the site dashboard. */

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

/*
 * Vue components
 */

// Various buttons that allow you to manage an active lab environment
const active_lab_management_template = `
<div>
  <div
    v-bind:id="card_id"
    class="uk-card uk-card-body uk-card-default uk-margin-bottom">
    <h3 class="uk-card-title">Active lab: [[ lab_name ]]</h3>
    <p class="monospace waiting-text uk-text-center">
      Lab starting...
    </p>
    <ul class="uk-list uk-margin-top">
      <li>
        <button
          type="button"
          class="open-button uk-button uk-button-primary uk-width-1-1@m"
          v-on:click="let win = window.open('/guacamole/#/client/' + b64_conn_id, '_blank'); win.focus();"
          disabled>
          Open lab
        </button>
      </li>
      <li>
        <button
          type="button"
          class="uk-button uk-button-primary uk-width-1-1@m"
          v-on:click="delete_lab(conn_name)">
          Delete lab
        </button>
      </li>
    </ul>
  </div>
</div>`;

// Header above lab management panels
const active_lab_dashboard_header = `
<div>
  <h1 class="uk-h1 uk-text-center">
    Active labs
  </h1>
  <hr>
</div>
`;

Vue.component("lab-component", {
  delimiters: ["[[", "]]"],
  props: ["lab_name", "conn_name", "b64_conn_id", "card_id"],
  template: active_lab_management_template,
});

Vue.component("active-lab-header", {
  template: active_lab_dashboard_header,
});

/*
 * Helper functions
 */

function watch_lab_status(conn_name) {
  // Monitor the status of the lab and wait until it's ready to go

  const el = document.getElementById("conn_" + conn_name);
  const waiting_text = el.getElementsByClassName("waiting-text")[0];
  const open_button = el.getElementsByClassName("open-button")[0];

  let counter = 0;
  const check_status = window.setInterval(function() {
    waiting_text.innerHTML = "Lab starting" + ".".repeat(counter);
    counter = (counter + 1) % 4;

    // Check whether the lab is ready
    axios.get("/labs/pod/status?id=" + conn_name)
      .then(response => {
        const conditions = response.data.conditions;
        for ( let ii = 0; ii < conditions.length; ++ii ) {
          if ( conditions[ii].status !== "True" ) {
            return;
          }
        }
        // Ready. Remove the listener, the waiting text, and enable the
        // button to open the lab.
        waiting_text.innerHTML = "Ready";
        open_button.disabled = false;
        window.clearInterval(check_status);
      })
      .catch(error => {
        console.log("Error get status of " + conn_name + ": " + error);
        return false;
      });
  }, 1500);
}

function display_lab_manager() {
  axios.get("/labs/info")
    .then(response => {
      // Display a new lab card for every lab environment that the user is running
      const el = document.getElementById("active_lab_management");
      const n_active = response.data.length;
      console.log("User is running " + n_active + " labs");

      if ( n_active > 0 ) {
        const header = document.createElement("active-lab-header");
        el.parentNode.insertBefore(header, el);
      }

      let conns = [];
      for ( let ii = 0; ii < n_active; ++ii ) {
        const fields = response.data[ii];
        const lab_component = document.createElement("lab-component");
        const b64_conn_id =
        lab_component.setAttribute("card_id", "conn_" + fields.conn_name);
        lab_component.setAttribute("lab_name", fields.name);
        lab_component.setAttribute("conn_name", fields.conn_name);
        // TODO: something less hacky than this?
        lab_component.setAttribute("b64_conn_id", btoa(fields.conn_id + "\u0000c\u0000mysql"));
        el.appendChild(lab_component);
        conns.push(fields.conn_name);
      }

      new Vue({
        el: "#active_labs",
        mounted: function() {
          conns.forEach(conn => {
            watch_lab_status(conn);
          });
        }
      });

      //lab_starting_animation();
    })
    .catch(error => {
      // Can't do anything outside of printing an error
      console.log("Unable to read labs for user");
      console.log(error);
    });
}

/*
 * Script to run on page load
 */

document.addEventListener("DOMContentLoaded", function() {
  display_lab_manager();
}, false);
