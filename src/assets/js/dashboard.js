/* JavaScript for the site dashboard. */

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

/*
 * Vue components
 */

// Various buttons that allow you to manage an active lab environment
const active_lab_management_template = `
<div>
  <div class="uk-card uk-card-body uk-card-default uk-margin-bottom">
    <h3 class="uk-card-title">Active lab: [[ lab_name ]]</h3>
    <p class="monospace waiting-text uk-text-center">
      Lab starting...
    </p>
    <ul class="uk-list uk-margin-top">
      <li>
        <button
          type="button"
          class="uk-button uk-button-primary uk-width-1-1@m"
          disabled>
          Start lab
        </button>
      </li>
      <li>
        <button type="button" class="uk-button uk-button-primary uk-width-1-1@m">
          Lab status
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
  props: ["lab_name", "conn_name"],
  template: active_lab_management_template,
});

Vue.component("active-lab-header", {
  template: active_lab_dashboard_header,
});

/*
 * Helper functions
 */

function lab_starting_animation(lab_management_el) {
  let el = lab_management_el.getElementsByTagName("p")[0];
  console.log(el);

  // Display some text saying "Lab starting..." (with the ellipsis
  // animated) until the lab is ready to go.
  let ii = 0;
  window.setInterval(function () {
    el.innerHTML = "Lab starting" + ".".repeat(ii);
    ii = (ii + 1) % 4;
  }, 1500);
}

function display_lab_manager() {
  axios.get("/labs/info")
    .then(response => {
      // Display a new lab card for every lab environment that the user is running
      const el = document.getElementById("active_lab_management");
      const n_active = response.data.length;
      console.log("User is running " + n_active + " labs");
      console.log(response);

      if ( n_active > 0 ) {
        const header = document.createElement("active-lab-header");
        el.parentNode.insertBefore(header, el);
      }

      for ( let ii = 0; ii < n_active; ++ii ) {
        const fields = response.data[ii];
        const lab_component = document.createElement("lab-component");
        lab_component.setAttribute("lab_name", fields.name);
        lab_component.setAttribute("conn_name", fields.conn_name);
        el.appendChild(lab_component);
      }

      new Vue({
        el: "#active_labs",
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

display_lab_manager();
