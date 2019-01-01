$('#btn-submit').click(function(){
	var method = $("form").find("#method").val();
  var url = "../api/v1.0/video_editor/"+method; // the script where you handle the form input.
  var $formData = $("form").serializeArray();
	var assocArray = {};
  var videos = [];
	$.map($formData, function(o,i){
            var m = o['name'].match(/videos-\d/);
            if (m) {
               videos.push(o['value']);
            } else {
               assocArray[o['name']] = o['value'];
            }
        });
  if (assocArray['method'] === 'concat') {
    assocArray['videos'] = videos;
  } else if (assocArray['method'] === 'cut') {
    assocArray['video'] = videos[0];
  } else {
    assocArray['video_id'] = videos[0];
  }

  var jsonData = JSON.stringify(assocArray);
  $.ajax({
           type: "POST",
           url: url,
           data: jsonData, // serializes the form's elements.
           cache: false,
           processData: false, // Don't process the files
           dataType: "json",
           contentType : "application/json",
           success: function(data) {
	           alert(JSON.stringify(data));
             $("#message").html('<a href="'+data['uri']+'">'+data['uri']+'</a>');
	         },
	         error: function(xhr,status,error) {
	           alert(error);
	         }
  });
});
