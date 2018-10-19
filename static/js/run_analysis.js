// Socket msgs
var socket = io.connect(location.protocol + '//' + location.host);

socket.on('connect', function() {
  socket.emit('user_connect', {data: 'user connected'});
});

socket.on('feed-bloom-us', function(data) {
  console.log(data);
  $('#analysis2').text(data)
});

socket.on('feed-bloom-glob', function(data) {
  console.log(data);
  $('#analysis3').text(data)
});

socket.on('feed-sky', function(data) {
  console.log(data);
  $('#analysis1').text(data)
});

socket.on('feed-cnbc-africa', function(data) {
  console.log(data);
  $('#analysis4').text(data)
});

//////////////

var apiUrl = location.protocol + '//' + location.host + location.pathname + "api/";
var AjaxResponse = {};
$('#show_feeds').click(function() {
    $("#feeds").toggle();
  });

$('#downloadtoCSV').click(function() {
    JSONToCSV(AjaxResponse,true);
  });
//Hide Feeds
$("#feeds").hide();

$("#portfolio_file").change(function(e) {
 // The event listener for the file upload
    var ext = $("input#portfolio_file").val().split(".").pop().toLowerCase();
    $('.sandboxtwo').toggleClass('loading');
    $('.loader').addClass('active');
    if($.inArray(ext, ["csv"]) == -1) {
        alert('Upload CSV');
        window.location = window.location;
        return false;
    }   
    if (e.target.files != undefined) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var csvval=e.target.result.split("\n");
            var json_file = JSON.stringify(csvval);
            $.ajax({
                type: 'POST',
                url: apiUrl + 'upload',
                data: json_file,
                dataType: 'json',
                contentType: 'application/json',
                success: function(data) {
                    console.log(data);
                    alert("Portfolio uploaded successfully. You can now select it from the dropdown.");
                    window.location = window.location;
                }
            });
        };
    reader.readAsText(e.target.files.item(0));
    }  
    return false;
});

$("#news_stream_file").change(function() {
  console.log("uploading video file");
  
  var ext = $("input#news_stream_file").val().split(".").pop().toLowerCase();
  $('.sandboxtwo').toggleClass('loading');
  $('.loader').addClass('active');
  if($.inArray(ext, ["mp4"]) == -1) {
    alert('Upload MP4');
    window.location = window.location;
    return false;
  }

  var myfile = new FormData($('#video_form')[0]);
  var videofile = this.files[0];
  $.ajax({
      url: apiUrl + 'uploadvid',
      type: 'POST',
      success: function (res) {
          res = JSON.parse(res);
          var reader = new FileReader();
          reader.onload = function(file) {
            var fileContent = file.target.result;
            // original
            $('#success_video_container').append('<br><video src="' + fileContent + '" width="420" controls></video><br>');
            $('.sandboxtwo').removeClass('loading');
            $('.loader').removeClass('active');
          }
          reader.readAsDataURL(videofile);
      },
      data: myfile,
      cache: false,
      contentType: false,
      processData: false
  });
    return false;
});

