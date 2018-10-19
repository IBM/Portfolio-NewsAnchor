var apiUrl = location.protocol + '//' + location.host + location.pathname + "api/";

//update interface with portfolios and risk factors
function updateText() {

    console.log("apiUrl: " + apiUrl)
    $('#video_tbl').hide();
    //update portfolio lists
    var portfolioLists;
    $.get(apiUrl + 'news_anchor_portfolios', function(data) {
        $('.enter-portfolio select').html(function() {
            if(data == "No portfolios found."){
                return "Please load a portfolio below.";
            }else{
            var str = '<option value="" disabled="" selected="">[pick portfolio]</option>';
            var parsed = JSON.parse(data)
            console.log("data in get portfolionames" + data);
            for (var i = 0; i < parsed.length; i++) {
                str = str + '<option>' + parsed[i] + '</option>';
            }
            portfolioLists = parsed;
            console.log("str: " + str)
            return str;
        }
        });
    });
}
