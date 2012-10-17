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



$('#test-btn').click(function(){
   alert("working");
    var username = $('#id_username').val();
    var password = $('#id_password').val();
    alert(username);
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
                alert("log in works");
            }
            else if(data==0){
                alert("log in failed");
            }
        }
    });

});

