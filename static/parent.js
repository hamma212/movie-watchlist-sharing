// only searches have the following *_js classes, so jQuery only returns one element
var searchTypeElement = $(".search_options_js");

searchTypeElement.on('change', changeSearchPlaceholder);

function changeSearchPlaceholder() {
    // console.log(this.value);
    if (this.value == "media"){
        $(".searchbox_js").attr("placeholder", "Search for media...");
    }
    else {
        $(".searchbox_js").attr("placeholder", "Search for users...");
    }
}


var profileDropdownButton = $("#profile_dropdown_button");

profileDropdownButton.on('click', showProfileDropdown);
profileDropdownButton.on('mouseenter', function() {
    console.log(profileDropdownButton.css("border-color"))
    if (profileDropdownButton.css("border-color") == "rgb(24, 24, 24)"){ //black
        profileDropdownButton.css("border-color", "rgb(105, 105, 105)"); //gray

    }
});
profileDropdownButton.on('mouseleave', function() {
    if (profileDropdownButton.css("border-color") == "rgb(105, 105, 105)"){ //gray
        profileDropdownButton.css("border-color", "rgb(24, 24, 24)"); //black
    }
});



function showProfileDropdown() {
    $(".profile_dropdown_content").toggle();
    if (profileDropdownButton.css("border-color") == "rgb(105, 105, 105)"){ //gray
        profileDropdownButton.css("border-color", "rgb(255, 255, 255)"); //white
    }
    else {      //white
        profileDropdownButton.css("border-color", "rgb(105, 105, 105)"); //if on profile and click: gray
    }
    // console.log("buttton press");
}

// https://www.w3schools.com/howto/tryit.asp?filename=tryhow_css_js_dropdown
window.onclick = function(event) {
    // console.log(event.target);

    if (!event.target.matches('#profile_dropdown_button') && !event.target.matches('.profile_dropdown_content div, .profile_dropdown_content b') && $(".profile_dropdown_content").is(":visible")) {//white
            profileDropdownButton.css("border-color", "rgb(24, 24, 24)"); //if not on profile and click: black
            $(".profile_dropdown_content").hide()
        // console.log("window button press");
    }
}


// https://gist.github.com/edysegura/9984108
document.addEventListener('invalid', (function(){
    return function(e) {
      //prevent the browser from showing default error bubble / hint
      e.preventDefault();
      // optionally fire off some custom validation handler
      // myValidation();
    };
})(), true);
