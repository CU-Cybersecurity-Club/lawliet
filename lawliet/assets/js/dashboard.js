/* JavaScript for the site dashboard. */

/***************************************
 * Dashboard sidebar toggle
 ***************************************/
$("#sidebar-toggle").click(function(e) {
    e.preventDefault();
    $("#wrapper").toggleClass("toggled");
});

/***************************************
 * Text autosizing to fit in enclosing containers.
 ***************************************/
// Resize text in elements
function scale_font_by_factor(el, shrink_factor) {
     // Scale the font size of a CSS element by a provided factor
    const initial_font_size = parseInt(el.css("font-size"), 10);
    const scaled_font_size = initial_font_size * shrink_factor;
    el.css("font-size", scaled_font_size + "px");
}

function get_shrinkage_ratio(el, width) {
    /* 
     * Shrink the font size in an element until the element
     * reaches a desired width. Return the shrinking factor
     * (in the range of 0 to 1).
     */
    const initial_font_size = parseInt(el.css("font-size"), 10);
    let current_font_size = initial_font_size;

    for ( ; el.width() > width; --current_font_size ) {
        el.css("font-size", current_font_size + "px");
    }

    // Restore the element back to its original font size
    el.css("font-size", initial_font_size);

    let ratio = current_font_size / initial_font_size;
    return current_font_size / initial_font_size;
}

function autosize_text() {
    $(".resize-parent").each(function () {
        const rs_parent = $(this);
        const parent_width = rs_parent.width();
        let shrink_ratio = 1;

        // Get the shrink factor that will bring all of the text
        // to the appropriate width
        let shrink_factors = rs_parent.find(".resize-child").each(function () {
            const ratio = get_shrinkage_ratio($(this), parent_width);
            const font_size = parseInt($(this).css("font-size"), 10);
            scale_font_by_factor($(this), ratio);
            $(this).removeClass("resize-child");
        });
    });
}

/***************************************
 * Code to run when the page loads.
 ***************************************/
$(document).ready(function() {
    autosize_text();
});
