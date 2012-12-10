function initialize() {
	map = new Microsoft.Maps.Map(document.getElementById("mapDiv"), {
		credentials:"AkL7bdBJmEpRncJpZ9MmXwEUIvnkId7Yo9IJrDhNFGrkR--08hfritan5JH_nzRw",
		center: new Microsoft.Maps.Location(37.7577,-122.4376),
		mapTypeId: Microsoft.Maps.MapTypeId.road,
		zoom: 4});
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

$(function () {
    $("#updateFavorite").click(function () {
        $("#updateFavForm").submit();
    });
});