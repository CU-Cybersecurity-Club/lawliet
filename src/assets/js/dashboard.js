/* JavaScript for the site dashboard. */

axios.defaults.xsrfCookieName = "csrftoken";
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

/*
 * Vue components
 */

const active_lab_management_template = `
<ul class="uk-list">
  <li>
    <button type="button" class="uk-button uk-button-primary uk-width-1-3@m">
      Lab status
    </button>
  </li>
  <li>
    <button
      type="button"
      id="delete-button"
      class="uk-button uk-button-primary uk-width-1-3@m"
      v-on:click="delete_lab()">
      Delete lab
    </button>
  </li>
</ul>`;

/*
const active_lab_management_template = `
<div class="uk-container uk-width-1-2@m">
<div class="uk-card uk-card-body uk-card-secondary">
  <h3 class="uk-card-title">Current lab:</h3>
</div></div>`;
*/

Vue.component("active-lab-manager", {
  // props: [],
  template: active_lab_management_template,
});

/*
 * Helper functions
 */

function display_lab_manager() {
  axios.get("/user/info")
    .then(response => {
      console.log("Number of active labs: " + response.data.n_active_labs);
      if ( response.data.n_active_labs > 0 ) {
        // If n_active_labs > 0, display the lab manager
        new Vue({
          el: "#active_lab_management",
        });
      }
      else {
        // Otherwise, don't display anything
        console.log("User has no active labs");
      }
    })
    .catch(error => {
      // Can't do anything outside of printing an error
      console.log("Unable to read user information");
      console.log(error);
    });
}

/*
 * Script to run on page load
 */

display_lab_manager();
