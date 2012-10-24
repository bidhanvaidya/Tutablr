  var geocoder;
  var map;
  var markersArray = [];
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
        deleteOverlays();
         var address = document.getElementById("address").value;
        geocoder.geocode( { 'address': address}, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
                map.setCenter(results[0].geometry.location);
                addMarker(results[0].geometry.location);
/*        var marker = new google.maps.Marker({
            map: map,
            position: results[0].geometry.location,
            title: "Hello World"
        });  */
        /*
            marker['infowindow'] = new google.maps.InfoWindow({
            content: marker.position.lng().toString() + "  <> "+ marker.position.lat().toString()});*/
/*
            google.maps.event.addListener(marker, 'click', function() {
                this['infowindow'].open(map, this);
            });*/
            console.log(results[0]);
            var suburb;
            if (results[0].address_components.length == 3) {
                suburb = results[0].address_components[0].long_name;
                            console.log(results[0].address_components[0].long_name);
            }
            else {
                        suburb = results[0].address_components[1].long_name;
                            console.log(results[0].address_components[1].long_name);
            }
            $("#id_preferred_suburb").val(suburb);
            $("#id_longitude").val(results[0].geometry.location.Ya);
            $("#id_latitude").val(results[0].geometry.location.Xa);
      } 
      else {
        alert("An error occured. Please try again.");
      }
    });
  }

function addMarker(location) {
  marker = new google.maps.Marker({
    position: location,
    map: map
  });
  markersArray.push(marker);
}

// Removes the overlays from the map, but keeps them in the array
function clearOverlays() {
  if (markersArray) {
    for (i in markersArray) {
      markersArray[i].setMap(null);
    }
  }
}

// Shows any overlays currently in the array
function showOverlays() {
  if (markersArray) {
    for (i in markersArray) {
      markersArray[i].setMap(map);
    }
  }
}

// Deletes all markers in the array by removing references to them
function deleteOverlays() {
  if (markersArray) {
    for (i in markersArray) {
      markersArray[i].setMap(null);
    }
    markersArray.length = 0;
  }
}
  