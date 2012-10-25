$(document).ready(function() {
        var dialog_open = false;
      setInterval("refresh_check();",2000);
      
      function refresh_check(){
        
          $('#calendar').fullCalendar('refetchEvents');
          
      }
         $.getJSON("/calendar/events.json", function(json) {
          for (i = 0; i < json.length; i++) { 
            console.log(json[i].editable);
          json[i].selectable =  true;
          json[i].editable = false;
        }
          
        $('#calendar').fullCalendar({
         header : {
            left : 'prev,next today',
            center : 'title',
            right : 'month,agendaWeek,agendaDay'
          },
          defaultView : 'month',
          selectable : true,
          selectHelper : true,
          editable : true,
          disableResizing : true,
          aspectRatio : 1.75,
          allDaySlot:false,
          
          
          
         
          events : json,
         
        });
        
        });
        
      
      });