/* JavaScript for the site dashboard. */

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

/*
 * Vue components
 */

const active_lab_management_template = `
<div>
  <div class="uk-card uk-card-body uk-card-default uk-margin-bottom">
    <h3 class="uk-card-title">Active lab: [[ lab_name ]]</h3>
    <ul class="uk-list">
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

Vue.component("lab-component", {
  delimiters: ["[[", "]]"],
  props: ["lab_name", "conn_name"],
  template: active_lab_management_template,
});

/*
 * Helper functions
 */

function display_lab_manager() {
  axios.get("/labs/info")
    .then(response => {
      // Display a new lab card for every lab environment that the user is running
      const el = document.getElementById("active_lab_management");
      const n_active = response.data.length;
      console.log("User is running " + n_active + " labs");
      console.log(response);

      for ( let ii = 0; ii < n_active; ++ii ) {
        const fields = response.data[ii];
        const lab_component = document.createElement("lab-component");
        lab_component.setAttribute("lab_name", fields.name);
        lab_component.setAttribute("conn_name", fields.conn_name);
        console.log(lab_component);
        el.appendChild(lab_component);
      }

      new Vue({
        el: "#active_lab_management",
      });
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
