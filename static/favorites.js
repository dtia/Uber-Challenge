var map = null;
function initialize() {
	map = new Microsoft.Maps.Map(document.getElementById("mapDiv"), {
		credentials:"AkL7bdBJmEpRncJpZ9MmXwEUIvnkId7Yo9IJrDhNFGrkR--08hfritan5JH_nzRw",
		center: new Microsoft.Maps.Location(37.7577,-122.4376),
		mapTypeId: Microsoft.Maps.MapTypeId.road,
		zoom: 6});
	
	//Create two layers, one for pushpins, the other for the infobox. This way the infobox will always be above the pushpins.
	infoboxLayer = new Microsoft.Maps.EntityCollection();
	map.entities.push(infoboxLayer);
	pinLayer = new Microsoft.Maps.EntityCollection();
	map.entities.push(pinLayer);
	
	pushpinFrameHTML = '<div id="infobox" class="infobox"><div id="infobox_content" class="infobox_content">{content}</div></div><div class="infobox_pointer"><img src="/static/pointer_shadow.png" /></div>';
	
	plotFavorites();
}

function plotFavorites() {
	$.get('/get_coords', function(resp) {
		if (resp['favorites']) {
			addMarkersOnMapForLocations(resp['favorites']);
		}
	});
}

function addMarkersOnMapForLocations(locations) {
	for(var i=0; i<locations.length; i++){
		if (i===0) {
			center = new Microsoft.Maps.Location(locations[i].lat, locations[i].lng);
			map.setView({ center:  center });
		}
		addMarkersOnMap(locations[i]);
	}
}

function addMarkersOnMap(location) {
	if(typeof location === 'undefined')
		return;
	
	var loc = new Microsoft.Maps.Location(location.lat, location.lng);
	var pushpin = new Microsoft.Maps.Pushpin(loc);
	
	// infobox content
	pushpin.title = location.name;
	pushpin.description = get_address(location.street, location.city, location.state, location.zip);
	
	// Create the infobox for the pushpin
    var pinInfobox = new Microsoft.Maps.Infobox(pushpin.getLocation(), {visible:false});
	infoboxLayer.push(pinInfobox);
	currentPinInfobox = pinInfobox;

	 // Add handler for the pushpin click event.
    Microsoft.Maps.Events.addHandler(pushpin, 'click', displayInfobox.bind(pinInfobox));

	// Hide infobox when anywhere on map is clicked
	Microsoft.Maps.Events.addHandler(map, 'click', function displayInfobox(e)
	{
		this.setOptions({ visible:false });
	}.bind(pinInfobox));
	
	map.entities.push(pushpin);
}

function get_address(street, city, state, zip) {
	return street + ' ' + city + ' ' + state + ' ' + zip;
}

function listFavorites() {
	$.get('/', function(data) {
		$('#page').html(data);
	});
	
	$('#listFav').addClass("active");
	$('#addFav').removeClass("active");
}

function addFavorites() {
	$.get('/add', function(data) {
		$('#page').html(data);
	});
	
	$('#addFav').addClass("active");
	$('#listFav').removeClass("active");
}

function deleteFavorite(id) {
	if(confirm('Are you sure you want to delete this favorite location?')) 
		window.location = '/delete/' + id;	
}

$(function () {
    $(".updateFavorite").click(function () {
        $(".updateFavForm").submit();
    });
});

function displayInfobox(e) {
	if (e.targetType == "pushpin") {
		
		currentPinInfobox.setOptions({visible: false});
		currentPinInfobox = this;
		
		var pin = e.target;
		var html = "<span class='infobox_title'>" + pin.title + "</span><br/>" + pin.description;
		
		this.setOptions({
			visible:!this.getVisible(),
			offset: new Microsoft.Maps.Point(-33,10),
			htmlContent: pushpinFrameHTML.replace('{content}',html)
		});
		
        this.setLocation(e.target.getLocation());

         //A buffer limit to use to specify the infobox must be away from the edges of the map.
         var buffer = 25;

         var infoboxOffset = currentPinInfobox.getOffset();
         var infoboxAnchor = currentPinInfobox.getAnchor();
         var infoboxLocation = map.tryLocationToPixel(e.target.getLocation(), Microsoft.Maps.PixelReference.control);

         var dx = infoboxLocation.x + infoboxOffset.x - infoboxAnchor.x;
         var dy = infoboxLocation.y - 25 - infoboxAnchor.y;

         if (dy < buffer) {    //Infobox overlaps with top of map.
             //Offset in opposite direction.
             dy *= -1;

             //add buffer from the top edge of the map.
             dy += buffer;
         } else {
             //If dy is greater than zero than it does not overlap.
             dy = 0;
         }

         if (dx < buffer) {    //Check to see if overlapping with left side of map.
             //Offset in opposite direction.
             dx *= -1;

             //add a buffer from the left edge of the map.
             dx += buffer;
         } else {              //Check to see if overlapping with right side of map.
             dx = map.getWidth() - infoboxLocation.x + infoboxAnchor.x - currentPinInfobox.getWidth();

             //If dx is greater than zero then it does not overlap.
             if (dx > buffer) {
                 dx = 0;
             } else {
                 //add a buffer from the right edge of the map.
                 dx -= buffer;
             }
         }

         //Adjust the map so infobox is in view
         if (dx != 0 || dy != 0) {
             map.setView({ centerOffset: new Microsoft.Maps.Point(dx, dy), center: map.getCenter() });
         }
     }
 }