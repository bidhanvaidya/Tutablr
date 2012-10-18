var baseURL = "http://127.0.0.1:8000";

function getUrlVar(key){
var result = new RegExp(key + "=([^&]*)", "i").exec(window.location.search); 
return result && result[1] || ""; 
}


$.ajaxSetup({ 
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                 if (cookie.substring(0, name.length + 1) == (name + '=')) {
                     cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                     break;
                 }
             }
         }
         return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     } 
});


$("#login-form").submit(function(){
    var redirectURL;
    if (getUrlVar("next")== "") {
        redirectURL = baseURL + "/dashboard";
    }
    else {
        redirectURL = baseURL + getUrlVar("next");
    }
    var username = $('#id_username').val();
    var password = $('#id_password').val();
    if (username == "" || password == "") {
        $("#login-input").addClass("control-group error")
        alert("Please enter a valid username and password.");
    }    
    $.ajax({
      url: '/login',
      type: 'POST',
      //dataType: 'xml/html/script/json/jsonp',
      data: {
        username:username,
        password:password
    },

        success: function(data) {
            if (data==1) {
                var pathname = window.location.pathname;
                //$("#login-div").load("{{TEMPLATE_DIRS}}base_logged_out.html");
                window.location.replace(redirectURL);
            }
            else if(data==0){
                alert("Username and Password do not match!");
            }
        }
    });  
    return false;
});

$('#logout-btn').click(function(){
    $.ajax({
      url: '/accounts/logout',
      type: 'GET',
        success: function(data) {
             window.location.replace(baseURL);
        }
    });

});