//check user input and process, generate result in tables
$('.run-analysis.Button').click(function(){
    var Portfolio = $('.enter-portfolio select').find(":selected").text();
    var Portfolio = JSON.stringify(Portfolio);
    var selected = [];                
    $("input:checkbox[name=feeds]:checked").each(function() {
           selected.push($(this).val());
    });
    input_parameters = {};
    input_parameters["portfolio"] = Portfolio.replace(/"/g,"");
    input_parameters["feeds"] = selected;
    input_parameters = JSON.stringify(input_parameters);
    //verify input otherwise display an informative message
    if(Portfolio.includes('Loading...')) {
        alert("Load a portfolio first using Investment Portfolio service");
        return;
      } else if(Portfolio.includes('[pick portfolio]')) {
        alert("Select a portfolio");
        return;
      }
      $('#video_tbl').show();
			//need to make this based on which stream selected (currently only one choice).
      //do we make the streams mutually exclusive, or actually allow multiple. Probably multiple if the analysis can be parallelized...
      console.log(selected);
      if (selected.length == 0) {
        alert("Select at least one News channel to monitor");
        return;
      }
      if(selected.includes("https://www.bloomberg.com/live/us") > 0){
            $('#feed1').append('<br><div class="newsfeed_container"><iframe id="bloomberg-stream" height="320" src="https://www.bloomberg.com/live/us?width=560&height=315&autoPlay=true&mute=false" width="480" scrolling="no" style="margin-top: -50px;"></iframe></div>');
      }
      if(selected.includes("https://www.youtube.com/watch?v=XOacA3RYrXk") > 0){
            $('#feed2').append('<br><div class="newsfeed_container"><iframe width="480" height="270"  type="text/html" src="https://www.youtube.com/embed/XOacA3RYrXk?autoplay=1&fs=1&iv_load_policy=3&showinfo=0&rel=0&cc_load_policy=0&start=0&end=0&origin=https://youtubeembedcode.com&mute=1"></iframe></div>');
      }
      if(selected.includes("https://www.bloomberg.com/live") > 0){
            $('#feed3').append('<br><div class="newsfeed_container"><iframe id="bloomberg-stream" height="320"src="https://www.bloomberg.com/live?width=560&height=315&autoPlay=true&mute=false" width="480" scrolling="no" style="margin-top: -50px;"></iframe></div>');
      }
      if(selected.includes("https://www.youtube.com/watch?v=IpmKglKxQpA") > 0){
            $('#feed4').append('<br><div class="newsfeed_container"><iframe width="480" height="270" type="text/html" src="https://www.youtube.com/embed/IpmKglKxQpA?autoplay=1&fs=1&iv_load_policy=3&showinfo=0&rel=0&cc_load_policy=0&start=0&end=0&origin=https://youtubeembedcode.com&mute=1"></iframe></div>');
      }
      $('.sandboxtwo').toggleClass('loading');
      $('.loader').addClass('active');
      $.ajax({
        type: 'POST',
        url: apiUrl + 'news_anchor',
        data: input_parameters,
        dataType: 'json',
        contentType: 'application/json',
        error: function(xhr, err) {
          console.log(xhr);
          console.log(err);
        },
        success: function(res) {
          console.log(res.metadata);
          // clips
//          for (index in res.metadata) {
//            var clip = res.metadata[index];
//            $('#success_video_container').append(
//                '<br>' +
//                '<div class="clip-div">' +
//                  '<div style="padding: inherit">' +
//                    '<a href="/clips/'+clip.filename+'" download>' +
//                      '<Button class="clip-download-btn"><i class="fa fa-download"></i> Download clip </button>' +
//                    '</a>' +
//                  '</div>' +
//                  '<div style="padding: inherit">' +
//                    '<span class="clip-meta">Keywords:&nbsp'+clip.keyword+'</span>' +
//                    '<br>' +
//                    '<span class="clip-meta">Start Time:&nbsp'+clip.start+'</span>' +
//                    '<br>' +
//                    '<span class="clip-meta">End Time:&nbsp'+clip.end+'</span>' +
//                  '</div>' +
//                '</div>'
//            );
//          }
          $('.sandboxtwo').removeClass('loading');
          $('.loader').removeClass('active');
        }
    });
});

//create the output tables
function Process(data) {
    //process input into server to create output json
    //display today's date
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1;
    var yyyy = today.getFullYear();
    if(dd<10) {
        dd='0'+dd
    }
    if(mm<10) {
        mm='0'+mm
    }
    today = mm+'/'+dd+'/'+yyyy;
    $('.date a').text(today);

    //update header
    var holdings_title = 'Portfolio analytics results:';
    $('.title1 h3').text(holdings_title);
    th = '<tr style="width: 100%"><th>Name</th><th>ID</th><th>Quantity</th>'
    for (var key in data[0]){
        if(['name','quantity','id','portfolio','date'].includes(key) == false){
            th += "<th>" + AnalyticName(key) + "</th>";
        }
    }
    th += "</tr>"
    $('.port-table thead').html(th);

    //display holdings data
    var holdingsDataLength = data.length;
    var tr = "";
    for (var i = 0; i < holdingsDataLength; i++) {
        var name = data[i].name;
        var identifier = data[i].id;
        var quantity = data[i].quantity;
        //create row in table
        tr += "<tr tabindex='0' aria-label=" + name + "><td>" + name + "</td><td>" + identifier + "</td><td>" + quantity + "</td>";
        for (var key in data[i]){
            if(['name','quantity','id','portfolio','date'].includes(key) == false){
                tr += "<td>" + data[i][key] + "</td>";
            }
        }
        tr += "</tr>"
    }
    $('.port-table tbody').html(tr);
}

//sort the objects on key
function sortByKey(array, key) {
    return array.sort(function(a, b) {
        var x = a[key]; var y = b[key];
        return ((x > y) ? -1 : ((x < y) ? 1 : 0));
    });
}

//converts JSON to CSV for download
function JSONToCSV(JSONData) {
    var arrData = typeof JSONData != 'object' ? JSON.parse(JSONData) : JSONData;
    const header = Object.keys(arrData[0]);
    let csv = arrData.map(row => header.map(fieldName => JSON.stringify(row[fieldName], (key, value) => value === null ? '' : value)).join(','))
    
    csv.unshift(header.join(','))
    csv = csv.join('\r\n')
    
    var portfolioName = $("#portfolio_name :selected").text();
    var fileName = "PortfolioAnalytics_" + portfolioName.replace(/ /g,"_");
    var uri = 'data:text/csv;charset=utf-8,' + escape(csv);
    var link = document.createElement("a");
    
    link.href = uri;
    link.style = "visibility:hidden";
    link.download = fileName + ".csv";
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
