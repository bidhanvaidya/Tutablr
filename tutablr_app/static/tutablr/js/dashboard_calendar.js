$(document).ready(function() {
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
          defaultView : 'agendaDay',
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