  var geocoder;
  var map;
  var marker;
  var latitude;
  var longitude;
  var infowindow = new google.maps.InfoWindow();
  function initialize() {
        console.log("working")
    geocoder = new google.maps.Geocoder();
    var latlng = new google.maps.LatLng(-34.397, 150.644);
    var mapOptions = {
      zoom: 8,
      center: latlng,
      mapTypeId: google.maps.MapTypeId.ROADMAP
    }
    map = new google.maps.Map(document.getElementById("map_canvas"), mapOptions);
  }

  function codeAddress() {
    var address = document.getElementById("address").value;
    geocoder.geocode( { 'address': address}, function(results, status) {
      if (status == google.maps.GeocoderStatus.OK) {
        map.setCenter(results[0].geometry.location);
        var marker = new google.maps.Marker({
            map: map,
            position: results[0].geometry.location,
            title: "Hello World"
        }); 
            marker['infowindow'] = new google.maps.InfoWindow({
            content: marker.position.lng().toString() + "  <> "+ marker.position.lat().toString()
         });

            google.maps.event.addListener(marker, 'click', function() {
                this['infowindow'].open(map, this);
            });
            console.log(results);
            console.log(results[0].address_components[0].long_name);
      } 
      else {
        alert("Geocode was not successful for the following reason: " + status);
      }
    });
  }


  