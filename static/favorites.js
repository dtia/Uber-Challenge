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