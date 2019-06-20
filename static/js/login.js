/*!
 * Start Bootstrap - SB Admin v5.0.3 (https://startbootstrap.com/template-overviews/sb-admin)
 * Copyright 2013-2019 Start Bootstrap
 * Licensed under MIT (https://github.com/BlackrockDigital/startbootstrap-sb-admin/blob/master/LICENSE)
 */
///Function provides linkage to the UI elements that generate it.
//It will call the remove feed and pass in the sliced ID of the object so it can remove the appropriate entry in database
function OnClickDynamic (event){
	RemoveFeed(event.id.slice(11,event.id.length))
}
//Perform AJAX request, and stringify the results for sending with the request.
//On a successful return, remove the element from the page 
//On a fail, alert the user
function RemoveFeed(ID){
	Username = $("#Username").text()
	Link = $("#FeedValue-" + ID).text()
	if (CheckNull(Link) && CheckNull(Username) && CheckLink(Link) && CheckUsername(Username)){
	data = JSON.stringify({Username: Username, Link: Link})
	$.ajax({
	  method: "POST",
	  contentType: 'application/json',
	  url: "http://localhost:5000/RSS-Delete",
	  data: data,
	  success: function( response ) {
	  $("#Container-" + ID).remove()},
	  error: function( response ) {
	  alert(response.responseText)}
})}}
;
	
	
//Broadcast the login click to the login function
$("#Login").click(function() {
	Login();
});
//Broadcast the register click to the register event
$("#Register").click(function() {
	Register();
});

//Broadcast the save button click to the save function
$("#SaveButton").click(function() {
	Save();
});
//Broadcast the get feed click event to the function.
$("#GetFeedButton").click(function() {
	GetFeed();
});
  
  
//Perform an ajax request to the server, stringify data on the page and send this up to the server.
//On success replace the document with the returned template passed down.
//On fail, alert the user with the message.
function Register (){
	Username = $("#Username").val()
	Password = $("#Password").val()
	if (CheckNull(Password) && CheckNull(Username) && CheckPassword(Password) && CheckPasswordStrength(Password) && CheckUsername(Username)){
	data = JSON.stringify({Username: Username, Password: Password})
	$.ajax({
	  method: "POST",
	  contentType: 'application/json',
	  url: "http://localhost:5000/Register",
	  data: data,
	  success: function( response ) {
		console.log("Logging in")
		document.write(response)
		document.close()},
	  error: function( response ) {
	  alert(response.responseText)}
})};}

//Perform an ajax request to the server and stringify the data on the page and send this up to the server.
//On success replace the document with the returned template passed down.
//On fail, alert the user with the message.
function Login(){
	Username = $("#Username").val()
	Password = $("#Password").val()
	if (CheckNull(Password) && CheckNull(Username) && CheckPasswordStrength(Password) && CheckPassword(Password) && CheckUsername(Username))
		{
	
		data = JSON.stringify({Username: Username, Password: Password})
		$.ajax({
		  method: "POST",
		  contentType: 'application/json',
		  url: "http://localhost:5000/Login",
		  data: data,
		  success: function( response ) {
			console.log("Logging in")
			document.write(response)
			document.close()},
		  error: function( response ) {
		  alert(response.responseText)}
		})
};}
//Perform an ajax request after the user has clicked save. 
//Based on the response it will alert the user, either success or fail.
function Save(){
	Link = $("#FeedURL").val()
	Username = $("#Username").text()
	if (CheckNull(Link) && CheckNull(Username) && CheckLink(Link) && CheckUsername(Username)){
	data = JSON.stringify({Username: Username, Link: Link})
	$.ajax({
	  method: "POST",
	  contentType: 'application/json',
	  url: "http://localhost:5000/RSS-Save",
	  data: data,
	  success: function( response ) {
			alert(response)
	  },
	  error: function( response ) {
			alert(response.responseText)
}
	  
	});
};}

//Perform an ajax request to get the feed back from the server.
//On a success, the body element searchfeedbody will be replaced with the XML from the response.
//Otherwise inform the user.
function GetFeed(){
	Link = $("#FeedURL").val()
	if (CheckNull(Link) && CheckLink(Link)){
	data = JSON.stringify({Link: Link})
	$.ajax({
	  method: "POST",
	  contentType: 'application/json',
	  url: "http://localhost:5000/RSS-One",
	  data: data,
	  success: function( response ) {
			$("#SearchFeedBody").html(response)
},
error: function( response ) {
			alert(response.responseText)
}
})}};


//Input validation - Client side

//Valid password for strength
function CheckPasswordStrength(Value){
	if (Value.length < 6) {
		alert('Your Password needs to be at least 6 characters long')
		return false
	}	
	else if (/^[0-9]*$/.test(Value) == true){
		alert('Your Password cannot be just numbers')
		return false
	}	
	else if (/^[a-z]*$/.test(Value) == true){
		alert('Your Password cannot just be letters')
		return false
	}	
	else if (/^[A-Z]*$/.test(Value) == true){
		alert('Your Password cannot just be capital letters')
		return false
	}	
	else if (/^[0-9a-z]*$/.test(Value) == true){
		alert('Your Password cannot just be numbers and letters')
		return false
	}
	else if (/^[0-9A-Z]*$/.test(Value) == true){
		alert('Your Password cannot just be numbers and capitals')
		return false
	}	
	else if (/^[a-zA-Z]*$/.test(Value) == true){
		alert('Your Password cannot just be letters')
		return false
	}	
	else if (/^[,.@;:[}}{|!£$%^&*()-]*$/.test(Value) == true){
		alert('Your Password cannot just be symbols')
		return false
	}
	else if (/^[a-z,.@;:[}}{|!£$%^&*()-]*$/.test(Value) == true){
		alert('Your Password cannot just be symbols and letters')
		return false
	}
	else if (/^[A-Z,.@;:[}}{|!£$%^&*()-]*$/.test(Value) == true){
		alert('Your Password cannot just be capital letters and symbols')
		return false
	}
	else if (/^[A-Za-z,.@;:[}}{|!£$%^&*()-]*$/.test(Value) == true){
		alert('Your Password cannot just be capital letters, letters and symbols')
		return false
	}
	else if (/^[a-z0-9,.@;:[}}{|!£$%^&*()-]*$/.test(Value) == true){
		alert('Your password cannot just be letters, numbers and symbols')
		return false
	}
	else if (/^[A-Z0-9,.@;:[}}{|!£$%^&*()-]*$/.test(Value) == true){
		alert('Your Password cannot just be capital letters, numbers and symbols')
		return false
	}
	else{
		return true
	}
	}
//Valid input for any XSS or SQL injection
function CheckUsername(Value){
	if(/^[a-zA-Z0-9]*$/.test(Value) == false) {
    alert('Your username cannot have complex characters, such as quotation marks.');
	return false
}
return true
}

function CheckPassword(Value){
	if(/^[a-z0-9A-Z,.@;:[}}{|!£$%^&*()-_]*$/.test(Value) == false) {
    alert('Your password cannot contain invalid characters, such as quotation marks');
	return false
}
return true
}

function CheckLink(Value){
	if(/^[a-zA-Z0-9:/.]*$/.test(Value) == false) {
    alert('Your html link needs to be valid');
	return false
}
return true
}


//Check for null
function CheckNull(Value){
	if (Value.length == 0){
		alert("You can't have an empty field")
		return false
	}
	return true
}

